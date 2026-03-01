import pytest
import sys
import os
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Danh sách các server - CHẠY RIÊNG BIỆT
SERVERS = [
    r"D:\git\MCP\mcp_client\mcp1.py",
    r"D:\git\MCP\mcp_client\mcp2.py"
]

EXPECTED_TOOLS = [
    "get_customer_info",
    "get_order_details",
    "check_inventory",
    "get_customer_ids_by_name",
    "get_orders_by_customer_id",
]

@pytest.mark.asyncio
@pytest.mark.parametrize("server_script", SERVERS) # Test từng file một
async def test_mcp_server_connection(server_script):
    """Connect to an MCP server and verify the tools"""

    exit_stack = AsyncExitStack()

    # Thiết lập PYTHONPATH để server tìm thấy file transactional_db.py ở thư mục gốc
    env = os.environ.copy()
    env["PYTHONPATH"] = r"D:\git\MCP" 

    # CẤU HÌNH ĐÚNG: args chỉ chứa 1 file script tại một thời điểm
    server_params = StdioServerParameters(
        command=sys.executable, 
        args=[server_script], 
        env=env
    )

    try:
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport
        session = await exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )

        await session.initialize()

        response = await session.list_tools()
        tool_names = [tool.name for tool in response.tools]
        
        print(f"\nTesting server: {server_script}")
        print(f"Tools found: {tool_names}")

        # Kiểm tra xem các tool mong muốn có tồn tại không
        for tool in EXPECTED_TOOLS:
            assert tool in tool_names, f"Tool {tool} not found in {server_script}"

    finally:
        await exit_stack.aclose()
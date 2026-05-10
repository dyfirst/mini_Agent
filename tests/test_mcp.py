"""测试 MCP 功能"""
import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

from src.agent.mcp import MCPClient, MCPToolAdapter


async def test_mcp_client():
    """测试 MCP Client 基本功能"""
    print("=== 测试 MCP Client ===\n")

    # 1. 创建客户端
    client = MCPClient()
    print("[OK] MCPClient 创建成功")

    # 2. 检查初始状态
    assert len(client.tools) == 0
    assert len(client.servers) == 0
    print("[OK] 初始状态正确（无工具、无服务器）")

    # 3. 检查工具定义格式
    definitions = client.get_tool_definitions()
    assert definitions == []
    print("[OK] get_tool_definitions() 返回空列表")

    # 4. 检查列表功能
    tools_list = client.list_tools()
    assert tools_list == []
    print("[OK] list_tools() 返回空列表")

    # 5. 测试调用不存在的工具
    result = await client.call_tool("nonexistent", {})
    assert "not found" in result.lower()
    print("[OK] 调用不存在的工具返回错误信息")

    print("\n[OK] 所有 MCP Client 测试通过!\n")


async def test_mcp_adapter():
    """测试 MCP Tool Adapter"""
    print("=== 测试 MCP Tool Adapter ===\n")

    client = MCPClient()

    # 1. 创建适配器
    adapter = MCPToolAdapter(
        tool_name="test_tool",
        tool_description="A test tool",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query string"}
            },
            "required": ["query"]
        },
        mcp_client=client,
    )
    print("[OK] MCPToolAdapter 创建成功")

    # 2. 检查工具定义
    definition = adapter.get_definition()
    assert definition["type"] == "function"
    assert definition["function"]["name"] == "test_tool"
    assert "query" in definition["function"]["parameters"]["properties"]
    print("[OK] 工具定义格式正确")

    # 3. 测试执行（会失败，因为没有服务器）
    result = await adapter.execute(query="test")
    assert "not found" in result.lower() or "error" in result.lower()
    print("[OK] 执行未连接的工具返回错误")

    print("\n[OK] 所有 MCP Adapter 测试通过!\n")


async def test_mcp_config():
    """测试 MCP 配置文件"""
    print("=== 测试 MCP 配置文件 ===\n")

    config_path = "mcp_config.json"

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        print(f"[OK] 配置文件存在，包含 {len(servers)} 个服务器配置")

        for name, server_config in servers.items():
            command = server_config.get("command", "")
            args = server_config.get("args", [])
            print(f"  - {name}: {command} {' '.join(args)}")
    else:
        print("[SKIP] 配置文件不存在，跳过测试")

    print()


async def main():
    print("=" * 50)
    print("MCP 功能测试")
    print("=" * 50 + "\n")

    await test_mcp_client()
    await test_mcp_adapter()
    await test_mcp_config()

    print("=" * 50)
    print("所有测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

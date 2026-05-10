"""测试 MCP 功能"""
import pytest
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

from src.agent.mcp import MCPClient, MCPToolAdapter


@pytest.mark.asyncio
async def test_mcp_client():
    """测试 MCP Client 基本功能"""
    # 创建客户端
    client = MCPClient()
    assert len(client.tools) == 0
    assert len(client.servers) == 0

    # 检查工具定义格式
    definitions = client.get_tool_definitions()
    assert definitions == []

    # 检查列表功能
    tools_list = client.list_tools()
    assert tools_list == []

    # 测试调用不存在的工具
    result = await client.call_tool("nonexistent", {})
    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_mcp_adapter():
    """测试 MCP Tool Adapter"""
    client = MCPClient()

    # 创建适配器
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

    # 检查工具定义
    definition = adapter.get_definition()
    assert definition["type"] == "function"
    assert definition["function"]["name"] == "test_tool"
    assert "query" in definition["function"]["parameters"]["properties"]

    # 测试执行（会失败，因为没有服务器）
    result = await adapter.execute(query="test")
    assert "not found" in result.lower() or "error" in result.lower()


def test_mcp_config():
    """测试 MCP 配置文件"""
    config_path = "mcp_config.json"

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        assert len(servers) > 0

        for name, server_config in servers.items():
            assert "command" in server_config
            assert "args" in server_config

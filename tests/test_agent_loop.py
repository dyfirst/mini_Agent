"""测试完整 Agent Loop"""
import asyncio
import os
import sys
import pytest
from src.agent.agent_loop import AgentLoop
from src.agent.providers.openai import OpenAIProvider
from src.agent.tools import ToolRegistry, ReadFileTool, ListDirectoryTool, ShellTool

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')


@pytest.mark.asyncio
async def test_basic_agent():
    """测试基本 Agent 功能"""
    # 检查 API Key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY 未设置")

    # 创建 Provider
    provider = OpenAIProvider(api_key=api_key, model="gpt-3.5-turbo")

    # 创建 Agent
    agent = AgentLoop(
        provider=provider,
        system_prompt="You are a helpful assistant. Keep responses concise.",
    )

    # 测试简单对话
    response = await agent.run("What is 2+2?")
    print(f"问题: What is 2+2?")
    print(f"回答: {response}")

    assert "4" in response

    print("[OK] 基本 Agent 测试通过")


@pytest.mark.asyncio
async def test_agent_with_tools():
    """测试带工具的 Agent"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY 未设置")

    # 创建 Provider
    provider = OpenAIProvider(api_key=api_key, model="gpt-3.5-turbo")

    # 创建工具
    tools = ToolRegistry()
    tools.register("list_directory", ListDirectoryTool())
    tools.register("read_file", ReadFileTool())
    tools.register("shell", ShellTool())

    # 创建 Agent
    agent = AgentLoop(
        provider=provider,
        tools=tools,
        system_prompt="You are a helpful assistant with access to file tools. Use them when appropriate.",
    )

    # 测试工具调用
    response = await agent.run("List files in the current directory")
    print(f"问题: List files in the current directory")
    print(f"回答:\n{response}")

    assert "src" in response or "tests" in response

    print("[OK] Agent 工具调用测试通过")


if __name__ == "__main__":
    asyncio.run(test_basic_agent())
    asyncio.run(test_agent_with_tools())
    print("\n[OK] 所有 Agent Loop 测试完成")

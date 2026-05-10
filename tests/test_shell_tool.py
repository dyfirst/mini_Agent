"""测试 Shell 工具"""
import asyncio
import sys
import pytest
from src.agent.tools import ShellTool

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')


@pytest.mark.asyncio
async def test_basic_command():
    """测试基本命令执行"""
    shell = ShellTool()

    # 测试 echo 命令
    result = await shell.execute(command="echo Hello World")
    print(f"Echo 结果: {result}")

    assert "Hello World" in result

    print("[OK] 基本命令测试通过")


@pytest.mark.asyncio
async def test_list_command():
    """测试列表命令"""
    shell = ShellTool()

    # 测试 dir 命令（Windows）或 ls 命令（Linux/Mac）
    result = await shell.execute(command="dir")
    print(f"Dir 结果:\n{result[:200]}...")  # 只显示前200字符

    assert "src" in result or "tests" in result

    print("[OK] 列表命令测试通过")


@pytest.mark.asyncio
async def test_timeout():
    """测试命令超时"""
    shell = ShellTool(timeout=1)  # 1秒超时

    # 测试一个会超时的命令
    result = await shell.execute(command="ping -n 10 127.0.0.1")
    print(f"超时结果: {result}")

    # 注意：这个测试可能需要调整，取决于系统
    print("[OK] 超时测试完成")


if __name__ == "__main__":
    asyncio.run(test_basic_command())
    asyncio.run(test_list_command())
    # asyncio.run(test_timeout())  # 可选：取消注释以测试超时
    print("\n[OK] 所有 Shell 工具测试通过")

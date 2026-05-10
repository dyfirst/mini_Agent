"""测试文件操作工具"""
import asyncio
import os
import sys
from src.agent.tools import ReadFileTool, WriteFileTool, ListDirectoryTool

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')


async def test_write_and_read():
    """测试写入和读取文件"""
    write_tool = WriteFileTool()
    read_tool = ReadFileTool()

    test_file = "test_output.txt"
    test_content = "Hello, this is a test file!"

    # 写入文件
    result = await write_tool.execute(path=test_file, content=test_content)
    print(f"写入结果: {result}")

    # 读取文件
    content = await read_tool.execute(path=test_file)
    print(f"读取内容: {content}")

    # 验证
    assert content == test_content

    # 清理
    os.remove(test_file)

    print("[OK] 文件写入/读取测试通过")


async def test_list_directory():
    """测试列出目录"""
    list_tool = ListDirectoryTool()

    result = await list_tool.execute(path=".")
    print(f"目录内容:\n{result}")

    assert "src" in result
    assert "tests" in result

    print("[OK] 目录列出测试通过")


async def test_read_nonexistent():
    """测试读取不存在的文件"""
    read_tool = ReadFileTool()

    result = await read_tool.execute(path="nonexistent.txt")
    print(f"错误信息: {result}")

    assert "Error" in result or "not found" in result

    print("[OK] 读取不存在文件测试通过")


if __name__ == "__main__":
    asyncio.run(test_write_and_read())
    asyncio.run(test_list_directory())
    asyncio.run(test_read_nonexistent())
    print("\n[OK] 所有文件工具测试通过")

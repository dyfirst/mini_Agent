"""测试 ToolRegistry 类"""
from src.agent.tools import ToolRegistry, ReadFileTool, WriteFileTool


def test_register_tools():
    """测试工具注册"""
    registry = ToolRegistry()

    # 注册工具
    registry.register("read_file", ReadFileTool())
    registry.register("write_file", WriteFileTool())

    print(f"已注册工具: {registry.tool_names}")
    print(f"工具数量: {len(registry)}")

    assert "read_file" in registry
    assert "write_file" in registry
    assert len(registry) == 2

    print("✅ 工具注册测试通过")


def test_get_definitions():
    """测试获取工具定义"""
    registry = ToolRegistry()
    registry.register("read_file", ReadFileTool())

    definitions = registry.get_tool_definitions()

    print(f"工具定义数量: {len(definitions)}")
    print(f"工具名称: {definitions[0]['function']['name']}")

    assert len(definitions) == 1
    assert definitions[0]["function"]["name"] == "read_file"

    print("✅ 工具定义测试通过")


if __name__ == "__main__":
    test_register_tools()
    test_get_definitions()
    print("\n✅ 所有 ToolRegistry 测试通过")

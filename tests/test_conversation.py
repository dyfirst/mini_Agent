"""测试 Conversation 类"""
from src.agent.conversation import Conversation, Message


def test_basic_conversation():
    """测试基本会话功能"""
    # 创建会话
    conv = Conversation(system_prompt="You are a helpful assistant")

    # 添加消息
    conv.add_user_message("Hello")
    conv.add_assistant_message("Hi there!")
    conv.add_tool_result("tool_123", "Tool result")

    # 验证消息
    messages = conv.get_messages_for_api()

    print(f"消息数量: {len(messages)}")
    print(f"消息类型: {[m['role'] for m in messages]}")

    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "tool"

    print("✅ 基本会话测试通过")


def test_clear_conversation():
    """测试清空会话"""
    conv = Conversation(system_prompt="System prompt")
    conv.add_user_message("Hello")
    conv.add_assistant_message("Hi")

    conv.clear()

    messages = conv.get_messages_for_api()
    assert len(messages) == 1
    assert messages[0]["role"] == "system"

    print("✅ 清空会话测试通过")


if __name__ == "__main__":
    test_basic_conversation()
    test_clear_conversation()
    print("\n✅ 所有 Conversation 测试通过")

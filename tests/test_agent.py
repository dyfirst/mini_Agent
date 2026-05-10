"""Tests for Agent Loop"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.agent.conversation import Conversation, Message
from src.agent.providers.base import LLMResponse, ToolCall
from src.agent.tools import ToolRegistry, ReadFileTool


class TestConversation:
    """Tests for Conversation class"""

    def test_add_messages(self):
        """Test adding different types of messages"""
        conv = Conversation(system_prompt="You are a test assistant")

        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi there!")
        conv.add_tool_result("tool_123", "Tool result")

        messages = conv.get_messages_for_api()

        assert len(messages) == 4  # system + user + assistant + tool
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"
        assert messages[3]["role"] == "tool"
        assert messages[3]["tool_call_id"] == "tool_123"

    def test_clear_conversation(self):
        """Test clearing conversation while keeping system prompt"""
        conv = Conversation(system_prompt="System prompt")
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi")

        conv.clear()

        messages = conv.get_messages_for_api()
        assert len(messages) == 1
        assert messages[0]["role"] == "system"


class TestToolRegistry:
    """Tests for ToolRegistry"""

    def test_register_tool(self):
        """Test registering a tool"""
        registry = ToolRegistry()
        tool = ReadFileTool()

        registry.register("read_file", tool)

        assert "read_file" in registry
        assert registry.get_tool("read_file") == tool

    def test_get_tool_definitions(self):
        """Test getting tool definitions"""
        registry = ToolRegistry()
        registry.register("read_file", ReadFileTool())

        definitions = registry.get_tool_definitions()

        assert len(definitions) == 1
        assert definitions[0]["function"]["name"] == "read_file"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

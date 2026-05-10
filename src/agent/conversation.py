"""Conversation management for Agent"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Message:
    """Represents a single message in the conversation"""

    role: str  # "system", "user", "assistant", "tool"
    content: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format for API"""
        msg = {"role": self.role}

        if self.content is not None:
            msg["content"] = self.content

        if self.tool_call_id is not None:
            msg["tool_call_id"] = self.tool_call_id

        if self.tool_calls is not None:
            msg["tool_calls"] = self.tool_calls

        return msg


class Conversation:
    """Manages conversation history"""

    def __init__(self, system_prompt: Optional[str] = None):
        self.messages: List[Message] = []

        if system_prompt:
            self.add_system_message(system_prompt)

    def add_system_message(self, content: str):
        """Add system message"""
        self.messages.append(Message(role="system", content=content))

    def add_user_message(self, content: str):
        """Add user message"""
        self.messages.append(Message(role="user", content=content))

    def add_assistant_message(
        self,
        content: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
    ):
        """Add assistant message"""
        self.messages.append(
            Message(role="assistant", content=content, tool_calls=tool_calls)
        )

    def add_tool_result(self, tool_call_id: str, content: str):
        """Add tool execution result"""
        self.messages.append(
            Message(role="tool", content=content, tool_call_id=tool_call_id)
        )

    def get_messages_for_api(self) -> List[Dict[str, Any]]:
        """Get all messages in API format"""
        return [msg.to_dict() for msg in self.messages]

    def clear(self):
        """Clear conversation history"""
        system_messages = [m for m in self.messages if m.role == "system"]
        self.messages = system_messages

    @property
    def last_message(self) -> Optional[Message]:
        """Get the last message"""
        return self.messages[-1] if self.messages else None

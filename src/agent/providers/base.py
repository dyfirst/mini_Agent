"""Base class for LLM Providers"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ToolCall:
    """Represents a tool call from LLM"""

    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Response from LLM provider"""

    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

    @property
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls"""
        return self.tool_calls is not None and len(self.tool_calls) > 0


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Send chat request to LLM

        Args:
            messages: Conversation messages
            tools: Tool definitions for function calling

        Returns:
            LLMResponse with content or tool calls
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """Stream chat response from LLM

        Args:
            messages: Conversation messages
            tools: Tool definitions for function calling

        Yields:
            Chunks of response
        """
        pass

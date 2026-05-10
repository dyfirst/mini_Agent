"""Anthropic Provider implementation"""

import json
from typing import List, Dict, Any, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

from .base import LLMProvider, LLMResponse, ToolCall


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
    ):
        if anthropic is None:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )

        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Send chat request to Anthropic API"""
        # Extract system message if present
        system_message = None
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append(msg)

        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": chat_messages,
        }

        if system_message:
            kwargs["system"] = system_message

        if tools:
            # Convert OpenAI tool format to Anthropic format
            anthropic_tools = []
            for tool in tools:
                func = tool["function"]
                anthropic_tools.append({
                    "name": func["name"],
                    "description": func["description"],
                    "input_schema": func["parameters"],
                })
            kwargs["tools"] = anthropic_tools

        response = await self.client.messages.create(**kwargs)

        # Parse response
        content = None
        tool_calls = None

        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )

        return LLMResponse(content=content, tool_calls=tool_calls)

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """Stream chat response from Anthropic API"""
        # Extract system message if present
        system_message = None
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append(msg)

        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": chat_messages,
        }

        if system_message:
            kwargs["system"] = system_message

        if tools:
            anthropic_tools = []
            for tool in tools:
                func = tool["function"]
                anthropic_tools.append({
                    "name": func["name"],
                    "description": func["description"],
                    "input_schema": func["parameters"],
                })
            kwargs["tools"] = anthropic_tools

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

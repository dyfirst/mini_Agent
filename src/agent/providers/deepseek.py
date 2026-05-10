"""DeepSeek Provider implementation"""

import json
from typing import List, Dict, Any, Optional

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from .base import LLMProvider, LLMResponse, ToolCall


class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider (OpenAI-compatible)"""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
    ):
        if AsyncOpenAI is None:
            raise ImportError(
                "openai package not installed. Run: pip install openai"
            )

        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Send chat request to DeepSeek API"""
        kwargs = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools

        response = await self.client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        message = choice.message

        # Parse tool calls if present
        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        return LLMResponse(content=message.content, tool_calls=tool_calls)

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """Stream chat response from DeepSeek API"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        if tools:
            kwargs["tools"] = tools

        stream = await self.client.chat.completions.create(**kwargs)

        async for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content

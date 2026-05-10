"""Agent Loop - Core logic for AI Agent"""

from typing import Optional, List, Dict, Any

from .conversation import Conversation
from .providers.base import LLMProvider, LLMResponse
from .tools.registry import ToolRegistry


class AgentLoop:
    """Main Agent Loop that orchestrates conversation and tool execution"""

    def __init__(
        self,
        provider: LLMProvider,
        tools: Optional[ToolRegistry] = None,
        system_prompt: Optional[str] = None,
        max_iterations: int = 10,
    ):
        """Initialize Agent Loop

        Args:
            provider: LLM provider for generating responses
            tools: Tool registry for available tools
            system_prompt: Optional system prompt
            max_iterations: Maximum tool call iterations before stopping
        """
        self.provider = provider
        self.tools = tools or ToolRegistry()
        self.conversation = Conversation(system_prompt=system_prompt)
        self.max_iterations = max_iterations

    async def run(self, user_input: str) -> str:
        """Process user input and generate response

        Args:
            user_input: User's input message

        Returns:
            Final response from the agent
        """
        # Add user message to conversation
        self.conversation.add_user_message(user_input)

        # Agent loop
        iterations = 0
        while iterations < self.max_iterations:
            iterations += 1

            # Get response from LLM
            response = await self._get_llm_response()

            # Check if there are tool calls
            if response.has_tool_calls:
                # Process tool calls
                await self._process_tool_calls(response)
                # Continue loop to get next response
                continue

            # No tool calls, return final response
            if response.content:
                self.conversation.add_assistant_message(content=response.content)
                return response.content
            else:
                return "No response generated."

        # Max iterations reached
        return "Maximum iterations reached. Stopping."

    async def _get_llm_response(self) -> LLMResponse:
        """Get response from LLM provider

        Returns:
            LLMResponse from provider
        """
        messages = self.conversation.get_messages_for_api()
        tools = self.tools.get_tool_definitions() if self.tools else None

        return await self.provider.chat(messages=messages, tools=tools)

    async def _process_tool_calls(self, response: LLMResponse):
        """Process tool calls from LLM response

        Args:
            response: LLM response containing tool calls
        """
        import json

        # Add assistant message with tool calls
        tool_calls_data = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": json.dumps(tc.arguments, ensure_ascii=False),
                },
            }
            for tc in response.tool_calls
        ]
        self.conversation.add_assistant_message(tool_calls=tool_calls_data)

        # Execute each tool call
        for tool_call in response.tool_calls:
            result = await self.tools.execute(
                name=tool_call.name,
                arguments=tool_call.arguments,
            )

            # Add tool result to conversation
            self.conversation.add_tool_result(
                tool_call_id=tool_call.id,
                content=result,
            )

    def clear_conversation(self):
        """Clear conversation history (except system prompt)"""
        self.conversation.clear()

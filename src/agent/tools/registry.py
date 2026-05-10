"""Tool Registry for managing available tools"""

from typing import Dict, List, Any, Optional

from .base import Tool


class ToolRegistry:
    """Registry for managing and discovering tools"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, name: str, tool: Tool):
        """Register a tool

        Args:
            name: Tool name
            tool: Tool instance
        """
        self._tools[name] = tool

    def unregister(self, name: str):
        """Unregister a tool

        Args:
            name: Tool name to remove
        """
        if name in self._tools:
            del self._tools[name]

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name

        Args:
            name: Tool name

        Returns:
            Tool instance or None
        """
        return self._tools.get(name)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all tool definitions for LLM

        Returns:
            List of tool definitions in OpenAI format
        """
        definitions = []
        for name, tool in self._tools.items():
            definitions.append(tool.get_definition())
        return definitions

    async def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool by name

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        tool = self._tools.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found"

        try:
            if not tool.validate_arguments(arguments):
                return f"Error: Invalid arguments for tool '{name}'"

            result = await tool.execute(**arguments)
            return result
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    @property
    def tool_names(self) -> List[str]:
        """Get list of registered tool names"""
        return list(self._tools.keys())

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

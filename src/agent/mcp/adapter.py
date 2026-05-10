"""MCP Tool Adapter - bridges MCP tools with the internal Tool system"""

from typing import Dict, Any

from ..tools.base import Tool
from .client import MCPClient


class MCPToolAdapter(Tool):
    """Adapter that wraps an MCP tool as an internal Tool"""

    def __init__(self, tool_name: str, tool_description: str, input_schema: Dict[str, Any], mcp_client: MCPClient):
        """Initialize MCP tool adapter

        Args:
            tool_name: MCP tool name
            tool_description: Tool description
            input_schema: JSON Schema for input
            mcp_client: MCP client instance
        """
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.input_schema = input_schema
        self.mcp_client = mcp_client

    def get_definition(self) -> Dict[str, Any]:
        """Get tool definition in OpenAI format"""
        return {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.tool_description,
                "parameters": self.input_schema,
            },
        }

    async def execute(self, **kwargs) -> str:
        """Execute the MCP tool"""
        return await self.mcp_client.call_tool(self.tool_name, kwargs)

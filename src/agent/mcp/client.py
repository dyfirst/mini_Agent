"""MCP (Model Context Protocol) Client implementation"""

import asyncio
import json
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class MCPTool:
    """Represents a tool from MCP server"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


class MCPServer:
    """Represents an MCP server connection"""

    def __init__(self, name: str, command: str, args: List[str] = None, env: Dict[str, str] = None):
        """Initialize MCP server

        Args:
            name: Server name
            command: Command to start the server
            args: Command arguments
            env: Environment variables
        """
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.process: Optional[subprocess.Popen] = None
        self.tools: Dict[str, MCPTool] = {}
        self._request_id = 0

    async def start(self):
        """Start the MCP server process"""
        try:
            cmd = [self.command] + self.args

            # Merge environment variables
            import os
            merged_env = {**os.environ, **self.env}

            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=merged_env,
            )

            # Wait a bit for the server to start
            await asyncio.sleep(2)

            # Initialize connection
            await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "my-agent",
                    "version": "0.4.0",
                },
            })

            # Send initialized notification
            await self._send_notification("initialized", {})

            # List available tools
            await self._refresh_tools()

            return True

        except Exception as e:
            print(f"Failed to start MCP server '{self.name}': {e}")
            return False

    async def stop(self):
        """Stop the MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except:
                self.process.kill()

    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send JSON-RPC request to server

        Args:
            method: Method name
            params: Method parameters

        Returns:
            Response from server
        """
        self._request_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
        }

        if params:
            request["params"] = params

        # Send request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()

        # Read response
        response_str = await asyncio.wait_for(
            self.process.stdout.readline(),
            timeout=30.0,
        )

        response = json.loads(response_str.decode())

        if "error" in response:
            raise Exception(f"MCP error: {response['error']}")

        return response.get("result", {})

    async def _send_notification(self, method: str, params: Dict[str, Any] = None):
        """Send JSON-RPC notification (no response expected)

        Args:
            method: Method name
            params: Method parameters
        """
        notification = {
            "jsonrpc": "2.0",
            "method": method,
        }

        if params:
            notification["params"] = params

        # Send notification
        notification_str = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_str.encode())
        await self.process.stdin.drain()

    async def _refresh_tools(self):
        """Refresh available tools from server"""
        result = await self._send_request("tools/list")

        self.tools = {}
        for tool_data in result.get("tools", []):
            tool = MCPTool(
                name=tool_data["name"],
                description=tool_data.get("description", ""),
                input_schema=tool_data.get("inputSchema", {}),
                server_name=self.name,
            )
            self.tools[tool.name] = tool

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the server

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        result = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments,
        })

        # Extract text content
        content = result.get("content", [])
        texts = [item.get("text", "") for item in content if item.get("type") == "text"]

        return "\n".join(texts) if texts else str(result)


class MCPClient:
    """MCP Client that manages multiple servers"""

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.tools: Dict[str, MCPTool] = {}

    async def add_server(self, name: str, command: str, args: List[str] = None, env: Dict[str, str] = None) -> bool:
        """Add and start an MCP server

        Args:
            name: Server name
            command: Command to start the server
            args: Command arguments
            env: Environment variables

        Returns:
            True if successful
        """
        server = MCPServer(name, command, args, env)

        if await server.start():
            self.servers[name] = server

            # Register tools
            for tool_name, tool in server.tools.items():
                self.tools[tool_name] = tool

            return True

        return False

    async def remove_server(self, name: str):
        """Remove and stop an MCP server

        Args:
            name: Server name
        """
        if name in self.servers:
            server = self.servers[name]

            # Remove tools
            for tool_name in list(self.tools.keys()):
                if self.tools[tool_name].server_name == name:
                    del self.tools[tool_name]

            await server.stop()
            del self.servers[name]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        tool = self.tools.get(name)
        if not tool:
            return f"Error: MCP tool '{name}' not found"

        server = self.servers.get(tool.server_name)
        if not server:
            return f"Error: Server for tool '{name}' not found"

        try:
            return await server.call_tool(name, arguments)
        except Exception as e:
            return f"Error calling MCP tool: {str(e)}"

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all tool definitions in OpenAI format"""
        return [tool.to_openai_format() for tool in self.tools.values()]

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "server": tool.server_name,
            }
            for tool in self.tools.values()
        ]

    async def close(self):
        """Close all server connections"""
        for name in list(self.servers.keys()):
            await self.remove_server(name)

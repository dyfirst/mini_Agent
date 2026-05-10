"""Shell command execution tool"""

import asyncio
import subprocess
from typing import Dict, Any

from .base import Tool


class ShellTool(Tool):
    """Tool for executing shell commands"""

    def __init__(self, timeout: int = 30):
        """Initialize ShellTool

        Args:
            timeout: Command execution timeout in seconds
        """
        self.timeout = timeout

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "shell",
                "description": "Execute a shell command",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute",
                        }
                    },
                    "required": ["command"],
                },
            },
        }

    async def execute(self, command: str, **kwargs) -> str:
        """Execute shell command asynchronously

        Args:
            command: Command to execute

        Returns:
            Command output (stdout + stderr)
        """
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Error: Command timed out after {self.timeout} seconds"

            # Decode output
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            # Format result
            result = ""
            if stdout_str:
                result += stdout_str
            if stderr_str:
                if result:
                    result += "\n"
                result += f"STDERR:\n{stderr_str}"

            if process.returncode != 0:
                result += f"\nExit code: {process.returncode}"

            return result if result else "Command executed successfully (no output)"

        except Exception as e:
            return f"Error executing command: {str(e)}"

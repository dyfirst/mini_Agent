"""File operation tools"""

import os
from typing import Dict, Any

from .base import Tool


class ReadFileTool(Tool):
    """Tool for reading file contents"""

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read",
                        }
                    },
                    "required": ["path"],
                },
            },
        }

    async def execute(self, path: str, **kwargs) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"


class WriteFileTool(Tool):
    """Tool for writing file contents"""

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to write",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file",
                        },
                    },
                    "required": ["path", "content"],
                },
            },
        }

    async def execute(self, path: str, content: str, **kwargs) -> str:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"


class ListDirectoryTool(Tool):
    """Tool for listing directory contents"""

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "List contents of a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the directory (default: current directory)",
                        }
                    },
                    "required": [],
                },
            },
        }

    async def execute(self, path: str = ".", **kwargs) -> str:
        try:
            items = os.listdir(path)

            # Separate files and directories
            dirs = []
            files = []

            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    dirs.append(f"  📁 {item}/")
                else:
                    size = os.path.getsize(full_path)
                    files.append(f"  📄 {item} ({size} bytes)")

            # Format output
            result = f"Contents of {path}:\n"
            if dirs:
                result += "\nDirectories:\n" + "\n".join(dirs)
            if files:
                result += "\nFiles:\n" + "\n".join(files)

            return result
        except FileNotFoundError:
            return f"Error: Directory not found: {path}"
        except PermissionError:
            return f"Error: Permission denied: {path}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"

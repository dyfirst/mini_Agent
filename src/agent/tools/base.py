"""Base class for Tools"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Tool(ABC):
    """Abstract base class for agent tools"""

    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        """Get tool definition for LLM

        Returns:
            Tool definition in OpenAI function calling format
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool

        Args:
            **kwargs: Tool arguments

        Returns:
            Tool execution result as string
        """
        pass

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments

        Args:
            arguments: Arguments to validate

        Returns:
            True if valid, False otherwise
        """
        return True

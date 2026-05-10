"""Vibe Editor - Interactive code editing with AI"""

import re
from typing import List, Dict, Any, Optional

from .scanner import ProjectScanner
from ..agent_loop import AgentLoop
from ..providers.base import LLMProvider


class VibeEditor:
    """Interactive code editor with AI assistance"""

    def __init__(self, provider: LLMProvider, root_path: str = "."):
        """Initialize Vibe Editor

        Args:
            provider: LLM provider
            root_path: Project root path
        """
        self.provider = provider
        self.scanner = ProjectScanner(root_path)

    def build_context(self, task: str, files: List[str] = None) -> str:
        """Build context for the task

        Args:
            task: Task description
            files: Specific files to include (optional)

        Returns:
            Context string
        """
        context_parts = []

        # Add project structure
        scan_result = self.scanner.scan()
        context_parts.append("## Project Structure")
        context_parts.append(f"- Root: {scan_result['root']}")
        context_parts.append(f"- Files: {scan_result['file_count']}")
        context_parts.append(f"- Total lines: {scan_result['total_lines']}")

        # Add language stats
        if scan_result['languages']:
            context_parts.append("\n## Languages")
            for ext, count in sorted(scan_result['languages'].items(), key=lambda x: -x[1]):
                context_parts.append(f"- {ext}: {count} files")

        # Add relevant files
        if files is None:
            files = self.scanner.get_relevant_files(task)

        if files:
            context_parts.append("\n## Relevant Files")
            for filepath in files:
                content = self.scanner.read_file(filepath)
                context_parts.append(f"\n### {filepath}")
                context_parts.append("```")
                context_parts.append(content)
                context_parts.append("```")

        return "\n".join(context_parts)

    def parse_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Parse code blocks from LLM response

        Args:
            response: LLM response containing code blocks

        Returns:
            List of {filepath, content} dictionaries
        """
        blocks = []

        # Pattern: filepath followed by code block
        # Example: ### src/main.py
        # ```python
        # code here
        # ```
        pattern = r'###\s+(.+?)\s*\n```(?:\w+)?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)

        for filepath, content in matches:
            blocks.append({
                "filepath": filepath.strip(),
                "content": content.strip(),
            })

        return blocks

    async def edit(self, task: str, files: List[str] = None) -> str:
        """Execute an edit task

        Args:
            task: Edit task description
            files: Specific files to edit (optional)

        Returns:
            Response with changes
        """
        # Build context
        context = self.build_context(task, files)

        # Create prompt
        prompt = f"""You are a code editor. Based on the following project context and task, provide the necessary code changes.

{context}

## Task
{task}

## Instructions
1. Analyze the task and existing code
2. Provide complete file contents for any files that need to be created or modified
3. Use the format:
### filepath/to/file.py
```python
complete file content here
```

4. If no changes are needed, explain why

Provide your response:"""

        # Create agent
        agent = AgentLoop(
            provider=self.provider,
            system_prompt="You are an expert code editor. Provide complete, working code.",
        )

        # Get response
        response = await agent.run(prompt)

        return response

    async def apply_changes(self, response: str, auto_apply: bool = False) -> List[Dict[str, Any]]:
        """Apply changes from LLM response

        Args:
            response: LLM response with code blocks
            auto_apply: Whether to apply without confirmation

        Returns:
            List of applied changes
        """
        changes = []
        blocks = self.parse_code_blocks(response)

        for block in blocks:
            filepath = block["filepath"]
            new_content = block["content"]

            # Read current content
            old_content = self.scanner.read_file(filepath)

            if old_content == new_content:
                continue

            # Apply change
            if auto_apply:
                success = self.scanner.write_file(filepath, new_content)
                changes.append({
                    "file": filepath,
                    "applied": success,
                    "new_file": old_content.startswith("Error"),
                })
            else:
                changes.append({
                    "file": filepath,
                    "applied": False,
                    "pending": True,
                })

        return changes

    def format_response(self, response: str) -> str:
        """Format response for display

        Args:
            response: LLM response

        Returns:
            Formatted response
        """
        # Remove code blocks for cleaner display
        # but keep file references
        lines = response.split('\n')
        formatted = []
        in_code_block = False

        for line in lines:
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            formatted.append(line)

        return '\n'.join(formatted)

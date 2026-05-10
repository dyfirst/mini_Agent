"""Project scanner for Vibe Coding"""

import os
from typing import Dict, List, Any
from pathlib import Path


class ProjectScanner:
    """Scans and analyzes project structure"""

    # File extensions to include
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx',
        '.java', '.cpp', '.c', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php',
        '.html', '.css', '.scss',
        '.json', '.yaml', '.yml', '.toml',
        '.md', '.txt', '.sh', '.bash',
    }

    # Directories to ignore
    IGNORE_DIRS = {
        '__pycache__', 'node_modules', '.git',
        'venv', 'env', '.env', 'dist', 'build',
        '.idea', '.vscode', '.pytest_cache',
    }

    def __init__(self, root_path: str = "."):
        """Initialize scanner

        Args:
            root_path: Root directory to scan
        """
        self.root_path = os.path.abspath(root_path)

    def scan(self) -> Dict[str, Any]:
        """Scan project and return structure

        Returns:
            Project structure information
        """
        files = []
        languages = {}
        total_lines = 0

        for root, dirs, filenames in os.walk(self.root_path):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]

            for filename in filenames:
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, self.root_path)

                # Get file extension
                _, ext = os.path.splitext(filename)

                if ext.lower() in self.CODE_EXTENSIONS:
                    try:
                        # Count lines
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())

                        files.append({
                            "path": relative_path,
                            "extension": ext,
                            "lines": lines,
                        })

                        # Track languages
                        languages[ext] = languages.get(ext, 0) + 1
                        total_lines += lines

                    except Exception:
                        pass

        return {
            "root": self.root_path,
            "files": files,
            "file_count": len(files),
            "languages": languages,
            "total_lines": total_lines,
        }

    def read_file(self, filepath: str) -> str:
        """Read file content

        Args:
            filepath: File path (relative or absolute)

        Returns:
            File content
        """
        if os.path.isabs(filepath):
            full_path = filepath
        else:
            full_path = os.path.join(self.root_path, filepath)

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, filepath: str, content: str) -> bool:
        """Write content to file

        Args:
            filepath: File path (relative or absolute)
            content: Content to write

        Returns:
            True if successful
        """
        if os.path.isabs(filepath):
            full_path = filepath
        else:
            full_path = os.path.join(self.root_path, filepath)

        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

    def get_relevant_files(self, task: str, max_files: int = 5) -> List[str]:
        """Get files relevant to a task

        Args:
            task: Task description
            max_files: Maximum files to return

        Returns:
            List of relevant file paths
        """
        # Simple relevance scoring based on keywords
        task_lower = task.lower()
        keywords = task_lower.split()

        scored_files = []

        scan_result = self.scan()
        for file_info in scan_result["files"]:
            filepath = file_info["path"]
            filepath_lower = filepath.lower()

            # Calculate relevance score
            score = 0

            # Check if keywords appear in filepath
            for keyword in keywords:
                if keyword in filepath_lower:
                    score += 2

            # Check if keywords appear in filename
            filename = os.path.basename(filepath).lower()
            for keyword in keywords:
                if keyword in filename:
                    score += 3

            # Prefer Python files for Python tasks
            if 'python' in task_lower and filepath.endswith('.py'):
                score += 1

            if score > 0:
                scored_files.append((score, filepath))

        # Sort by score and return top files
        scored_files.sort(reverse=True)
        return [filepath for _, filepath in scored_files[:max_files]]

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

My Agent is a custom AI Agent implementation with Agent Loop, similar to Claude Code. It provides CLI interface for interacting with AI models with tool calling support.

## Build & Development Commands

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (development mode)
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Run the agent
agent chat                    # Interactive chat mode
agent ask "your query"        # Single query mode

# Run tests
pytest                        # Run all tests
pytest tests/test_agent.py    # Run specific test file
pytest -v                     # Verbose output
pytest -k "test_name"         # Run specific test

# Code formatting
black src/ tests/

# Type checking
mypy src/
```

## Architecture

### Core Flow
```
User Input → CLI (main.py) → Agent Loop → LLM Provider → Tool Execution → Response
```

### Key Modules

**Agent Loop** (`src/agent/agent_loop.py`):
- Core logic for processing user messages
- Manages conversation state and tool calling cycle
- Handles tool execution and result integration

**Tools System** (`src/agent/tools/`):
- `Tool` base class defines interface for all tools
- `ToolRegistry` manages tool registration and discovery
- Built-in tools: `ReadFileTool`, `WriteFileTool`, `ListDirectoryTool`, `ShellTool`
- Tools are defined with JSON Schema for LLM consumption

**Providers** (`src/agent/providers/`):
- `LLMProvider` abstract base class
- `OpenAIProvider` implements OpenAI API integration
- Supports tool calling format compatible with OpenAI/Anthropic

**CLI** (`src/agent/main.py`):
- Built with Click framework
- Commands: `chat` (interactive), `ask` (single query), `version`
- Rich library for terminal UI formatting

### Tool Definition Format

Tools use OpenAI-compatible function calling format:
```python
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "Tool description",
        "parameters": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}
```

## Development Notes

- Python 3.9+ required
- Async/await used throughout for LLM API calls
- Tools must inherit from `Tool` base class and implement `get_definition()` and `execute()`
- Register new tools in `ToolRegistry` to make them available to the agent
- Conversation history managed by `Conversation` class with message types: user, assistant, tool

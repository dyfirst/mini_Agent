# My Agent

Custom AI Agent with Agent Loop implementation.

## Features

- CLI interface for interactive AI conversations
- Agent Loop with tool calling support
- File operations (read, write, list)
- Shell command execution
- Extensible tool system

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Usage

```bash
# Interactive chat mode
agent chat

# Single query
agent ask "What is Python?"

# Execute with tools
agent chat --enable-tools
```

## Project Structure

```
my-agent/
├── src/agent/           # Main source code
│   ├── main.py         # CLI entry point
│   ├── agent_loop.py   # Agent Loop core
│   ├── conversation.py # Conversation management
│   ├── providers/      # LLM providers
│   ├── tools/          # Tool implementations
│   ├── mcp/            # MCP extension (optional)
│   └── skills/         # Skills extension (optional)
├── tests/              # Unit tests
└── docs/               # Documentation
```

## Development

```bash
# Run tests
pytest

# Format code
black src/ tests/
```

## License

MIT

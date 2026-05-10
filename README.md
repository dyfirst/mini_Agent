# My Agent

Custom AI Agent with Agent Loop implementation.

## Features

- CLI interface for interactive AI conversations
- Agent Loop with tool calling support
- Streaming output (typewriter effect)
- Skills system (predefined task templates)
- Multiple LLM provider support (OpenAI, DeepSeek, Anthropic, Ollama)
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

## Configuration

Set API keys for the LLM provider you want to use:

```bash
# DeepSeek (recommended)
export DEEPSEEK_API_KEY="your-deepseek-key"

# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"

# Ollama - No API key needed (runs locally)
```

## Usage

```bash
# List available providers
agent providers

# Interactive chat mode (default: openai)
agent chat --provider deepseek

# Single query
agent ask "What is Python?" --provider deepseek

# Execute with tools
agent chat --provider deepseek --enable-tools

# Specify model
agent ask "Hello" --provider deepseek --model deepseek-v4-flash

# Streaming output (typewriter effect)
agent ask "Hello" --provider deepseek --stream
agent chat --provider deepseek --stream --enable-tools

# List available skills
agent skills

# Run a skill
agent run-skill explain "什么是递归" --provider deepseek --stream
agent run-skill review_code "src/main.py" --provider deepseek
```

## Available Providers

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | gpt-4 |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-v4-flash |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| Ollama | (none) | llama3 |

## Project Structure

```
my-agent/
├── src/agent/              # Main source code
│   ├── main.py            # CLI entry point
│   ├── agent_loop.py      # Agent Loop core
│   ├── conversation.py    # Conversation management
│   ├── providers/         # LLM providers
│   │   ├── base.py        # Provider base class
│   │   ├── openai.py      # OpenAI provider
│   │   ├── deepseek.py    # DeepSeek provider
│   │   ├── anthropic.py   # Anthropic provider
│   │   └── ollama.py      # Ollama provider
│   └── tools/             # Tool implementations
│       ├── base.py        # Tool base class
│       ├── registry.py    # Tool registry
│       ├── file_ops.py    # File operations
│       └── shell.py       # Shell commands
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## Development

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_agent.py -v

# Run with coverage
python -m pytest --cov=src --cov-report=term-missing
```

## Testing

See [TEST_GUIDE.md](TEST_GUIDE.md) for detailed testing instructions.

Quick test:
```bash
# Unit tests (no API key needed)
python -m pytest tests/ -v

# Integration test (needs API key)
python -m src.agent.main ask "Hello" --provider deepseek
```

## License

MIT

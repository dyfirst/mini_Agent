# My Agent

Custom AI Agent with Agent Loop implementation.

English | [中文](README_CN.md)

## Features

- CLI interface for interactive AI conversations
- Agent Loop with tool calling support
- Streaming output (typewriter effect)
- Skills system (predefined task templates)
- MCP (Model Context Protocol) support for external tool servers
- Vibe Coding mode (interactive code editing with AI)
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

# List MCP servers
agent mcp-servers

# Chat with MCP tools enabled
agent chat --provider deepseek --enable-mcp

# Vibe Coding mode
agent vibe --task "添加用户认证功能" --provider deepseek
agent vibe --dir ./my-project --auto-apply
```

## Available Providers

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | gpt-4 |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-v4-flash |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| Ollama | (none) | llama3 |

## Skills System

### How It Works

```
用户输入 Skill 名称和任务
        ↓
SkillLoader 加载 YAML 配置
        ↓
获取 Skill 的 prompt 模板
        ↓
拼接 prompt + 用户任务
        ↓
创建 Agent（自动启用需要的工具）
        ↓
调用 LLM 执行任务
        ↓
返回结果
```

### Built-in Skills

**CODING**
| Skill | Description | Tools |
|-------|-------------|-------|
| `explain_code` | Explain code functionality | read_file |
| `review_code` | Code review | read_file |
| `refactor_code` | Refactoring suggestions | read_file, write_file |
| `write_tests` | Write unit tests | read_file, write_file |
| `fix_bug` | Fix bugs | read_file, write_file, shell |

**FILE**
| Skill | Description | Tools |
|-------|-------------|-------|
| `read_summary` | Read and summarize file | read_file |
| `find_files` | Find files by pattern | list_directory, shell |
| `create_file` | Create new file | write_file |
| `compare_files` | Compare file differences | read_file, shell |

**GENERAL**
| Skill | Description | Tools |
|-------|-------------|-------|
| `explain` | Explain concepts | - |
| `brainstorm` | Brainstorm ideas | - |
| `summarize` | Summarize content | read_file |
| `translate` | Translate text | - |
| `format_text` | Format text | - |

### Creating Custom Skills

Create a YAML file in `src/agent/skills/builtin/`:

```yaml
skills:
  - name: my_skill
    description: "Description of my skill"
    category: custom
    prompt: "Your prompt template:"
    tools:
      - read_file
    examples:
      - "my_skill example task"
```

## MCP (Model Context Protocol) Support

### What is MCP?

MCP is a protocol that allows AI models to connect to external tool servers. This enables access to tools like:
- Filesystem operations
- GitHub integration
- Web search
- Database access
- And more...

### How It Works

```
User Request
    ↓
Agent with MCP tools enabled
    ↓
MCP Client connects to servers
    ↓
Discover available tools
    ↓
Call tools as needed
    ↓
Return results to user
```

### Configuration

Create `mcp_config.json` in project root:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

### Usage

```bash
# List configured MCP servers
agent mcp-servers

# Chat with MCP tools
agent chat --provider deepseek --enable-mcp

# Single query with MCP tools
agent ask "List files in /path" --provider deepseek --enable-mcp
```

### Available MCP Servers

| Server | Description |
|--------|-------------|
| `@modelcontextprotocol/server-filesystem` | File system operations |
| `@modelcontextprotocol/server-github` | GitHub integration |
| `@modelcontextprotocol/server-brave-search` | Web search |
| `@modelcontextprotocol/server-memory` | Knowledge graph |

## Vibe Coding

### What is Vibe Coding?

Vibe Coding is an interactive code editing mode that lets you describe changes in natural language and have AI implement them for you.

### How It Works

```
用户描述任务
    ↓
扫描项目结构
    ↓
收集相关文件作为上下文
    ↓
AI 生成代码修改
    ↓
应用到文件
```

### Usage

```bash
# Start Vibe Coding mode
agent vibe --provider deepseek

# With initial task
agent vibe --task "添加用户认证功能" --provider deepseek

# Specify project directory
agent vibe --dir ./my-project --provider deepseek

# Auto-apply changes without confirmation
agent vibe --task "重构数据库模块" --provider deepseek --auto-apply
```

### Features

- **Project Scanning**: Automatically scans project structure and languages
- **Context Collection**: Collects relevant files as context for AI
- **Interactive Editing**: Describe changes in natural language
- **Auto-Apply**: Option to automatically apply changes

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
│   ├── tools/             # Tool implementations
│   │   ├── base.py        # Tool base class
│   │   ├── registry.py    # Tool registry
│   │   ├── file_ops.py    # File operations
│   │   └── shell.py       # Shell commands
│   ├── skills/            # Skills system
│   │   ├── loader.py      # Skill loader
│   │   └── builtin/       # Built-in skills
│   │       ├── coding.yml
│   │       ├── file_ops.yml
│   │       └── general.yml
│   ├── mcp/               # MCP support
│   │   ├── client.py      # MCP client
│   │   └── adapter.py     # MCP tool adapter
│   └── vibe/              # Vibe Coding
│       ├── scanner.py     # Project scanner
│       └── editor.py      # Code editor
├── mcp_config.example.json # MCP configuration example
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

# Test skills
python -m src.agent.main skills
python -m src.agent.main run-skill explain "什么是递归" --provider deepseek
```

## License

MIT

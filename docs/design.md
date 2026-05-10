# My Agent - 设计文档

## 1. 项目概述

My Agent 是一个自定义的 AI Agent 实现，类似于 Claude Code。它提供了一个 CLI 界面，允许用户与 AI 模型进行交互，并支持工具调用功能。

### 1.1 核心功能

- **CLI 交互界面**：支持交互式聊天和单次查询模式
- **Agent Loop**：核心逻辑，处理用户输入、LLM 响应和工具调用
- **工具系统**：可扩展的工具架构，支持文件操作和命令行执行
- **多 Provider 支持**：支持 OpenAI、DeepSeek、Anthropic、Ollama 等多种 LLM 服务商

### 1.2 技术栈

- **Python 3.9+**
- **Click**：CLI 框架
- **Rich**：终端 UI 美化
- **OpenAI SDK**：LLM 服务（兼容 DeepSeek、Ollama）
- **Anthropic SDK**：Claude 服务
- **Pytest**：测试框架

---

## 2. 架构设计

### 2.1 整体架构

```
用户输入
    ↓
CLI (main.py)
    ↓
Agent Loop
    ↓
LLM Provider (OpenAI/DeepSeek/Anthropic/Ollama)
    ↓
工具调用? → 是 → 执行工具 → 返回结果 → 继续循环
    ↓ 否
返回最终响应
```

### 2.2 核心模块

#### 2.2.1 Agent Loop (`agent_loop.py`)

Agent Loop 是系统的核心，负责：
- 接收用户输入
- 调用 LLM 生成响应
- 解析响应中的工具调用
- 执行工具并获取结果
- 将结果反馈给 LLM
- 返回最终响应

**关键类**：
- `AgentLoop`：主循环类

**关键方法**：
- `run(user_input: str) -> str`：处理用户输入并返回响应
- `_get_llm_response()`：获取 LLM 响应
- `_process_tool_calls(response)`：处理工具调用

#### 2.2.2 Conversation (`conversation.py`)

管理会话历史，包括：
- 系统提示词
- 用户消息
- 助手响应
- 工具调用和结果

**关键类**：
- `Message`：单条消息
- `Conversation`：会话管理器

#### 2.2.3 Providers (`providers/`)

LLM Provider 抽象层：

| Provider | 文件 | 环境变量 | 默认模型 |
|----------|------|----------|----------|
| OpenAI | `openai.py` | `OPENAI_API_KEY` | gpt-4 |
| DeepSeek | `deepseek.py` | `DEEPSEEK_API_KEY` | deepseek-v4-flash |
| Anthropic | `anthropic.py` | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| Ollama | `ollama.py` | 无 | llama3 |

**接口定义**：
```python
class LLMProvider(ABC):
    async def chat(messages, tools) -> LLMResponse
    async def stream_chat(messages, tools) -> AsyncGenerator
```

#### 2.2.4 Tools (`tools/`)

工具系统：
- `Tool`：工具抽象基类
- `ToolRegistry`：工具注册和发现
- 内置工具：ReadFileTool, WriteFileTool, ListDirectoryTool, ShellTool

**工具定义格式**（OpenAI 兼容）：
```json
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

### 2.3 数据流

```
1. 用户输入 "读取 config.txt 文件"
2. CLI 接收输入，创建 AgentLoop
3. AgentLoop.run() 被调用
4. 添加用户消息到会话
5. 调用 LLM Provider.chat()
6. LLM 返回工具调用：read_file(path="config.txt")
7. AgentLoop 调用 ToolRegistry.execute("read_file", {path: "config.txt"})
8. 工具返回文件内容
9. 将工具结果添加到会话
10. 再次调用 LLM Provider.chat()
11. LLM 返回最终响应
12. 返回响应给用户
```

---

## 3. 模块详细设计

### 3.1 CLI 模块

**文件**：`main.py`

**命令**：
- `agent chat`：交互式聊天
- `agent ask "prompt"`：单次查询
- `agent providers`：列出可用 Provider
- `agent version`：显示版本

**选项**：
- `--provider, -p`：指定 LLM Provider (openai, deepseek, anthropic, ollama)
- `--model, -m`：指定模型
- `--enable-tools, -t`：启用工具调用

### 3.2 Agent Loop 模块

**核心流程**：
```python
async def run(self, user_input: str) -> str:
    self.conversation.add_user_message(user_input)

    while iterations < max_iterations:
        response = await self._get_llm_response()

        if response.has_tool_calls:
            await self._process_tool_calls(response)
            continue

        return response.content

    return "Maximum iterations reached"
```

**错误处理**：
- LLM API 错误：重试并返回错误信息
- 工具执行错误：返回错误信息给 LLM
- 最大迭代次数：防止无限循环

### 3.3 工具系统

**工具基类**：
```python
class Tool(ABC):
    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        """获取工具定义"""

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """执行工具"""
```

**注册新工具**：
```python
registry = ToolRegistry()
registry.register("my_tool", MyTool())
```

**内置工具**：

| 工具名称 | 功能 | 参数 |
|---------|------|------|
| read_file | 读取文件内容 | path |
| write_file | 写入文件内容 | path, content |
| list_directory | 列出目录内容 | path |
| shell | 执行 shell 命令 | command |

### 3.4 Provider 系统

**Provider 接口**：
```python
class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        pass
```

**LLMResponse 结构**：
```python
@dataclass
class LLMResponse:
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
```

**ToolCall 结构**：
```python
@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]
```

---

## 4. API 文档

### 4.1 CLI API

```bash
# 查看帮助
agent --help

# 列出可用 Provider
agent providers

# 交互式聊天
agent chat [OPTIONS]
  -p, --provider TEXT  LLM provider (openai, deepseek, anthropic, ollama)
  -m, --model TEXT     Model to use
  -t, --enable-tools   Enable tool calling

# 单次查询
agent ask PROMPT [OPTIONS]
  -p, --provider TEXT  LLM provider
  -m, --model TEXT     Model to use
  -t, --enable-tools   Enable tool calling

# 显示版本
agent version
```

### 4.2 Python API

#### AgentLoop

```python
from src.agent.agent_loop import AgentLoop
from src.agent.providers.deepseek import DeepSeekProvider
from src.agent.tools import ToolRegistry, ReadFileTool

# 创建 Provider
provider = DeepSeekProvider(api_key="your-key")

# 创建工具注册表
tools = ToolRegistry()
tools.register("read_file", ReadFileTool())

# 创建 Agent
agent = AgentLoop(
    provider=provider,
    tools=tools,
    system_prompt="You are a helpful assistant.",
    max_iterations=10,
)

# 运行
response = await agent.run("Hello")
```

#### Conversation

```python
from src.agent.conversation import Conversation

conv = Conversation(system_prompt="You are a helper")
conv.add_user_message("Hello")
conv.add_assistant_message("Hi!")
conv.add_tool_result("tool_id", "result")

messages = conv.get_messages_for_api()
```

#### ToolRegistry

```python
from src.agent.tools import ToolRegistry, ReadFileTool, ShellTool

registry = ToolRegistry()
registry.register("read_file", ReadFileTool())
registry.register("shell", ShellTool())

definitions = registry.get_tool_definitions()
result = await registry.execute("read_file", {"path": "test.txt"})
```

---

## 5. 使用示例

### 5.1 基本使用

```bash
# 设置 API Key
export DEEPSEEK_API_KEY="your-key"

# 单次查询
agent ask "What is Python?" --provider deepseek

# 交互式聊天
agent chat --provider deepseek

# 带工具的聊天
agent chat --provider deepseek --enable-tools
```

### 5.2 使用不同 Provider

```bash
# 使用 OpenAI
agent ask "Hello" --provider openai --model gpt-3.5-turbo

# 使用 DeepSeek
agent ask "Hello" --provider deepseek --model deepseek-v4-flash

# 使用 Anthropic
agent ask "Hello" --provider anthropic

# 使用 Ollama（本地）
agent ask "Hello" --provider ollama --model llama3
```

### 5.3 工具调用示例

```bash
# 读取文件
agent ask "读取 README.md 的内容" --provider deepseek --enable-tools

# 列出目录
agent ask "列出当前目录的文件" --provider deepseek --enable-tools

# 执行命令
agent ask "查看 Python 版本" --provider deepseek --enable-tools
```

---

## 6. 扩展指南

### 6.1 添加新工具

1. 创建工具类，继承 `Tool`
2. 实现 `get_definition()` 方法
3. 实现 `execute()` 方法
4. 在 `ToolRegistry` 中注册

```python
from src.agent.tools.base import Tool

class MyTool(Tool):
    def get_definition(self):
        return {
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "My custom tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Parameter description"
                        }
                    },
                    "required": ["param1"]
                }
            }
        }

    async def execute(self, param1: str, **kwargs) -> str:
        # 实现逻辑
        return f"Result: {param1}"
```

### 6.2 添加新 Provider

1. 创建 Provider 类，继承 `LLMProvider`
2. 实现 `chat()` 方法
3. 可选：实现 `stream_chat()` 方法
4. 在 `main.py` 的 `PROVIDER_CONFIG` 中注册

```python
from src.agent.providers.base import LLMProvider, LLMResponse

class MyProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "default"):
        self.api_key = api_key
        self.model = model

    async def chat(self, messages, tools=None):
        # 调用 LLM API
        return LLMResponse(content="response")
```

---

## 7. 测试策略

### 7.1 单元测试

- 测试 Conversation 类
- 测试 ToolRegistry 类
- 测试各个 Tool 实现
- 测试 Provider 基类

### 7.2 集成测试

- 测试完整的 Agent Loop 流程
- 测试工具链式调用
- 测试错误处理

### 7.3 测试命令

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_agent.py -v

# 运行 Agent Loop 测试（需要 API Key）
python -m pytest tests/test_agent_loop.py -v
```

---

## 8. 项目结构

```
my-agent/
├── src/
│   └── agent/
│       ├── main.py              # CLI 入口
│       ├── agent_loop.py        # Agent Loop 核心
│       ├── conversation.py      # 会话管理
│       ├── providers/           # LLM Provider
│       │   ├── __init__.py
│       │   ├── base.py          # Provider 基类
│       │   ├── openai.py        # OpenAI Provider
│       │   ├── deepseek.py      # DeepSeek Provider
│       │   ├── anthropic.py     # Anthropic Provider
│       │   └── ollama.py        # Ollama Provider
│       └── tools/               # 工具系统
│           ├── __init__.py
│           ├── base.py          # Tool 基类
│           ├── registry.py      # ToolRegistry
│           ├── file_ops.py      # 文件操作工具
│           └── shell.py         # Shell 工具
├── tests/                       # 测试
│   ├── test_agent.py
│   ├── test_agent_loop.py
│   ├── test_conversation.py
│   ├── test_file_tools.py
│   ├── test_registry.py
│   └── test_shell_tool.py
├── docs/                        # 文档
│   └── design.md
├── pyproject.toml               # 项目配置
├── README.md                    # 项目说明
├── TEST_GUIDE.md                # 测试指南
└── CLAUDE.md                    # Claude Code 配置
```

---

## 9. 依赖列表

### 核心依赖

- click >= 8.0
- httpx >= 0.24.0
- pydantic >= 2.0
- rich >= 13.0
- prompt_toolkit >= 3.0
- openai >= 1.0

### 可选依赖

- anthropic >= 0.18.0（用于 Anthropic Provider）

### 开发依赖

- pytest >= 7.0
- pytest-asyncio >= 0.21
- pytest-cov（可选，用于覆盖率）

---

## 10. 参考资料

- [OpenAI API 文档](https://platform.openai.com/docs)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [Click 文档](https://click.palletsprojects.com/)
- [Rich 文档](https://rich.readthedocs.io/)

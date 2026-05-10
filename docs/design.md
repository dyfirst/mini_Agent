# My Agent - 设计文档

## 1. 项目概述

My Agent 是一个自定义的 AI Agent 实现，类似于 Claude Code。它提供了一个 CLI 界面，允许用户与 AI 模型进行交互，并支持工具调用功能。

### 1.1 核心功能

- **CLI 交互界面**：支持交互式聊天和单次查询模式
- **Agent Loop**：核心逻辑，处理用户输入、LLM 响应和工具调用
- **工具系统**：可扩展的工具架构，支持文件操作和命令行执行
- **Provider 系统**：支持多种 LLM 服务商（当前实现 OpenAI）

### 1.2 技术栈

- **Python 3.9+**
- **Click**：CLI 框架
- **Rich**：终端 UI 美化
- **OpenAI API**：LLM 服务
- **Pytest**：测试框架

## 2. 架构设计

### 2.1 整体架构

```
用户输入
    ↓
CLI (main.py)
    ↓
Agent Loop
    ↓
LLM Provider
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
- `LLMProvider`：抽象基类
- `OpenAIProvider`：OpenAI API 实现

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

## 3. 模块详细设计

### 3.1 CLI 模块

**文件**：`main.py`

**命令**：
- `agent chat`：交互式聊天
- `agent ask "prompt"`：单次查询
- `agent version`：显示版本

**选项**：
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

## 4. 扩展指南

### 4.1 添加新工具

1. 创建工具类，继承 `Tool`
2. 实现 `get_definition()` 方法
3. 实现 `execute()` 方法
4. 在 `ToolRegistry` 中注册

```python
class MyTool(Tool):
    def get_definition(self):
        return {
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "My custom tool",
                "parameters": {...}
            }
        }

    async def execute(self, **kwargs):
        # 实现逻辑
        return "result"
```

### 4.2 添加新 Provider

1. 创建 Provider 类，继承 `LLMProvider`
2. 实现 `chat()` 方法
3. 可选：实现 `stream_chat()` 方法

```python
class MyProvider(LLMProvider):
    async def chat(self, messages, tools=None):
        # 调用 LLM API
        return LLMResponse(content="response")
```

### 4.3 添加 MCP 支持

MCP (Model Context Protocol) 扩展：
1. 实现 MCP 客户端
2. 将 MCP 工具转换为 Tool 接口
3. 在 ToolRegistry 中注册

### 4.4 添加 Skills 支持

Skills 扩展：
1. 定义 Skill 文件格式（YAML/JSON）
2. 实现 Skill 加载器
3. 将 Skill 转换为工具调用

## 5. 测试策略

### 5.1 单元测试

- 测试 Conversation 类
- 测试 ToolRegistry 类
- 测试各个 Tool 实现
- 测试 Provider 基类

### 5.2 集成测试

- 测试完整的 Agent Loop 流程
- 测试工具链式调用
- 测试错误处理

### 5.3 测试命令

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agent.py

# 运行带详细输出
pytest -v
```

## 6. 部署和使用

### 6.1 安装

```bash
# 克隆仓库
git clone <repository-url>
cd my-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -e .
```

### 6.2 配置

设置 OpenAI API Key：
```bash
export OPENAI_API_KEY="your-api-key"
```

### 6.3 使用

```bash
# 交互式聊天
agent chat

# 带工具的聊天
agent chat --enable-tools

# 单次查询
agent ask "What is Python?"

# 指定模型
agent chat --model gpt-3.5-turbo
```

## 7. 性能考虑

### 7.1 并发处理

- 使用 `asyncio` 进行异步操作
- 工具执行可以并发（如果无依赖）

### 7.2 缓存

- 可以添加 LLM 响应缓存
- 可以添加工具结果缓存

### 7.3 限制

- 最大迭代次数限制（默认 10）
- 工具执行超时（Shell 工具默认 30 秒）
- 会话历史长度限制（可选）

## 8. 安全考虑

### 8.1 API Key 管理

- 从环境变量读取 API Key
- 不在代码中硬编码

### 8.2 工具执行安全

- Shell 工具执行命令时需谨慎
- 文件操作工具应验证路径
- 可以添加白名单/黑名单机制

### 8.3 输入验证

- 验证工具参数
- 过滤敏感命令
- 限制文件访问范围

## 9. 未来改进

### 9.1 功能增强

- 支持更多 LLM Provider（Anthropic, Google）
- 支持流式输出
- 支持多模态输入（图片、文件）
- 支持会话持久化

### 9.2 工具增强

- 添加更多内置工具（搜索、数据库操作）
- 支持工具组合
- 支持条件工具调用

### 9.3 用户体验

- 添加命令历史
- 添加自动补全
- 添加主题配置

## 10. 附录

### 10.1 项目结构

```
my-agent/
├── src/
│   └── agent/
│       ├── main.py           # CLI 入口
│       ├── agent_loop.py     # Agent Loop 核心
│       ├── conversation.py   # 会话管理
│       ├── providers/        # LLM Provider
│       │   ├── base.py
│       │   └── openai.py
│       └── tools/            # 工具系统
│           ├── base.py
│           ├── registry.py
│           ├── file_ops.py
│           └── shell.py
├── tests/                    # 测试
├── docs/                     # 文档
├── pyproject.toml           # 项目配置
└── README.md                # 项目说明
```

### 10.2 依赖列表

- click >= 8.0
- httpx >= 0.24.0
- pydantic >= 2.0
- rich >= 13.0
- prompt_toolkit >= 3.0
- openai >= 1.0

### 10.3 参考资料

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Click 文档](https://click.palletsprojects.com/)
- [Rich 文档](https://rich.readthedocs.io/)

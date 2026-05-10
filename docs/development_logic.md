# My Agent 开发逻辑文档

## 一、项目概述

My Agent 是一个自定义 AI Agent 实现，核心是 **Agent Loop**（智能体循环），通过 CLI 与用户交互，支持多种 LLM Provider、工具调用、Skills 系统、MCP 协议和 Vibe Coding。

### 技术栈

- **语言**: Python 3.9+
- **CLI 框架**: Click
- **终端美化**: Rich
- **异步**: asyncio
- **LLM SDK**: openai, anthropic
- **配置**: PyYAML
- **测试**: pytest, pytest-asyncio

---

## 二、核心架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI (main.py)                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐│
│  │  chat   │ │   ask   │ │ skills  │ │  vibe   │ │  mcp   ││
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └───┬────┘│
│       │           │           │           │          │      │
│       └───────────┴───────────┴───────────┴──────────┘      │
│                            │                                 │
│                    ┌───────▼───────┐                        │
│                    │  Agent Loop   │                        │
│                    └───────┬───────┘                        │
│                            │                                 │
│           ┌────────────────┼────────────────┐               │
│           │                │                │               │
│   ┌───────▼───────┐ ┌─────▼─────┐ ┌────────▼────────┐     │
│   │   Provider    │ │   Tools   │ │   Conversation  │     │
│   │ (OpenAI等)    │ │ (文件等)  │ │   (会话管理)    │     │
│   └───────────────┘ └───────────┘ └─────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
用户输入 "读取 README.md"
        │
        ▼
┌───────────────┐
│   CLI 接收    │  main.py → chat/ask 命令
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ 创建 Agent    │  create_agent() → 创建 Provider + Tools
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Agent Loop    │  agent.run(user_input)
└───────┬───────┘
        │
        ▼
┌───────────────┐     ┌───────────────┐
│ 调用 Provider │ ──► │ LLM 返回响应  │
└───────────────┘     └───────┬───────┘
                              │
                    ┌─────────▼─────────┐
                    │ 是否有工具调用？  │
                    └─────────┬─────────┘
                              │
                 ┌────────────┴────────────┐
                 │ 否                      │ 是
                 ▼                         ▼
        ┌───────────────┐        ┌───────────────┐
        │ 返回最终响应  │        │ 执行工具      │
        └───────────────┘        └───────┬───────┘
                                         │
                                         ▼
                                ┌───────────────┐
                                │ 结果加入会话  │
                                └───────┬───────┘
                                        │
                                        ▼
                                   继续循环
```

---

## 三、核心模块逻辑

### 3.1 Agent Loop（核心循环）

**文件**: `src/agent/agent_loop.py`

**职责**: 协调 Provider、Tools 和 Conversation 的交互

```python
class AgentLoop:
    def __init__(self, provider, tools, system_prompt, max_iterations=10):
        self.provider = provider          # LLM 提供商
        self.tools = tools                # 工具注册表
        self.conversation = Conversation() # 会话管理
        self.max_iterations = max_iterations

    async def run(self, user_input: str) -> str:
        """主循环"""
        self.conversation.add_user_message(user_input)

        for _ in range(self.max_iterations):
            # 1. 调用 LLM
            response = await self.provider.chat(
                messages=self.conversation.get_messages_for_api(),
                tools=self.tools.get_tool_definitions()
            )

            # 2. 检查是否有工具调用
            if response.has_tool_calls:
                # 3. 执行工具
                for tool_call in response.tool_calls:
                    result = await self.tools.execute(
                        tool_call.name,
                        tool_call.arguments
                    )
                    self.conversation.add_tool_result(tool_call.id, result)
                continue  # 继续循环

            # 4. 返回最终响应
            self.conversation.add_assistant_message(response.content)
            return response.content

        return "Maximum iterations reached"
```

**关键点**:
- 最大迭代次数限制（防止无限循环）
- 工具调用结果自动加入会话
- 支持流式输出 `run_stream()`

---

### 3.2 Provider 系统（LLM 提供商）

**文件**: `src/agent/providers/`

**职责**: 封装不同 LLM API 的调用

```
providers/
├── base.py        # 抽象基类
├── openai.py      # OpenAI 实现
├── deepseek.py    # DeepSeek 实现（OpenAI 兼容）
├── anthropic.py   # Anthropic 实现
└── ollama.py      # Ollama 实现（本地模型）
```

**核心接口**:

```python
class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages, tools) -> LLMResponse:
        """发送聊天请求"""
        pass

    @abstractmethod
    async def stream_chat(self, messages, tools):
        """流式聊天"""
        pass
```

**LLMResponse 结构**:

```python
@dataclass
class LLMResponse:
    content: Optional[str] = None           # 文本响应
    tool_calls: Optional[List[ToolCall]] = None  # 工具调用
```

**多 Provider 设计**:
- 统一接口，可替换
- 通过环境变量配置 API Key
- 支持自定义模型和 base_url

---

### 3.3 Tools 系统（工具）

**文件**: `src/agent/tools/`

**职责**: 提供可扩展的工具能力

```
tools/
├── base.py        # Tool 抽象基类
├── registry.py    # 工具注册表
├── file_ops.py    # 文件操作工具
└── shell.py       # Shell 命令工具
```

**工具定义格式**（OpenAI 兼容）:

```json
{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file"
                }
            },
            "required": ["path"]
        }
    }
}
```

**内置工具**:

| 工具 | 功能 | 参数 |
|------|------|------|
| `read_file` | 读取文件 | path |
| `write_file` | 写入文件 | path, content |
| `list_directory` | 列出目录 | path |
| `shell` | 执行命令 | command |

**扩展新工具**:

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

    async def execute(self, **kwargs) -> str:
        # 实现逻辑
        return "result"

# 注册
registry.register("my_tool", MyTool())
```

---

### 3.4 Conversation（会话管理）

**文件**: `src/agent/conversation.py`

**职责**: 管理消息历史

```python
class Conversation:
    def __init__(self, system_prompt=None):
        self.messages = []

    def add_user_message(self, content):
        """添加用户消息"""

    def add_assistant_message(self, content, tool_calls=None):
        """添加助手响应"""

    def add_tool_result(self, tool_call_id, content):
        """添加工具执行结果"""

    def get_messages_for_api(self) -> List[Dict]:
        """获取 API 格式的消息列表"""
```

**消息类型**:

```python
# 系统消息
{"role": "system", "content": "You are a helpful assistant"}

# 用户消息
{"role": "user", "content": "Hello"}

# 助手消息（普通）
{"role": "assistant", "content": "Hi!"}

# 助手消息（带工具调用）
{
    "role": "assistant",
    "tool_calls": [{
        "id": "call_123",
        "type": "function",
        "function": {"name": "read_file", "arguments": "{\"path\": \"test.txt\"}"}
    }]
}

# 工具结果
{"role": "tool", "tool_call_id": "call_123", "content": "file content..."}
```

---

### 3.5 Skills 系统

**文件**: `src/agent/skills/`

**职责**: 提供预定义的任务模板

```
skills/
├── __init__.py
├── loader.py           # Skill 加载器
└── builtin/            # 内置 Skills
    ├── coding.yml      # 编程相关
    ├── file_ops.yml    # 文件操作
    └── general.yml     # 通用
```

**工作流程**:

```
用户: agent run-skill explain "什么是递归"
            │
            ▼
┌───────────────────────┐
│ SkillLoader 加载配置  │  从 YAML 文件读取
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 获取 Skill prompt     │  "Please explain the following:"
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 拼接完整 prompt       │  prompt + "\n\n" + "什么是递归"
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 创建 Agent 并执行     │  自动启用 Skill 需要的工具
└───────────────────────┘
```

**YAML 配置格式**:

```yaml
skills:
  - name: explain
    description: "Explain a concept"
    category: general
    prompt: "Please explain the following:"
    tools: []  # 需要的工具
    examples:
      - "explain how HTTP works"
```

---

### 3.6 MCP 支持

**文件**: `src/agent/mcp/`

**职责**: 连接外部工具服务器

```
mcp/
├── __init__.py
├── client.py    # MCP 客户端
└── adapter.py   # 工具适配器
```

**MCP 协议**:

```
┌─────────────┐     JSON-RPC      ┌─────────────┐
│  MCP Client │ ◄──────────────► │  MCP Server │
│  (my-agent) │     stdio         │  (npx ...)  │
└─────────────┘                   └─────────────┘
```

**通信流程**:

```python
# 1. 启动服务器进程
process = await asyncio.create_subprocess_exec("npx", "-y", "@modelcontextprotocol/server-filesystem", ".")

# 2. 发送初始化请求
await send_request("initialize", {
    "protocolVersion": "2024-11-05",
    "clientInfo": {"name": "my-agent", "version": "0.4.0"}
})

# 3. 列出可用工具
result = await send_request("tools/list")

# 4. 调用工具
result = await send_request("tools/call", {
    "name": "read_file",
    "arguments": {"path": "README.md"}
})
```

**MCPToolAdapter**: 将 MCP 工具桥接到内部 Tool 系统

---

### 3.7 Vibe Coding

**文件**: `src/agent/vibe/`

**职责**: 交互式代码编辑

```
vibe/
├── __init__.py
├── scanner.py   # 项目扫描器
└── editor.py    # 编辑器
```

**工作流程**:

```
用户: "创建一个包含当前时间的 txt 文件"
            │
            ▼
┌───────────────────────┐
│ ProjectScanner 扫描   │  获取项目结构、文件列表
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 收集相关上下文        │  读取相关文件内容
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 构建完整 prompt       │  项目上下文 + 用户任务
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ LLM 生成代码          │  返回包含代码块的响应
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 解析代码块            │  提取文件路径和内容
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 应用到文件            │  写入文件系统
└───────────────────────┘
```

---

## 四、CLI 命令结构

```
agent
├── chat          # 交互式聊天
│   ├── --provider    # LLM 提供商
│   ├── --model       # 模型名称
│   ├── --enable-tools # 启用工具
│   ├── --enable-mcp   # 启用 MCP
│   └── --stream       # 流式输出
│
├── ask           # 单次查询
│   └── (同 chat 选项)
│
├── providers     # 列出 Provider
├── skills        # 列出 Skills
├── run-skill     # 运行 Skill
├── mcp-servers   # 列出 MCP 服务器
├── vibe          # Vibe Coding 模式
│   ├── --task        # 初始任务
│   ├── --dir         # 项目目录
│   └── --auto-apply  # 自动应用
│
└── version       # 版本信息
```

---

## 五、扩展机制

### 5.1 添加新 Provider

```python
# 1. 创建 Provider 文件
class MyProvider(LLMProvider):
    async def chat(self, messages, tools=None):
        # 调用 API
        return LLMResponse(content="response")

# 2. 在 main.py 注册
PROVIDER_CONFIG["my_provider"] = {
    "name": "My Provider",
    "env_key": "MY_API_KEY",
    "default_model": "default",
    "provider_class": MyProvider,
}
```

### 5.2 添加新工具

```python
# 1. 创建工具类
class MyTool(Tool):
    def get_definition(self):
        return {...}

    async def execute(self, **kwargs):
        return "result"

# 2. 在 create_agent() 中注册
tools.register("my_tool", MyTool())
```

### 5.3 添加新 Skill

```yaml
# 创建 YAML 文件: src/agent/skills/builtin/my_skills.yml
skills:
  - name: my_skill
    description: "My custom skill"
    category: custom
    prompt: "Do this task:"
    tools: [read_file]
    examples: ["my_skill example"]
```

### 5.4 添加 MCP 服务器

```json
// mcp_config.json
{
  "mcpServers": {
    "my_server": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"],
      "env": {"API_KEY": "xxx"}
    }
  }
}
```

---

## 六、测试策略

### 6.1 测试层次

```
┌─────────────────────────────────────┐
│         集成测试 (2 skipped)        │  需要 API Key
├─────────────────────────────────────┤
│         单元测试 (20 passed)        │  本地测试
├─────────────────────────────────────┤
│         工具测试                    │  文件、Shell
└─────────────────────────────────────┘
```

### 6.2 测试文件

| 文件 | 测试内容 | 需要 API |
|------|----------|----------|
| test_agent.py | Conversation, ToolRegistry | 否 |
| test_conversation.py | 会话管理 | 否 |
| test_registry.py | 工具注册 | 否 |
| test_file_tools.py | 文件工具 | 否 |
| test_shell_tool.py | Shell 工具 | 否 |
| test_mcp.py | MCP 模块 | 否 |
| test_vibe.py | Vibe Coding | 否 |
| test_agent_loop.py | Agent Loop | 是 |

---

## 七、版本历史

| 版本 | 功能 | 提交 |
|------|------|------|
| v0.1.0 | CLI 框架、Agent Loop、基础工具 | 67decde |
| v0.2.0 | 多 Provider、流式输出 | 3f96e95 |
| v0.3.0 | Skills 系统 | 2706c49 |
| v0.4.0 | MCP 支持 | 9db46e3 |
| v0.5.0 | Vibe Coding | a553ecb |

---

## 八、项目结构

```
my-agent/
├── src/agent/
│   ├── __init__.py
│   ├── main.py              # CLI 入口
│   ├── agent_loop.py        # Agent Loop 核心
│   ├── conversation.py      # 会话管理
│   ├── providers/           # LLM Provider
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── deepseek.py
│   │   ├── anthropic.py
│   │   └── ollama.py
│   ├── tools/               # 工具系统
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── file_ops.py
│   │   └── shell.py
│   ├── skills/              # Skills 系统
│   │   ├── loader.py
│   │   └── builtin/
│   │       ├── coding.yml
│   │       ├── file_ops.yml
│   │       └── general.yml
│   ├── mcp/                 # MCP 支持
│   │   ├── client.py
│   │   └── adapter.py
│   └── vibe/                # Vibe Coding
│       ├── scanner.py
│       └── editor.py
├── tests/                   # 测试
├── docs/                    # 文档
├── pyproject.toml
├── README.md
├── README_CN.md
└── TEST_GUIDE.md
```

---

*文档版本: v1.0*
*最后更新: 2026-05-10*

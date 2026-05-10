# My Agent

自定义 AI Agent 实现，支持 Agent Loop。

[English](README.md) | 中文

## 功能特性

- CLI 交互界面，支持与 AI 对话
- Agent Loop 核心逻辑，支持工具调用
- 流式输出（打字机效果）
- Skills 系统（预定义任务模板）
- MCP（Model Context Protocol）支持外部工具服务器
- Vibe Coding 模式（交互式代码编辑）
- 多 LLM Provider 支持（OpenAI、DeepSeek、Anthropic、Ollama）
- 文件操作（读取、写入、列出目录）
- Shell 命令执行
- 可扩展的工具系统

## 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .
```

## 配置

设置要使用的 LLM Provider 的 API Key：

```bash
# DeepSeek（推荐）
export DEEPSEEK_API_KEY="your-deepseek-key"

# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"

# Ollama - 无需 API Key（本地运行）
```

## 使用方法

安装后可以直接使用 `agent` 命令（如果未安装，使用 `python -m src.agent.main` 替代）：

```bash
# 查看可用 Provider
agent providers

# 交互式聊天模式（默认：openai）
agent chat --provider deepseek

# 单次查询
agent ask "什么是 Python？" --provider deepseek

# 启用工具
agent chat --provider deepseek --enable-tools

# 指定模型
agent ask "你好" --provider deepseek --model deepseek-v4-flash

# 流式输出（打字机效果）
agent ask "你好" --provider deepseek --stream
agent chat --provider deepseek --stream --enable-tools

# 查看可用 Skills
agent skills

# 运行 Skill
agent run-skill explain "什么是递归" --provider deepseek --stream
agent run-skill review_code "src/main.py" --provider deepseek

# 查看 MCP 服务器
agent mcp-servers

# 使用 MCP 工具聊天
agent chat --provider deepseek --enable-mcp

# Vibe Coding 模式
agent vibe --task "添加用户认证功能" --provider deepseek
agent vibe --dir ./my-project --auto-apply
```

## 可用 Provider

| Provider | 环境变量 | 默认模型 |
|----------|----------|----------|
| OpenAI | `OPENAI_API_KEY` | gpt-4 |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-v4-flash |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| Ollama | （无） | llama3 |

## Skills 系统

### 工作原理

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

### 内置 Skills

**编程相关（CODING）**

| Skill | 描述 | 工具 |
|-------|------|------|
| `explain_code` | 解释代码功能 | read_file |
| `review_code` | 代码审查 | read_file |
| `refactor_code` | 重构建议 | read_file, write_file |
| `write_tests` | 编写单元测试 | read_file, write_file |
| `fix_bug` | 修复 Bug | read_file, write_file, shell |

**文件操作（FILE）**

| Skill | 描述 | 工具 |
|-------|------|------|
| `read_summary` | 读取并总结文件 | read_file |
| `find_files` | 查找文件 | list_directory, shell |
| `create_file` | 创建文件 | write_file |
| `compare_files` | 比较文件差异 | read_file, shell |

**通用（GENERAL）**

| Skill | 描述 | 工具 |
|-------|------|------|
| `explain` | 解释概念 | - |
| `brainstorm` | 头脑风暴 | - |
| `summarize` | 总结内容 | read_file |
| `translate` | 翻译文本 | - |
| `format_text` | 格式化文本 | - |

### 创建自定义 Skill

在 `src/agent/skills/builtin/` 目录创建 YAML 文件：

```yaml
skills:
  - name: my_skill
    description: "我的自定义技能"
    category: custom
    prompt: "你的提示词模板："
    tools:
      - read_file
    examples:
      - "my_skill 示例任务"
```

## MCP（Model Context Protocol）支持

### 什么是 MCP？

MCP 是一种协议，允许 AI 模型连接到外部工具服务器。支持的工具包括：
- 文件系统操作
- GitHub 集成
- 网页搜索
- 数据库访问
- 等等...

### 工作原理

```
用户请求
    ↓
启用 MCP 的 Agent
    ↓
MCP Client 连接服务器
    ↓
发现可用工具
    ↓
调用工具
    ↓
返回结果
```

### 配置

在项目根目录创建 `mcp_config.json`：

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

### 使用方法

```bash
# 查看配置的 MCP 服务器
agent mcp-servers

# 使用 MCP 工具聊天
agent chat --provider deepseek --enable-mcp

# 使用 MCP 工具查询
agent ask "列出 /path 目录的文件" --provider deepseek --enable-mcp
```

### 可用 MCP 服务器

| 服务器 | 描述 |
|--------|------|
| `@modelcontextprotocol/server-filesystem` | 文件系统操作 |
| `@modelcontextprotocol/server-github` | GitHub 集成 |
| `@modelcontextprotocol/server-brave-search` | 网页搜索 |
| `@modelcontextprotocol/server-memory` | 知识图谱 |

## Vibe Coding

### 什么是 Vibe Coding？

Vibe Coding 是一种交互式代码编辑模式，让你用自然语言描述修改，由 AI 来实现。

### 工作原理

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

### 使用方法

```bash
# 启动 Vibe Coding 模式
agent vibe --provider deepseek

# 带初始任务
agent vibe --task "添加用户认证功能" --provider deepseek

# 指定项目目录
agent vibe --dir ./my-project --provider deepseek

# 自动应用修改
agent vibe --task "重构数据库模块" --provider deepseek --auto-apply
```

### 功能特点

- **项目扫描**：自动扫描项目结构和编程语言
- **上下文收集**：收集相关文件作为 AI 上下文
- **交互式编辑**：用自然语言描述修改
- **自动应用**：可选择自动应用修改

## 项目结构

```
my-agent/
├── src/agent/              # 主要源代码
│   ├── main.py            # CLI 入口
│   ├── agent_loop.py      # Agent Loop 核心
│   ├── conversation.py    # 会话管理
│   ├── providers/         # LLM Provider
│   │   ├── base.py        # Provider 基类
│   │   ├── openai.py      # OpenAI Provider
│   │   ├── deepseek.py    # DeepSeek Provider
│   │   ├── anthropic.py   # Anthropic Provider
│   │   └── ollama.py      # Ollama Provider
│   ├── tools/             # 工具实现
│   │   ├── base.py        # Tool 基类
│   │   ├── registry.py    # 工具注册表
│   │   ├── file_ops.py    # 文件操作
│   │   └── shell.py       # Shell 命令
│   ├── skills/            # Skills 系统
│   │   ├── loader.py      # Skill 加载器
│   │   └── builtin/       # 内置 Skills
│   │       ├── coding.yml
│   │       ├── file_ops.yml
│   │       └── general.yml
│   ├── mcp/               # MCP 支持
│   │   ├── client.py      # MCP 客户端
│   │   └── adapter.py     # MCP 工具适配器
│   └── vibe/              # Vibe Coding
│       ├── scanner.py     # 项目扫描器
│       └── editor.py      # 代码编辑器
├── tests/                 # 单元测试
├── docs/                  # 文档
├── mcp_config.example.json # MCP 配置示例
├── pyproject.toml         # 项目配置
├── README.md              # 英文说明
└── README_CN.md           # 中文说明（本文件）
```

## 开发

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_agent.py -v

# 运行覆盖率报告
python -m pytest --cov=src --cov-report=term-missing
```

## 测试

详见 [TEST_GUIDE.md](TEST_GUIDE.md) 获取详细测试说明。

快速测试：
```bash
# 单元测试（无需 API Key）
python -m pytest tests/ -v

# 集成测试（需要 API Key）
python -m src.agent.main ask "你好" --provider deepseek

# 测试 Skills
python -m src.agent.main skills
python -m src.agent.main run-skill explain "什么是递归" --provider deepseek

# 测试 Vibe Coding
python -m src.agent.main vibe --task "列出项目结构" --provider deepseek
```

## 许可证

MIT

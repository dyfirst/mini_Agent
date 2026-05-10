# 测试指南

本文档详细说明如何测试 My Agent 项目的各个功能模块。

## 目录

1. [环境准备](#1-环境准备)
2. [单元测试](#2-单元测试)
3. [CLI 功能测试](#3-cli-功能测试)
4. [Agent Loop 测试](#4-agent-loop-测试)
5. [工具系统测试](#5-工具系统测试)
6. [集成测试](#6-集成测试)
7. [故障排查](#7-故障排查)

---

## 1. 环境准备

### 1.1 安装依赖

```bash
# 进入项目目录
cd my-agent

# 创建虚拟环境（如果还没有）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装项目依赖
pip install click rich openai pytest pytest-asyncio anthropic

# 或者以开发模式安装
pip install -e .
```

### 1.2 配置 API Key

根据使用的 LLM Provider 设置对应的 API Key：

```bash
# OpenAI
# Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key-here"
# Windows CMD:
set OPENAI_API_KEY=your-api-key-here
# Linux/Mac:
export OPENAI_API_KEY="your-api-key-here"

# DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"
```

**注意**：如果没有 API Key，可以跳过需要 API 调用的测试，只测试本地功能。

---

## 2. 单元测试

### 2.1 运行所有测试

```bash
# 运行所有测试
python -m pytest

# 运行测试并显示详细输出
python -m pytest -v

# 运行测试并显示打印输出
python -m pytest -s
```

**预期输出**：
```
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-7.4.4
collected 16 items

tests/test_agent.py::TestConversation::test_add_messages PASSED          [  6%]
tests/test_agent.py::TestConversation::test_clear_conversation PASSED    [ 12%]
tests/test_agent.py::TestToolRegistry::test_register_tool PASSED         [ 18%]
tests/test_agent.py::TestToolRegistry::test_get_tool_definitions PASSED  [ 25%]
tests/test_agent_loop.py::test_basic_agent SKIPPED                       [ 31%]
tests/test_agent_loop.py::test_agent_with_tools SKIPPED                  [ 37%]
tests/test_conversation.py::test_basic_conversation PASSED               [ 43%]
tests/test_conversation.py::test_clear_conversation PASSED               [ 50%]
tests/test_file_tools.py::test_write_and_read PASSED                     [ 56%]
tests/test_file_tools.py::test_list_directory PASSED                     [ 62%]
tests/test_file_tools.py::test_read_nonexistent PASSED                   [ 68%]
tests/test_registry.py::test_register_tools PASSED                       [ 75%]
tests/test_registry.py::test_get_definitions PASSED                      [ 81%]
tests/test_shell_tool.py::test_basic_command PASSED                      [ 87%]
tests/test_shell_tool.py::test_list_command PASSED                       [ 93%]
tests/test_shell_tool.py::test_timeout PASSED                            [100%]

======================== 14 passed, 2 skipped in 1.81s ========================
```

### 2.2 运行特定测试

```bash
# 运行特定测试文件
python -m pytest tests/test_agent.py

# 运行特定测试类
python -m pytest tests/test_agent.py::TestConversation

# 运行特定测试方法
python -m pytest tests/test_agent.py::TestConversation::test_add_messages

# 按关键字过滤
python -m pytest -k "conversation"
```

### 2.3 查看测试覆盖率

```bash
# 安装覆盖率工具
pip install pytest-cov

# 运行测试并生成覆盖率报告
python -m pytest --cov=src --cov-report=term-missing

# 生成 HTML 覆盖率报告
python -m pytest --cov=src --cov-report=html
```

---

## 3. CLI 功能测试

### 3.1 查看帮助信息

```bash
# 查看主帮助
python -m src.agent.main --help
```

**预期输出**：
```
Usage: python -m src.agent.main [OPTIONS] COMMAND [ARGS]...

  My Agent - AI Agent with Agent Loop

  A CLI tool for interacting with AI models using Agent Loop.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  ask        Execute a single query
  chat       Start interactive chat mode
  providers  List available LLM providers
  version    Show version information
```

### 3.2 查看版本信息

```bash
python -m src.agent.main version
```

**预期输出**：
```
My Agent v0.1.0
```

### 3.3 查看可用 Provider

```bash
python -m src.agent.main providers
```

**预期输出**：
```
Available LLM Providers:

  openai - OpenAI
    Default model: gpt-4
    [X] API Key not set

  deepseek - DeepSeek
    Default model: deepseek-chat
    [X] API Key not set

  anthropic - Anthropic
    Default model: claude-sonnet-4-20250514
    [X] API Key not set

  ollama - Ollama (Local)
    Default model: llama3
    No API key required
```

### 3.4 查看子命令帮助

```bash
# 查看 chat 命令帮助
python -m src.agent.main chat --help
```

**预期输出**：
```
Usage: python -m src.agent.main chat [OPTIONS]

  Start interactive chat mode

Options:
  -p, --provider TEXT  LLM provider (openai, deepseek, anthropic, ollama)
  -m, --model TEXT     Model to use (uses provider default if not specified)
  -t, --enable-tools   Enable tool calling
  --help               Show this message and exit.
```

### 3.5 测试单次查询（需要 API Key）

```bash
# 使用 OpenAI
python -m src.agent.main ask "What is Python?" --provider openai

# 使用 DeepSeek
python -m src.agent.main ask "What is Python?" --provider deepseek

# 使用 Anthropic
python -m src.agent.main ask "What is Python?" --provider anthropic

# 使用 Ollama 本地模型
python -m src.agent.main ask "What is Python?" --provider ollama

# 启用工具
python -m src.agent.main ask "List files in current directory" --provider openai --enable-tools
```

### 3.6 测试交互式聊天（需要 API Key）

```bash
# 启动交互式聊天
python -m src.agent.main chat --provider deepseek

# 启用工具的聊天
python -m src.agent.main chat --provider openai --enable-tools
```

---

## 4. Agent Loop 测试

### 4.1 测试 Conversation 类

```bash
# 运行测试
python -m pytest tests/test_conversation.py -v
```

**预期输出**：
```
tests/test_conversation.py::test_basic_conversation PASSED
tests/test_conversation.py::test_clear_conversation PASSED
```

### 4.2 测试 ToolRegistry 类

```bash
# 运行测试
python -m pytest tests/test_registry.py -v
```

**预期输出**：
```
tests/test_registry.py::test_register_tools PASSED
tests/test_registry.py::test_get_definitions PASSED
```

---

## 5. 工具系统测试

### 5.1 测试文件操作工具

```bash
# 运行测试
python -m pytest tests/test_file_tools.py -v
```

**预期输出**：
```
tests/test_file_tools.py::test_write_and_read PASSED
tests/test_file_tools.py::test_list_directory PASSED
tests/test_file_tools.py::test_read_nonexistent PASSED
```

### 5.2 测试 Shell 工具

```bash
# 运行测试
python -m pytest tests/test_shell_tool.py -v
```

**预期输出**：
```
tests/test_shell_tool.py::test_basic_command PASSED
tests/test_shell_tool.py::test_list_command PASSED
tests/test_shell_tool.py::test_timeout PASSED
```

---

## 6. 集成测试

### 6.1 测试完整 Agent Loop（需要 API Key）

```bash
# 运行 Agent Loop 测试
python -m pytest tests/test_agent_loop.py -v
```

**预期输出**（有 API Key）：
```
tests/test_agent_loop.py::test_basic_agent PASSED
tests/test_agent_loop.py::test_agent_with_tools PASSED
```

**预期输出**（无 API Key）：
```
tests/test_agent_loop.py::test_basic_agent SKIPPED
tests/test_agent_loop.py::test_agent_with_tools SKIPPED
```

### 6.2 测试 CLI 集成（需要 API Key）

```bash
# 测试单次查询
python -m src.agent.main ask "What is Python?" --provider deepseek

# 测试带工具的查询
python -m src.agent.main ask "List files in current directory" --provider openai --enable-tools

# 测试交互式聊天
python -m src.agent.main chat --provider deepseek --enable-tools
```

---

## 7. 故障排查

### 7.1 常见问题

#### 问题：ModuleNotFoundError

```
ModuleNotFoundError: No module named 'src'
```

**解决方案**：
```bash
# 确保在项目根目录运行
cd my-agent

# 或者设置 PYTHONPATH
set PYTHONPATH=%CD%  # Windows
export PYTHONPATH=$(pwd)  # Linux/Mac
```

#### 问题：API Key 未设置

```
Error: OPENAI_API_KEY environment variable not set
```

**解决方案**：
```bash
# 设置对应的环境变量
export OPENAI_API_KEY="your-api-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

#### 问题：pytest 找不到测试

```
no tests ran in 0.00s
```

**解决方案**：
```bash
# 确保测试文件以 test_ 开头
# 确保测试函数以 test_ 开头
# 确保在项目根目录运行
python -m pytest tests/
```

#### 问题：异步测试未执行

```
PytestUnhandledCoroutineWarning
```

**解决方案**：
```bash
# 确保安装了 pytest-asyncio
pip install pytest-asyncio
```

---

## 8. 测试检查清单

### 8.1 基础功能

- [ ] 单元测试全部通过 (14 passed, 2 skipped)
- [ ] CLI 帮助信息正常显示
- [ ] 版本命令正常工作
- [ ] providers 命令显示所有 Provider
- [ ] 文件读写工具正常
- [ ] 目录列出工具正常
- [ ] Shell 工具正常

### 8.2 Agent 功能（需要 API Key）

- [ ] 基本对话正常
- [ ] 工具调用正常
- [ ] 多轮对话正常
- [ ] 错误处理正常
- [ ] 多 Provider 切换正常

### 8.3 Git 相关

- [x] Git 仓库已初始化
- [x] 有多次有意义的提交
- [x] 提交信息使用英文
- [x] .gitignore 配置正确

---

## 9. 测试文件汇总

项目测试文件位于 `tests/` 目录：

| 文件 | 用途 | 需要 API Key |
|------|------|--------------|
| `tests/test_agent.py` | Conversation 和 ToolRegistry 单元测试 | 否 |
| `tests/test_conversation.py` | Conversation 类详细测试 | 否 |
| `tests/test_registry.py` | ToolRegistry 类详细测试 | 否 |
| `tests/test_file_tools.py` | 文件操作工具测试 | 否 |
| `tests/test_shell_tool.py` | Shell 工具测试 | 否 |
| `tests/test_agent_loop.py` | 完整 Agent Loop 集成测试 | 是 |

---

## 10. 快速测试命令

```bash
# 1. 运行所有单元测试
python -m pytest tests/ -v

# 2. 测试 CLI
python -m src.agent.main version
python -m src.agent.main providers

# 3. 测试文件工具
python -m pytest tests/test_file_tools.py -v

# 4. 测试 Shell 工具
python -m pytest tests/test_shell_tool.py -v

# 5. 测试完整 Agent（需要 API Key）
python -m pytest tests/test_agent_loop.py -v

# 6. 测试聊天功能（需要 API Key）
python -m src.agent.main ask "Hello" --provider deepseek
```

---

*文档创建时间：2026-05-10*
*最后更新：2026-05-10*
*项目版本：v0.1.0*

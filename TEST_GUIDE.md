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
pip install click rich openai pytest pytest-asyncio

# 或者以开发模式安装
pip install -e .
```

### 1.2 配置 API Key

```bash
# 设置 OpenAI API Key（测试 Agent Loop 需要）
# Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key-here"

# Windows CMD:
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac:
export OPENAI_API_KEY="your-api-key-here"
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
collected 4 items

tests/test_agent.py::TestConversation::test_add_messages PASSED          [ 25%]
tests/test_agent.py::TestConversation::test_clear_conversation PASSED    [ 50%]
tests/test_agent.py::TestToolRegistry::test_register_tool PASSED         [ 75%]
tests/test_agent.py::TestToolRegistry::test_get_tool_definitions PASSED  [100%]

============================== 4 passed in 1.22s ==============================
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

**预期输出**：
```
---------- coverage: platform win32, python 3.12.8 ----------
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
src/agent/__init__.py             2      0   100%
src/agent/agent_loop.py          45     10    78%   45-55
src/agent/conversation.py        35      2    94%   67, 72
src/agent/main.py                60     15    75%   85-100
src/agent/providers/__init__.py   4      0   100%
src/agent/providers/base.py      20      5    75%   30-35
src/agent/providers/openai.py    40     20    50%   25-45
src/agent/tools/__init__.py       8      0   100%
src/agent/tools/base.py          15      3    80%   25-28
src/agent/tools/file_ops.py      60     10    83%   45-55
src/agent/tools/registry.py      35      5    86%   55-60
src/agent/tools/shell.py         30      8    73%   40-48
-----------------------------------------------------------
TOTAL                           354     78    78%
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
  ask      Execute a single query
  chat     Start interactive chat mode
  version  Show version information
```

### 3.2 查看版本信息

```bash
python -m src.agent.main version
```

**预期输出**：
```
My Agent v0.1.0
```

### 3.3 查看子命令帮助

```bash
# 查看 chat 命令帮助
python -m src.agent.main chat --help
```

**预期输出**：
```
Usage: python -m src.agent.main chat [OPTIONS]

  Start interactive chat mode

Options:
  -m, --model TEXT       Model to use  [default: gpt-4]
  -t, --enable-tools     Enable tool calling
  --help                 Show this message and exit.
```

```bash
# 查看 ask 命令帮助
python -m src.agent.main ask --help
```

**预期输出**：
```
Usage: python -m src.agent.main ask [OPTIONS] PROMPT

  Execute a single query

Options:
  -m, --model TEXT       Model to use  [default: gpt-4]
  -t, --enable-tools     Enable tool calling
  --help                 Show this message and exit.
```

### 3.4 测试单次查询（需要 API Key）

```bash
# 基本查询
python -m src.agent.main ask "What is Python?"

# 指定模型
python -m src.agent.main ask "What is Python?" --model gpt-3.5-turbo

# 启用工具
python -m src.agent.main ask "List files in current directory" --enable-tools
```

**预期行为**：
- 显示查询内容
- 调用 API 获取响应
- 显示格式化的响应

### 3.5 测试交互式聊天（需要 API Key）

```bash
# 启动交互式聊天
python -m src.agent.main chat

# 启用工具的聊天
python -m src.agent.main chat --enable-tools
```

**测试步骤**：
1. 启动聊天
2. 输入消息，按 Enter
3. 查看响应
4. 输入 `exit` 或 `quit` 退出

**预期行为**：
```
╭─────────────────────────────────────────────────╮
│ My Agent - Interactive Chat                     │
│ Type 'exit' or 'quit' to end the conversation  │
╰─────────────────────────────────────────────────╯

You: Hello

Agent:
Hello! How can I help you today?

You: exit

Goodbye!
```

---

## 4. Agent Loop 测试

### 4.1 测试 Conversation 类

创建测试脚本 `test_conversation.py`：

```python
"""测试 Conversation 类"""
from src.agent.conversation import Conversation, Message

def test_basic_conversation():
    """测试基本会话功能"""
    # 创建会话
    conv = Conversation(system_prompt="You are a helpful assistant")

    # 添加消息
    conv.add_user_message("Hello")
    conv.add_assistant_message("Hi there!")
    conv.add_tool_result("tool_123", "Tool result")

    # 验证消息
    messages = conv.get_messages_for_api()

    print(f"消息数量: {len(messages)}")
    print(f"消息类型: {[m['role'] for m in messages]}")

    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "tool"

    print("✅ 基本会话测试通过")

def test_clear_conversation():
    """测试清空会话"""
    conv = Conversation(system_prompt="System prompt")
    conv.add_user_message("Hello")
    conv.add_assistant_message("Hi")

    conv.clear()

    messages = conv.get_messages_for_api()
    assert len(messages) == 1
    assert messages[0]["role"] == "system"

    print("✅ 清空会话测试通过")

if __name__ == "__main__":
    test_basic_conversation()
    test_clear_conversation()
    print("\n✅ 所有 Conversation 测试通过")
```

**运行测试**：
```bash
python test_conversation.py
```

**预期输出**：
```
消息数量: 4
消息类型: ['system', 'user', 'assistant', 'tool']
✅ 基本会话测试通过
✅ 清空会话测试通过

✅ 所有 Conversation 测试通过
```

### 4.2 测试 ToolRegistry 类

创建测试脚本 `test_registry.py`：

```python
"""测试 ToolRegistry 类"""
from src.agent.tools import ToolRegistry, ReadFileTool, WriteFileTool

def test_register_tools():
    """测试工具注册"""
    registry = ToolRegistry()

    # 注册工具
    registry.register("read_file", ReadFileTool())
    registry.register("write_file", WriteFileTool())

    print(f"已注册工具: {registry.tool_names}")
    print(f"工具数量: {len(registry)}")

    assert "read_file" in registry
    assert "write_file" in registry
    assert len(registry) == 2

    print("✅ 工具注册测试通过")

def test_get_definitions():
    """测试获取工具定义"""
    registry = ToolRegistry()
    registry.register("read_file", ReadFileTool())

    definitions = registry.get_tool_definitions()

    print(f"工具定义数量: {len(definitions)}")
    print(f"工具名称: {definitions[0]['function']['name']}")

    assert len(definitions) == 1
    assert definitions[0]["function"]["name"] == "read_file"

    print("✅ 工具定义测试通过")

if __name__ == "__main__":
    test_register_tools()
    test_get_definitions()
    print("\n✅ 所有 ToolRegistry 测试通过")
```

**运行测试**：
```bash
python test_registry.py
```

**预期输出**：
```
已注册工具: ['read_file', 'write_file']
工具数量: 2
✅ 工具注册测试通过
工具定义数量: 1
工具名称: read_file
✅ 工具定义测试通过

✅ 所有 ToolRegistry 测试通过
```

---

## 5. 工具系统测试

### 5.1 测试文件操作工具

创建测试脚本 `test_file_tools.py`：

```python
"""测试文件操作工具"""
import asyncio
import os
from src.agent.tools import ReadFileTool, WriteFileTool, ListDirectoryTool

async def test_write_and_read():
    """测试写入和读取文件"""
    write_tool = WriteFileTool()
    read_tool = ReadFileTool()

    test_file = "test_output.txt"
    test_content = "Hello, this is a test file!"

    # 写入文件
    result = await write_tool.execute(path=test_file, content=test_content)
    print(f"写入结果: {result}")

    # 读取文件
    content = await read_tool.execute(path=test_file)
    print(f"读取内容: {content}")

    # 验证
    assert content == test_content

    # 清理
    os.remove(test_file)

    print("✅ 文件写入/读取测试通过")

async def test_list_directory():
    """测试列出目录"""
    list_tool = ListDirectoryTool()

    result = await list_tool.execute(path=".")
    print(f"目录内容:\n{result}")

    assert "src" in result
    assert "tests" in result

    print("✅ 目录列出测试通过")

async def test_read_nonexistent():
    """测试读取不存在的文件"""
    read_tool = ReadFileTool()

    result = await read_tool.execute(path="nonexistent.txt")
    print(f"错误信息: {result}")

    assert "Error" in result or "not found" in result

    print("✅ 读取不存在文件测试通过")

if __name__ == "__main__":
    asyncio.run(test_write_and_read())
    asyncio.run(test_list_directory())
    asyncio.run(test_read_nonexistent())
    print("\n✅ 所有文件工具测试通过")
```

**运行测试**：
```bash
python test_file_tools.py
```

**预期输出**：
```
写入结果: Successfully wrote to test_output.txt
读取内容: Hello, this is a test file!
✅ 文件写入/读取测试通过
目录内容:
Contents of .:

Directories:
  📁 src/
  📁 tests/
  📁 docs/
  📁 venv/

Files:
  📄 pyproject.toml (596 bytes)
  📄 README.md (1240 bytes)
  📄 CLAUDE.md (1756 bytes)
✅ 目录列出测试通过
错误信息: Error: File not found: nonexistent.txt
✅ 读取不存在文件测试通过

✅ 所有文件工具测试通过
```

### 5.2 测试 Shell 工具

创建测试脚本 `test_shell_tool.py`：

```python
"""测试 Shell 工具"""
import asyncio
from src.agent.tools import ShellTool

async def test_basic_command():
    """测试基本命令执行"""
    shell = ShellTool()

    # 测试 echo 命令
    result = await shell.execute(command="echo Hello World")
    print(f"Echo 结果: {result}")

    assert "Hello World" in result

    print("✅ 基本命令测试通过")

async def test_list_command():
    """测试列表命令"""
    shell = ShellTool()

    # 测试 dir 命令（Windows）或 ls 命令（Linux/Mac）
    result = await shell.execute(command="dir")
    print(f"Dir 结果:\n{result[:200]}...")  # 只显示前200字符

    assert "src" in result or "tests" in result

    print("✅ 列表命令测试通过")

async def test_timeout():
    """测试命令超时"""
    shell = ShellTool(timeout=1)  # 1秒超时

    # 测试一个会超时的命令
    result = await shell.execute(command="ping -n 10 127.0.0.1")
    print(f"超时结果: {result}")

    # 注意：这个测试可能需要调整，取决于系统
    print("✅ 超时测试完成")

if __name__ == "__main__":
    asyncio.run(test_basic_command())
    asyncio.run(test_list_command())
    # asyncio.run(test_timeout())  # 可选：取消注释以测试超时
    print("\n✅ 所有 Shell 工具测试通过")
```

**运行测试**：
```bash
python test_shell_tool.py
```

**预期输出**：
```
Echo 结果: Hello World

✅ 基本命令测试通过
Dir 结果:
 Volume in drive C is Windows
 Volume Serial Number is XXXX-XXXX

 Directory of C:\Users\DY\Desktop\0510-2\my-agent

05/10/2026  09:42 AM    <DIR>          .
05/10/2026  09:42 AM    <DIR>          ..
05/10/2026  09:42 AM    <DIR>          src
05/10/2026  09:42 AM    <DIR>          tests
05/10/2026  09:42 AM    <DIR>          docs
...
✅ 列表命令测试通过

✅ 所有 Shell 工具测试通过
```

---

## 6. 集成测试

### 6.1 测试完整 Agent Loop（需要 API Key）

创建测试脚本 `test_agent_loop.py`：

```python
"""测试完整 Agent Loop"""
import asyncio
import os
from src.agent.agent_loop import AgentLoop
from src.agent.providers.openai import OpenAIProvider
from src.agent.tools import ToolRegistry, ReadFileTool, ListDirectoryTool, ShellTool

async def test_basic_agent():
    """测试基本 Agent 功能"""
    # 检查 API Key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  跳过测试：OPENAI_API_KEY 未设置")
        return

    # 创建 Provider
    provider = OpenAIProvider(api_key=api_key, model="gpt-3.5-turbo")

    # 创建 Agent
    agent = AgentLoop(
        provider=provider,
        system_prompt="You are a helpful assistant. Keep responses concise.",
    )

    # 测试简单对话
    response = await agent.run("What is 2+2?")
    print(f"问题: What is 2+2?")
    print(f"回答: {response}")

    assert "4" in response

    print("✅ 基本 Agent 测试通过")

async def test_agent_with_tools():
    """测试带工具的 Agent"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  跳过测试：OPENAI_API_KEY 未设置")
        return

    # 创建 Provider
    provider = OpenAIProvider(api_key=api_key, model="gpt-3.5-turbo")

    # 创建工具
    tools = ToolRegistry()
    tools.register("list_directory", ListDirectoryTool())
    tools.register("read_file", ReadFileTool())
    tools.register("shell", ShellTool())

    # 创建 Agent
    agent = AgentLoop(
        provider=provider,
        tools=tools,
        system_prompt="You are a helpful assistant with access to file tools. Use them when appropriate.",
    )

    # 测试工具调用
    response = await agent.run("List files in the current directory")
    print(f"问题: List files in the current directory")
    print(f"回答:\n{response}")

    assert "src" in response or "tests" in response

    print("✅ Agent 工具调用测试通过")

if __name__ == "__main__":
    asyncio.run(test_basic_agent())
    asyncio.run(test_agent_with_tools())
    print("\n✅ 所有 Agent Loop 测试完成")
```

**运行测试**：
```bash
python test_agent_loop.py
```

**预期输出**（有 API Key）：
```
问题: What is 2+2?
回答: 2 + 2 equals 4.
✅ 基本 Agent 测试通过
问题: List files in the current directory
回答:
I'll list the files in the current directory for you.

Contents of .:

Directories:
  📁 src/
  📁 tests/
  📁 docs/
  📁 venv/

Files:
  📄 pyproject.toml (596 bytes)
  📄 README.md (1240 bytes)
  📄 CLAUDE.md (1756 bytes)
✅ Agent 工具调用测试通过

✅ 所有 Agent Loop 测试完成
```

**预期输出**（无 API Key）：
```
⚠️  跳过测试：OPENAI_API_KEY 未设置
⚠️  跳过测试：OPENAI_API_KEY 未设置

✅ 所有 Agent Loop 测试完成
```

### 6.2 测试 CLI 集成（需要 API Key）

```bash
# 测试单次查询
python -m src.agent.main ask "What is Python?" --model gpt-3.5-turbo

# 测试带工具的查询
python -m src.agent.main ask "List files in current directory" --enable-tools

# 测试交互式聊天
python -m src.agent.main chat --enable-tools
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

#### 问题：OPENAI_API_KEY 未设置

```
Error: OPENAI_API_KEY environment variable not set
```

**解决方案**：
```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key"
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

### 7.2 调试技巧

#### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 使用 pdb 调试

```python
import pdb; pdb.set_trace()  # 在代码中设置断点
```

#### 查看工具定义

```python
from src.agent.tools import ToolRegistry, ReadFileTool

registry = ToolRegistry()
registry.register("read_file", ReadFileTool())

import json
print(json.dumps(registry.get_tool_definitions(), indent=2))
```

---

## 8. 测试检查清单

### 8.1 基础功能

- [ ] 单元测试全部通过
- [ ] CLI 帮助信息正常显示
- [ ] 版本命令正常工作
- [ ] 文件读写工具正常
- [ ] 目录列出工具正常
- [ ] Shell 工具正常

### 8.2 Agent 功能（需要 API Key）

- [ ] 基本对话正常
- [ ] 工具调用正常
- [ ] 多轮对话正常
- [ ] 错误处理正常

### 8.3 Git 相关

- [ ] Git 仓库已初始化
- [ ] 有多次有意义的提交
- [ ] 提交信息使用英文
- [ ] .gitignore 配置正确

---

## 9. 测试脚本汇总

项目包含以下测试脚本：

| 脚本 | 用途 | 是否需要 API Key |
|------|------|------------------|
| `tests/test_agent.py` | 单元测试 | 否 |
| `test_conversation.py` | Conversation 测试 | 否 |
| `test_registry.py` | ToolRegistry 测试 | 否 |
| `test_file_tools.py` | 文件工具测试 | 否 |
| `test_shell_tool.py` | Shell 工具测试 | 否 |
| `test_agent_loop.py` | Agent Loop 测试 | 是 |

---

## 10. 快速测试命令

```bash
# 1. 运行所有单元测试
python -m pytest -v

# 2. 测试 CLI
python -m src.agent.main version

# 3. 测试文件工具（快速）
python test_file_tools.py

# 4. 测试 Shell 工具（快速）
python test_shell_tool.py

# 5. 测试完整 Agent（需要 API Key）
python test_agent_loop.py
```

---

*文档创建时间：2026-05-10*
*项目版本：v0.1.0*

# 测试指南

本文档详细说明如何测试 My Agent 项目的各个功能模块。

## 目录

1. [环境准备](#1-环境准备)
2. [单元测试](#2-单元测试)
3. [CLI 功能测试](#3-cli-功能测试)
4. [Agent Loop 测试](#4-agent-loop-测试)
5. [工具系统测试](#5-工具系统测试)
6. [Skills 系统测试](#6-skills-系统测试)
7. [集成测试](#7-集成测试)
8. [故障排查](#8-故障排查)

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
pip install -e .
```

### 1.2 配置 API Key

根据使用的 LLM Provider 设置对应的 API Key：

```bash
# DeepSeek (推荐)
# Windows PowerShell:
$env:DEEPSEEK_API_KEY="your-deepseek-key"
# Windows CMD:
set DEEPSEEK_API_KEY=your-deepseek-key
# Linux/Mac:
export DEEPSEEK_API_KEY="your-deepseek-key"

# OpenAI
export OPENAI_API_KEY="your-openai-key"

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

---

## 3. CLI 功能测试

### 3.1 查看帮助信息

```bash
python -m src.agent.main --help
```

**预期输出**：
```
Usage: python -m src.agent.main [OPTIONS] COMMAND [ARGS]...

  My Agent - AI Agent with Agent Loop

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  ask        Execute a single query
  chat       Start interactive chat mode
  providers  List available LLM providers
  run-skill  Run a skill with the given task
  skills     List available skills
  version    Show version information
```

### 3.2 查看版本信息

```bash
python -m src.agent.main version
```

**预期输出**：
```
My Agent v0.3.0
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
    Default model: deepseek-v4-flash
    [OK] API Key set

  anthropic - Anthropic
    Default model: claude-sonnet-4-20250514
    [X] API Key not set

  ollama - Ollama (Local)
    Default model: llama3
    No API key required
```

### 3.4 测试单次查询（需要 API Key）

```bash
# 使用 DeepSeek
python -m src.agent.main ask "What is Python?" --provider deepseek

# 使用流式输出
python -m src.agent.main ask "What is Python?" --provider deepseek --stream
```

### 3.5 测试交互式聊天（需要 API Key）

```bash
# 启动交互式聊天
python -m src.agent.main chat --provider deepseek

# 启用工具和流式输出
python -m src.agent.main chat --provider deepseek --enable-tools --stream
```

---

## 4. Agent Loop 测试

### 4.1 测试 Conversation 类

```bash
python -m pytest tests/test_conversation.py -v
```

**预期输出**：
```
tests/test_conversation.py::test_basic_conversation PASSED
tests/test_conversation.py::test_clear_conversation PASSED
```

### 4.2 测试 ToolRegistry 类

```bash
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
python -m pytest tests/test_shell_tool.py -v
```

**预期输出**：
```
tests/test_shell_tool.py::test_basic_command PASSED
tests/test_shell_tool.py::test_list_command PASSED
tests/test_shell_tool.py::test_timeout PASSED
```

---

## 6. Skills 系统测试

### 6.1 Skills 系统逻辑

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

### 6.2 列出可用 Skills

```bash
python -m src.agent.main skills
```

**预期输出**：
```
Available Skills:

CODING
  explain_code - Explain what a piece of code does
    Example: explain_code src/main.py
  review_code - Review code for potential issues and improvements
    Example: review_code src/main.py
  refactor_code - Suggest refactoring improvements for code
    Example: refactor_code src/utils.py
  write_tests - Write unit tests for code
    Example: write_tests src/calculator.py
  fix_bug - Help fix a bug in code
    Example: fix_bug the TypeError in main.py

FILE
  read_summary - Read and summarize a file
    Example: read_summary README.md
  find_files - Find files matching a pattern
    Example: find_files all Python files
  create_file - Create a new file with specified content
    Example: create_file a new Python script
  compare_files - Compare two files and show differences
    Example: compare_files old.py and new.py

GENERAL
  explain - Explain a concept or topic
    Example: explain how HTTP works
  brainstorm - Brainstorm ideas on a topic
    Example: brainstorm features for a todo app
  summarize - Summarize text or content
    Example: summarize this article
  translate - Translate text between languages
    Example: translate to Chinese: Hello World
  format_text - Format text according to specified style
    Example: format_text as markdown
```

### 6.3 测试通用 Skills（不需要工具）

```bash
# 测试 explain skill
python -m src.agent.main run-skill explain "什么是递归" --provider deepseek

# 测试 translate skill
python -m src.agent.main run-skill translate "Hello World to Chinese" --provider deepseek

# 测试 brainstorm skill
python -m src.agent.main run-skill brainstorm "features for a todo app" --provider deepseek
```

### 6.4 测试文件 Skills（需要工具）

```bash
# 测试 read_summary skill
python -m src.agent.main run-skill read_summary "README.md" --provider deepseek

# 测试 find_files skill
python -m src.agent.main run-skill find_files "all Python files" --provider deepseek
```

### 6.5 测试编程 Skills（需要工具）

```bash
# 测试 explain_code skill
python -m src.agent.main run-skill explain_code "src/main.py" --provider deepseek

# 测试 review_code skill
python -m src.agent.main run-skill review_code "src/agent_loop.py" --provider deepseek
```

### 6.6 测试流式输出

```bash
python -m src.agent.main run-skill explain "什么是机器学习" --provider deepseek --stream
```

### 6.7 添加自定义 Skills

在 `src/agent/skills/builtin/` 目录创建 YAML 文件：

```yaml
# my_skills.yml
skills:
  - name: my_custom_skill
    description: "My custom skill"
    category: custom
    prompt: "Please do the following task:"
    tools:
      - read_file
    examples:
      - "my_custom_skill some task"
```

重新运行 `agent skills` 即可看到新 Skill。

---

## 6.8 Vibe Coding 测试

### Vibe Coding 工作原理

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

### 测试案例 1：创建包含当前时间的文件

```bash
# 使用 Vibe Coding 创建文件
python -m src.agent.main vibe --task "创建一个名为 datetime.txt 的文件，内容是当前日期和时间" --provider deepseek --auto-apply

# 验证文件
type datetime.txt
```

**预期行为**：
1. 扫描项目结构
2. AI 生成创建文件的代码
3. 自动创建 `datetime.txt` 文件
4. 文件内容包含当前日期和时间

### 测试案例 2：交互式编辑

```bash
# 启动 Vibe Coding 模式
python -m src.agent.main vibe --provider deepseek

# 输入任务
Vibe: 创建一个 hello.py 文件，打印 "Hello, World!"
Vibe: 修改 hello.py，添加当前时间显示
Vibe: exit
```

### 测试案例 3：指定目录

```bash
# 对指定目录进行操作
python -m src.agent.main vibe --dir ./my-project --task "列出所有 Python 文件" --provider deepseek
```

---

## 7. 集成测试

### 7.1 测试完整 Agent Loop（需要 API Key）

```bash
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

### 7.2 测试 CLI 集成（需要 API Key）

```bash
# 测试单次查询
python -m src.agent.main ask "What is Python?" --provider deepseek

# 测试带工具的查询
python -m src.agent.main ask "List files in current directory" --provider deepseek --enable-tools

# 测试 Skills
python -m src.agent.main run-skill explain "什么是递归" --provider deepseek --stream
```

---

## 8. 故障排查

### 8.1 常见问题

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
export DEEPSEEK_API_KEY="your-api-key"
```

#### 问题：PyYAML 未安装

```
ModuleNotFoundError: No module named 'yaml'
```

**解决方案**：
```bash
pip install pyyaml
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

# 3. 测试 Skills
python -m src.agent.main skills
python -m src.agent.main run-skill explain "什么是递归" --provider deepseek

# 4. 测试文件工具
python -m pytest tests/test_file_tools.py -v

# 5. 测试 Shell 工具
python -m pytest tests/test_shell_tool.py -v

# 6. 测试完整 Agent（需要 API Key）
python -m pytest tests/test_agent_loop.py -v

# 7. 测试聊天功能（需要 API Key）
python -m src.agent.main ask "Hello" --provider deepseek --stream

# 8. 测试 Skills 功能（需要 API Key）
python -m src.agent.main run-skill explain "什么是递归" --provider deepseek --stream
```

---

*文档创建时间：2026-05-10*
*最后更新：2026-05-10*
*项目版本：v0.3.0*

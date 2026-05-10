"""测试 Vibe Coding 功能"""
import pytest
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

from src.agent.vibe import ProjectScanner, VibeEditor


def test_project_scanner():
    """测试项目扫描器"""
    scanner = ProjectScanner(".")

    # 扫描项目
    result = scanner.scan()

    assert "root" in result
    assert "files" in result
    assert "file_count" in result
    assert "languages" in result
    assert "total_lines" in result

    # 应该找到一些文件
    assert result["file_count"] > 0
    assert result["total_lines"] > 0

    # 应该有 Python 文件
    assert ".py" in result["languages"]


def test_scanner_read_file():
    """测试读取文件"""
    scanner = ProjectScanner(".")

    # 读取 README
    content = scanner.read_file("README.md")
    assert len(content) > 0
    assert "My Agent" in content

    # 读取不存在的文件
    content = scanner.read_file("nonexistent.txt")
    assert "Error" in content


def test_scanner_get_relevant_files():
    """测试获取相关文件"""
    scanner = ProjectScanner(".")

    # 获取与 "agent" 相关的文件
    files = scanner.get_relevant_files("agent loop implementation")
    assert len(files) > 0

    # 应该包含 agent_loop.py
    agent_files = [f for f in files if "agent" in f.lower()]
    assert len(agent_files) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

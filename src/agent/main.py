"""CLI entry point for My Agent"""

import asyncio
import os
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

from .agent_loop import AgentLoop
from .conversation import Conversation
from .providers.openai import OpenAIProvider
from .providers.deepseek import DeepSeekProvider
from .providers.anthropic import AnthropicProvider
from .providers.ollama import OllamaProvider
from .providers.base import LLMProvider
from .tools import ToolRegistry, ReadFileTool, WriteFileTool, ListDirectoryTool, ShellTool

console = Console()

# Provider configuration
PROVIDER_CONFIG = {
    "openai": {
        "name": "OpenAI",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4",
        "provider_class": OpenAIProvider,
    },
    "deepseek": {
        "name": "DeepSeek",
        "env_key": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-v4-flash",
        "provider_class": DeepSeekProvider,
    },
    "anthropic": {
        "name": "Anthropic",
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-20250514",
        "provider_class": AnthropicProvider,
    },
    "ollama": {
        "name": "Ollama (Local)",
        "env_key": None,  # No API key needed
        "default_model": "llama3",
        "provider_class": OllamaProvider,
    },
}


def create_provider(provider_name: str, model: str = None) -> LLMProvider:
    """Create LLM provider based on provider name

    Args:
        provider_name: Provider name (openai, deepseek, anthropic, ollama)
        model: Model name (optional, uses default if not specified)

    Returns:
        LLMProvider instance
    """
    config = PROVIDER_CONFIG.get(provider_name)
    if not config:
        console.print(f"[red]Error: Unknown provider '{provider_name}'[/red]")
        console.print(f"[dim]Available providers: {', '.join(PROVIDER_CONFIG.keys())}[/dim]")
        raise click.Abort()

    # Get API key if needed
    api_key = None
    if config["env_key"]:
        api_key = os.environ.get(config["env_key"])
        if not api_key:
            console.print(f"[red]Error: {config['env_key']} environment variable not set[/red]")
            raise click.Abort()

    # Use default model if not specified
    if not model:
        model = config["default_model"]

    # Create provider
    try:
        if provider_name == "ollama":
            return config["provider_class"](model=model)
        elif api_key:
            return config["provider_class"](api_key=api_key, model=model)
        else:
            console.print(f"[red]Error: API key required for {config['name']}[/red]")
            raise click.Abort()
    except ImportError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


def create_agent(provider_name: str, model: str = None, enable_tools: bool = False) -> AgentLoop:
    """Create Agent instance with configured provider and tools

    Args:
        provider_name: Provider name
        model: Model name (optional)
        enable_tools: Whether to enable tool calling

    Returns:
        Configured AgentLoop instance
    """
    # Create provider
    provider = create_provider(provider_name, model)

    # Create tools if enabled
    tools = None
    if enable_tools:
        tools = ToolRegistry()
        tools.register("read_file", ReadFileTool())
        tools.register("write_file", WriteFileTool())
        tools.register("list_directory", ListDirectoryTool())
        tools.register("shell", ShellTool())

        console.print("[dim]Tools enabled: " + ", ".join(tools.tool_names) + "[/dim]")

    # Create agent
    system_prompt = """You are a helpful AI assistant. You can help with various tasks including:
- Answering questions
- Writing and editing code
- Working with files
- Executing commands

When using tools, explain what you're doing and why."""

    agent = AgentLoop(
        provider=provider,
        tools=tools,
        system_prompt=system_prompt,
    )

    return agent


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """My Agent - AI Agent with Agent Loop

    A CLI tool for interacting with AI models using Agent Loop.
    """
    pass


@cli.command()
@click.option("--provider", "-p", default="openai", help="LLM provider (openai, deepseek, anthropic, ollama)")
@click.option("--model", "-m", default=None, help="Model to use (uses provider default if not specified)")
@click.option("--enable-tools", "-t", is_flag=True, help="Enable tool calling")
def chat(provider: str, model: str, enable_tools: bool):
    """Start interactive chat mode"""
    console.print(
        Panel(
            f"[bold green]My Agent - Interactive Chat[/bold green]\n"
            f"[dim]Provider: {provider} | Type 'exit' or 'quit' to end[/dim]",
            title="Welcome",
        )
    )

    try:
        agent = create_agent(provider, model, enable_tools)
    except click.Abort:
        return

    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = console.input("\n[bold blue]You:[/bold blue] ")

            # Check for exit command
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("\n[yellow]Goodbye![/yellow]")
                break

            # Skip empty input
            if not user_input.strip():
                continue

            # Run agent
            console.print("\n[bold green]Agent:[/bold green]")
            response = asyncio.run(agent.run(user_input))

            # Display response
            console.print(Markdown(response))

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]")


@cli.command()
@click.argument("prompt")
@click.option("--provider", "-p", default="openai", help="LLM provider (openai, deepseek, anthropic, ollama)")
@click.option("--model", "-m", default=None, help="Model to use")
@click.option("--enable-tools", "-t", is_flag=True, help="Enable tool calling")
def ask(prompt: str, provider: str, model: str, enable_tools: bool):
    """Execute a single query"""
    console.print(f"[bold blue]Query:[/bold blue] {prompt}")
    console.print(f"[dim]Provider: {provider}[/dim]\n")

    try:
        agent = create_agent(provider, model, enable_tools)
    except click.Abort:
        return

    # Run agent
    try:
        response = asyncio.run(agent.run(prompt))
        console.print("\n[bold green]Response:[/bold green]")
        console.print(Markdown(response))
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
def providers():
    """List available LLM providers"""
    console.print("[bold]Available LLM Providers:[/bold]\n")

    for name, config in PROVIDER_CONFIG.items():
        env_status = ""
        if config["env_key"]:
            if os.environ.get(config["env_key"]):
                env_status = "[green][OK] API Key set[/green]"
            else:
                env_status = "[red][X] API Key not set[/red]"
        else:
            env_status = "[dim]No API key required[/dim]"

        console.print(f"  [bold]{name}[/bold] - {config['name']}")
        console.print(f"    Default model: {config['default_model']}")
        console.print(f"    {env_status}\n")


@cli.command()
def version():
    """Show version information"""
    console.print("[bold]My Agent[/bold] v0.1.0")


if __name__ == "__main__":
    cli()

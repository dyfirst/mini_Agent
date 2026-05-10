"""CLI entry point for My Agent"""

import asyncio
import os

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent_loop import AgentLoop
from .conversation import Conversation
from .providers.openai import OpenAIProvider
from .tools import ToolRegistry, ReadFileTool, WriteFileTool, ListDirectoryTool, ShellTool

console = Console()


def create_agent(model: str, enable_tools: bool) -> AgentLoop:
    """Create Agent instance with configured provider and tools

    Args:
        model: Model name to use
        enable_tools: Whether to enable tool calling

    Returns:
        Configured AgentLoop instance
    """
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        raise click.Abort()

    # Create provider
    provider = OpenAIProvider(api_key=api_key, model=model)

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
@click.option("--model", "-m", default="gpt-4", help="Model to use")
@click.option("--enable-tools", "-t", is_flag=True, help="Enable tool calling")
def chat(model: str, enable_tools: bool):
    """Start interactive chat mode"""
    console.print(
        Panel(
            "[bold green]My Agent - Interactive Chat[/bold green]\n"
            "[dim]Type 'exit' or 'quit' to end the conversation[/dim]",
            title="Welcome",
        )
    )

    try:
        agent = create_agent(model, enable_tools)
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
@click.option("--model", "-m", default="gpt-4", help="Model to use")
@click.option("--enable-tools", "-t", is_flag=True, help="Enable tool calling")
def ask(prompt: str, model: str, enable_tools: bool):
    """Execute a single query"""
    console.print(f"[bold blue]Query:[/bold blue] {prompt}")
    console.print(f"[dim]Using model: {model}[/dim]\n")

    try:
        agent = create_agent(model, enable_tools)
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
def version():
    """Show version information"""
    console.print("[bold]My Agent[/bold] v0.1.0")


if __name__ == "__main__":
    cli()

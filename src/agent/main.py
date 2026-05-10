"""CLI entry point for My Agent"""

import asyncio
import json
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
from .skills import SkillLoader
from .mcp import MCPClient, MCPToolAdapter

console = Console()

# Initialize skill loader
skill_loader = SkillLoader()

# Initialize MCP client
mcp_client = MCPClient()

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


def load_mcp_config(config_path: str = None):
    """Load MCP server configuration

    Args:
        config_path: Path to config file (default: mcp_config.json in project root)
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp_config.json")

    if not os.path.exists(config_path):
        return

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        for name, server_config in servers.items():
            command = server_config.get("command")
            args = server_config.get("args", [])
            env = server_config.get("env", {})

            if command:
                # Store for lazy loading
                mcp_client.servers[name] = None  # Placeholder

    except Exception as e:
        console.print(f"[yellow]Warning: Failed to load MCP config: {e}[/yellow]")


async def init_mcp_servers():
    """Initialize MCP servers from config"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp_config.json")

    if not os.path.exists(config_path):
        return

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        for name, server_config in servers.items():
            command = server_config.get("command")
            args = server_config.get("args", [])
            env = server_config.get("env", {})

            if command:
                console.print(f"[dim]Starting MCP server: {name}...[/dim]")
                success = await mcp_client.add_server(name, command, args, env)
                if success:
                    console.print(f"[green]MCP server '{name}' started with {len(mcp_client.servers[name].tools)} tools[/green]")
                else:
                    console.print(f"[yellow]Warning: Failed to start MCP server '{name}'[/yellow]")

    except Exception as e:
        console.print(f"[yellow]Warning: Failed to initialize MCP servers: {e}[/yellow]")


def create_agent(
    provider_name: str,
    model: str = None,
    enable_tools: bool = False,
    enable_mcp: bool = False,
) -> AgentLoop:
    """Create Agent instance with configured provider and tools

    Args:
        provider_name: Provider name
        model: Model name (optional)
        enable_tools: Whether to enable tool calling
        enable_mcp: Whether to enable MCP tools

    Returns:
        Configured AgentLoop instance
    """
    # Create provider
    provider = create_provider(provider_name, model)

    # Create tools if enabled
    tools = None
    if enable_tools or enable_mcp:
        tools = ToolRegistry()

        # Register built-in tools
        if enable_tools:
            tools.register("read_file", ReadFileTool())
            tools.register("write_file", WriteFileTool())
            tools.register("list_directory", ListDirectoryTool())
            tools.register("shell", ShellTool())

        # Register MCP tools
        if enable_mcp and mcp_client.tools:
            for tool_name, mcp_tool in mcp_client.tools.items():
                adapter = MCPToolAdapter(
                    tool_name=mcp_tool.name,
                    tool_description=mcp_tool.description,
                    input_schema=mcp_tool.input_schema,
                    mcp_client=mcp_client,
                )
                tools.register(tool_name, adapter)

        tool_names = tools.tool_names
        if tool_names:
            console.print(f"[dim]Tools enabled: {', '.join(tool_names)}[/dim]")

    # Create agent
    system_prompt = """You are a helpful AI assistant. You can help with various tasks including:
- Answering questions
- Writing and editing code
- Working with files
- Executing commands
- Using MCP tools for external integrations

When using tools, explain what you're doing and why."""

    agent = AgentLoop(
        provider=provider,
        tools=tools,
        system_prompt=system_prompt,
    )

    return agent


@click.group()
@click.version_option(version="0.4.0")
def cli():
    """My Agent - AI Agent with Agent Loop

    A CLI tool for interacting with AI models using Agent Loop.
    """
    pass


@cli.command()
@click.option("--provider", "-p", default="openai", help="LLM provider (openai, deepseek, anthropic, ollama)")
@click.option("--model", "-m", default=None, help="Model to use (uses provider default if not specified)")
@click.option("--enable-tools", "-t", is_flag=True, help="Enable tool calling")
@click.option("--enable-mcp", is_flag=True, help="Enable MCP tools")
@click.option("--stream", "-s", is_flag=True, help="Enable streaming output")
def chat(provider: str, model: str, enable_tools: bool, enable_mcp: bool, stream: bool):
    """Start interactive chat mode"""
    console.print(
        Panel(
            f"[bold green]My Agent - Interactive Chat[/bold green]\n"
            f"[dim]Provider: {provider} | Stream: {'on' if stream else 'off'} | Type 'exit' or 'quit' to end[/dim]",
            title="Welcome",
        )
    )

    # Initialize MCP if requested
    if enable_mcp:
        asyncio.run(init_mcp_servers())

    try:
        agent = create_agent(provider, model, enable_tools, enable_mcp)
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
            console.print("\n[bold green]Agent:[/bold green] ", end="")

            if stream:
                # Streaming output
                async def stream_response():
                    async for chunk in agent.run_stream(user_input):
                        if isinstance(chunk, dict):
                            # Tool call info
                            continue
                        console.print(chunk, end="", highlight=False)
                    console.print()  # New line after streaming

                asyncio.run(stream_response())
            else:
                # Non-streaming output
                response = asyncio.run(agent.run(user_input))
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
@click.option("--enable-mcp", is_flag=True, help="Enable MCP tools")
@click.option("--stream", "-s", is_flag=True, help="Enable streaming output")
def ask(prompt: str, provider: str, model: str, enable_tools: bool, enable_mcp: bool, stream: bool):
    """Execute a single query"""
    console.print(f"[bold blue]Query:[/bold blue] {prompt}")
    console.print(f"[dim]Provider: {provider} | Stream: {'on' if stream else 'off'}[/dim]\n")

    # Initialize MCP if requested
    if enable_mcp:
        asyncio.run(init_mcp_servers())

    try:
        agent = create_agent(provider, model, enable_tools, enable_mcp)
    except click.Abort:
        return

    # Run agent
    try:
        console.print("[bold green]Response:[/bold green] ", end="")

        if stream:
            # Streaming output
            async def stream_response():
                async for chunk in agent.run_stream(prompt):
                    if isinstance(chunk, dict):
                        continue
                    console.print(chunk, end="", highlight=False)
                console.print()

            asyncio.run(stream_response())
        else:
            # Non-streaming output
            response = asyncio.run(agent.run(prompt))
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
def skills():
    """List available skills"""
    console.print("[bold]Available Skills:[/bold]\n")

    categories = skill_loader.get_categories()

    for category in sorted(categories):
        console.print(f"[bold cyan]{category.upper()}[/bold cyan]")

        category_skills = skill_loader.list_skills(category=category)
        for skill in category_skills:
            console.print(f"  [bold]{skill.name}[/bold] - {skill.description}")
            if skill.examples:
                console.print(f"    [dim]Example: {skill.examples[0]}[/dim]")

        console.print()


@cli.command()
@click.argument("skill_name")
@click.argument("task")
@click.option("--provider", "-p", default="openai", help="LLM provider")
@click.option("--model", "-m", default=None, help="Model to use")
@click.option("--stream", "-s", is_flag=True, help="Enable streaming output")
def run_skill(skill_name: str, task: str, provider: str, model: str, stream: bool):
    """Run a skill with the given task"""
    skill = skill_loader.get_skill(skill_name)

    if not skill:
        console.print(f"[red]Error: Skill '{skill_name}' not found[/red]")
        console.print("[dim]Use 'agent skills' to list available skills[/dim]")
        raise click.Abort()

    # Build the full prompt
    full_prompt = f"{skill.prompt}\n\n{task}"

    console.print(f"[bold blue]Skill:[/bold blue] {skill.name}")
    console.print(f"[bold blue]Task:[/bold blue] {task}")
    console.print(f"[dim]Provider: {provider} | Stream: {'on' if stream else 'off'}[/dim]\n")

    # Create agent with tools if skill requires them
    enable_tools = skill.tools is not None and len(skill.tools) > 0

    try:
        agent = create_agent(provider, model, enable_tools)
    except click.Abort:
        return

    # Run agent
    try:
        console.print("[bold green]Response:[/bold green] ", end="")

        if stream:
            async def stream_response():
                async for chunk in agent.run_stream(full_prompt):
                    if isinstance(chunk, dict):
                        continue
                    console.print(chunk, end="", highlight=False)
                console.print()

            asyncio.run(stream_response())
        else:
            response = asyncio.run(agent.run(full_prompt))
            console.print(Markdown(response))
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
def mcp_servers():
    """List configured MCP servers"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp_config.json")

    if not os.path.exists(config_path):
        console.print("[yellow]No MCP configuration file found[/yellow]")
        console.print("[dim]Create mcp_config.json in project root[/dim]")
        return

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})

        if not servers:
            console.print("[yellow]No MCP servers configured[/yellow]")
            return

        console.print("[bold]Configured MCP Servers:[/bold]\n")

        for name, server_config in servers.items():
            command = server_config.get("command", "")
            args = server_config.get("args", [])
            console.print(f"  [bold]{name}[/bold]")
            console.print(f"    Command: {command} {' '.join(args)}")

        console.print("\n[dim]Use --enable-mcp flag with chat/ask commands to enable MCP tools[/dim]")

    except Exception as e:
        console.print(f"[red]Error reading MCP config: {e}[/red]")


@cli.command()
def version():
    """Show version information"""
    console.print("[bold]My Agent[/bold] v0.4.0")


if __name__ == "__main__":
    cli()

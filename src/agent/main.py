"""CLI entry point for My Agent"""

import click
from rich.console import Console
from rich.markdown import Markdown

console = Console()


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
    console.print(f"[bold green]Starting chat with model: {model}[/bold green]")
    console.print("[dim]Type 'exit' or 'quit' to end the conversation[/dim]\n")

    # TODO: Implement Agent Loop
    console.print("[yellow]Agent Loop not implemented yet...[/yellow]")


@cli.command()
@click.argument("prompt")
@click.option("--model", "-m", default="gpt-4", help="Model to use")
def ask(prompt: str, model: str):
    """Execute a single query"""
    console.print(f"[bold blue]Query:[/bold blue] {prompt}")
    console.print(f"[dim]Using model: {model}[/dim]\n")

    # TODO: Implement single query
    console.print("[yellow]Single query not implemented yet...[/yellow]")


@cli.command()
def version():
    """Show version information"""
    console.print("[bold]My Agent[/bold] v0.1.0")


if __name__ == "__main__":
    cli()

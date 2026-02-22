"""
AEGIS - Advanced Electronic Guardian & Intelligence System
Main entry point for the multi-agent AI system
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import click
from rich.console import Console
from rich.panel import Panel
from loguru import logger

from agents import OrchestratorAgent
from core import config
from core.mode import Mode

console = Console()

@click.command()
@click.option('--mode', type=click.Choice(['normal', 'monster', 'hat']), default='normal', help='Operational mode')
@click.option('--peer', is_flag=True, help='Enable peer integration (MCP server)')
@click.option('--mcp-port', type=int, default=3000, help='MCP server port')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(mode: str, peer: bool, mcp_port: int, debug: bool):
    """
    AEGIS - Advanced Electronic Guardian & Intelligence System
    
    A fully local multi-agent AI with dual-mode operation.
    """
    # Configure logging
    log_level = "DEBUG" if debug else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.add("data/memory/logs/aegis.log", rotation="1 day", level=log_level)
    
    # Display splash
    if mode == "monster":
        mode_enum = Mode.MONSTER
        mode_emoji = "💀⚡"
        mode_text = "PROTOCOL 666 ACTIVE"
        mode_color = "red"
    elif mode == "hat":
        mode_enum = Mode.HAT
        mode_emoji = "🎯🔐"
        mode_text = "HAT MODE - SECURITY TESTING"
        mode_color = "cyan"
    else:
        mode_enum = Mode.NORMAL
        mode_emoji = "🛡️✨"
        mode_text = "NORMAL MODE"
        mode_color = "green"
    
    peer_status = "ENABLED" if peer else "DISABLED"
    
    console.print(Panel.fit(
        f"[bold cyan]AEGIS[/bold cyan] {mode_emoji}\n"
        f"[dim]Advanced Electronic Guardian & Intelligence System[/dim]\n\n"
        f"Mode: [bold {mode_color}]{mode_text}[/bold {mode_color}]\n"
        f"Peer Integration: [bold]{peer_status}[/bold]",
        title="🛡️ System Initialization",
        border_style="cyan"
    ))
    
    # Run async main
    try:
        asyncio.run(main_async(mode_enum, peer, mcp_port))
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down gracefully...[/yellow]")
    except Exception as e:
        logger.exception("Fatal error")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

async def main_async(mode: Mode, peer: bool, mcp_port: int):
    """Async main function - conversation loop"""
    
    # Initialize orchestrator
    console.print("[cyan]Initializing Orchestrator...[/cyan]")
    orchestrator = OrchestratorAgent()
    
    # Set initial mode
    orchestrator.mode_manager.switch_mode(mode)
    
    console.print(f"[green]✓ Ready in {orchestrator.get_mode_display()} mode[/green]\n")
    
    # Display help
    console.print("[dim]Commands:[/dim]")
    console.print("  [cyan]/monster[/cyan] - Switch to Protocol 666")
    console.print("  [cyan]/hat[/cyan] - Switch to HAT Mode (Security Testing)")
    console.print("  [cyan]/normal[/cyan] - Switch to Normal mode")
    console.print("  [cyan]/exit[/cyan] or [cyan]Ctrl+C[/cyan] - Exit\n")
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            try:
                user_input = console.input(f"[bold green]You:[/bold green] ")
            except EOFError:
                console.print("\n[yellow]Input stream closed. Use /exit to quit.[/yellow]")
                console.print("[yellow]Interrupted. Type /exit to quit.[/yellow]")
                continue
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type /exit to quit.[/yellow]")
                continue
            
            if not user_input.strip():
                continue
            
            # Handle exit
            if user_input.strip() == "/exit":
                console.print("[yellow]Goodbye! 🛡️[/yellow]")
                # mcp_server is not defined in this scope, assuming it's part of a larger context or future feature
                # if mcp_server:
                #     await mcp_server.cleanup()
                break
            
            # Stream response
            console.print(f"\n[bold {orchestrator.mode_manager.get_mode_color()}]{orchestrator.get_mode_display()}:[/bold {orchestrator.mode_manager.get_mode_color()}] ", end="")
            
            response_generator = orchestrator.handle_message(user_input)
            
            full_response = ""
            async for chunk in response_generator:
                console.print(chunk, end="")
                full_response += chunk
            
            console.print("\n")
            
            # Update context with full response
            if full_response:
                orchestrator.update_context("assistant", full_response)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type /exit to quit.[/yellow]")
        except Exception as e:
            logger.exception("Error in conversation loop")
            console.print(f"\n[red]Error: {e}[/red]\n")

if __name__ == "__main__":
    cli()

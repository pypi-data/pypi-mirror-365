#!/usr/bin/env python3
"""
IOWarp Agents CLI - Beautiful command-line interface for managing scientific AI agents
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.markdown import Markdown
import requests

console = Console()

# Agent metadata
AGENTS_REPO_URL = "https://api.github.com/repos/iowarp/iowarp-agents/contents/agents"
AGENTS_RAW_URL = "https://raw.githubusercontent.com/iowarp/iowarp-agents/main/agents"

# Supported platforms and their paths
PLATFORMS = {
    "claude": {
        "name": "Claude Code",
        "local_path": ".claude/agents",
        "global_path": "~/.claude/agents",
        "description": "Claude Code AI assistant with subagent support"
    }
}

class AgentManager:
    """Manages agent operations"""
    
    def __init__(self):
        self.console = Console()
        self._agents_cache = None
    
    def fetch_available_agents(self) -> Dict[str, Dict]:
        """Fetch available agents from GitHub repository"""
        if self._agents_cache:
            return self._agents_cache
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Fetching available agents...", total=None)
                
                response = requests.get(AGENTS_REPO_URL, timeout=10)
                response.raise_for_status()
                
                agents = {}
                for item in response.json():
                    if item['name'].endswith('.md'):
                        agent_name = item['name'][:-3]  # Remove .md extension
                        
                        # Fetch agent content to parse metadata
                        agent_response = requests.get(f"{AGENTS_RAW_URL}/{item['name']}", timeout=10)
                        agent_response.raise_for_status()
                        
                        metadata = self._parse_agent_metadata(agent_response.text)
                        agents[agent_name] = {
                            'filename': item['name'],
                            'download_url': agent_response.url,
                            **metadata
                        }
                
                progress.update(task, completed=True)
                self._agents_cache = agents
                return agents
                
        except requests.RequestException as e:
            self.console.print(f"[red]Error fetching agents: {e}[/red]")
            return {}
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/red]")
            return {}
    
    def _parse_agent_metadata(self, content: str) -> Dict:
        """Parse agent metadata from markdown frontmatter"""
        lines = content.split('\n')
        if not lines[0].strip() == '---':
            return {}
        
        metadata = {}
        in_frontmatter = True
        i = 1
        
        while i < len(lines) and in_frontmatter:
            line = lines[i].strip()
            if line == '---':
                in_frontmatter = False
                break
            
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                if key == 'tools' and ',' in value:
                    metadata[key] = [tool.strip() for tool in value.split(',')]
                else:
                    metadata[key] = value
            i += 1
        
        # Extract description from content if not in metadata
        if 'description' not in metadata and i < len(lines):
            content_lines = lines[i+1:]  # Skip the --- line
            for line in content_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    metadata['description'] = line
                    break
        
        return metadata

def get_agent_display_name(agent_name: str) -> str:
    """Convert agent name to display name"""
    return agent_name.replace('-', ' ').title()

def get_category_icon(agent_name: str) -> str:
    """Get appropriate icon for agent category"""
    icons = {
        'data-io': '💾',
        'analysis': '📊', 
        'viz': '📊',
        'hpc': '🚀',
        'performance': '🚀',
        'research': '📚',
        'doc': '📚',
        'workflow': '⚙️',
        'orchestrator': '⚙️'
    }
    
    for key, icon in icons.items():
        if key in agent_name.lower():
            return icon
    
    return '🤖'  # Default icon

@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def cli(ctx):
    """
    🤖 IOWarp Agents - Beautiful CLI for Scientific AI Agents
    
    Manage and install specialized AI subagents for scientific computing workflows.
    """
    if ctx.invoked_subcommand is None:
        # Show welcome message and available commands
        console.print()
        console.print(Panel.fit(
            "[bold blue]🤖 IOWarp Agents CLI[/bold blue]\n\n"
            "[dim]Specialized AI subagents for scientific computing workflows[/dim]",
            border_style="blue"
        ))
        console.print()
        
        # Show available commands
        commands_table = Table(show_header=False, box=None, padding=(0, 2))
        commands_table.add_column("Command", style="cyan bold")
        commands_table.add_column("Description", style="dim")
        
        commands_table.add_row("list", "List all available agents")
        commands_table.add_row("install", "Install an agent for a specific platform")
        commands_table.add_row("uninstall", "Remove an installed agent")
        commands_table.add_row("status", "Show installation status of agents")
        commands_table.add_row("update", "Update agents to latest versions")
        
        console.print("Available commands:")
        console.print(commands_table)
        console.print()
        console.print("[dim]Use --help with any command for more information[/dim]")
        console.print()

@cli.command()
@click.option('--detailed', '-d', is_flag=True, help='Show detailed information about each agent')
def list(detailed):
    """📋 List all available agents"""
    
    manager = AgentManager()
    agents = manager.fetch_available_agents()
    
    if not agents:
        console.print("[red]No agents found or unable to fetch agent list.[/red]")
        return
    
    console.print()
    console.print(Panel.fit(
        f"[bold green]Available IOWarp Agents[/bold green] [dim]({len(agents)} total)[/dim]",
        border_style="green"
    ))
    console.print()
    
    if detailed:
        # Detailed view with full descriptions
        for agent_name, agent_data in sorted(agents.items()):
            icon = get_category_icon(agent_name)
            display_name = get_agent_display_name(agent_name)
            
            panel_content = f"[bold]{icon} {display_name}[/bold]\n\n"
            panel_content += f"[dim]ID:[/dim] {agent_name}\n"
            
            if 'description' in agent_data:
                panel_content += f"[dim]Description:[/dim] {agent_data['description']}\n"
            
            if 'tools' in agent_data:
                tools = agent_data['tools']
                if isinstance(tools, list):
                    panel_content += f"[dim]Tools:[/dim] {', '.join(tools[:3])}"
                    if len(tools) > 3:
                        panel_content += f" (+{len(tools) - 3} more)"
                    panel_content += "\n"
            
            console.print(Panel(panel_content.strip(), border_style="blue", padding=(1, 2)))
            
    else:
        # Compact grid view
        items = []
        for agent_name, agent_data in sorted(agents.items()):
            icon = get_category_icon(agent_name)
            display_name = get_agent_display_name(agent_name)
            
            # Create a compact card
            card = f"[bold]{icon} {display_name}[/bold]\n[dim]{agent_name}[/dim]"
            items.append(Panel(card, border_style="blue", padding=(0, 1)))
        
        # Display in columns
        console.print(Columns(items, equal=True, expand=True))
    
    console.print()
    console.print("[dim]Use 'iowarp-agents install <agent-name>' to install an agent[/dim]")
    console.print()

@cli.command()
@click.argument('agent_name', required=False)
@click.argument('platform', required=False)
@click.argument('scope', required=False)
def install(agent_name, platform, scope):
    """💾 Install an agent for a specific platform"""
    
    manager = AgentManager()
    agents = manager.fetch_available_agents()
    
    if not agents:
        console.print("[red]Unable to fetch agent list. Please check your internet connection.[/red]")
        return
    
    # Interactive agent selection if not provided
    if not agent_name:
        agent_name = _select_agent(agents)
        if not agent_name:
            return
    
    # Validate agent exists
    if agent_name not in agents:
        console.print(f"[red]Agent '{agent_name}' not found.[/red]")
        console.print("[dim]Use 'iowarp-agents list' to see available agents.[/dim]")
        return
    
    # Interactive platform selection if not provided
    if not platform:
        platform = _select_platform()
        if not platform:
            return
    
    # Validate platform
    if platform not in PLATFORMS:
        console.print(f"[red]Platform '{platform}' not supported.[/red]")
        console.print(f"[dim]Supported platforms: {', '.join(PLATFORMS.keys())}[/dim]")
        return
    
    # Interactive scope selection if not provided
    if not scope:
        scope = _select_scope()
        if not scope:
            return
    
    # Validate scope
    if scope not in ['local', 'global']:
        console.print(f"[red]Scope '{scope}' not valid. Use 'local' or 'global'.[/red]")
        return
    
    # Perform installation
    _install_agent(agent_name, agents[agent_name], platform, scope)

def _select_agent(agents: Dict[str, Dict]) -> Optional[str]:
    """Interactive agent selection"""
    console.print()
    console.print("[bold cyan]Select an agent to install:[/bold cyan]")
    console.print()
    
    agent_list = list(sorted(agents.keys()))
    
    # Create a numbered list
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("", style="cyan bold", width=4)
    table.add_column("Agent", style="bold")
    table.add_column("Description", style="dim")
    
    for i, agent_name in enumerate(agent_list, 1):
        icon = get_category_icon(agent_name)
        display_name = get_agent_display_name(agent_name)
        description = agents[agent_name].get('description', 'No description available')[:80]
        if len(agents[agent_name].get('description', '')) > 80:
            description += '...'
        
        table.add_row(f"{i})", f"{icon} {display_name}", description)
    
    console.print(table)
    console.print()
    
    while True:
        try:
            choice = IntPrompt.ask(
                "Enter your choice", 
                default=1, 
                console=console,
                show_default=True
            )
            
            if 1 <= choice <= len(agent_list):
                selected_agent = agent_list[choice - 1]
                console.print(f"[green]Selected:[/green] {get_agent_display_name(selected_agent)}")
                return selected_agent
            else:
                console.print(f"[red]Invalid choice. Please enter a number between 1 and {len(agent_list)}.[/red]")
                
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Installation cancelled.[/yellow]")
            return None

def _select_platform() -> Optional[str]:
    """Interactive platform selection"""
    console.print()
    console.print("[bold cyan]Select target platform:[/bold cyan]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("", style="cyan bold", width=4)
    table.add_column("Platform", style="bold")
    table.add_column("Description", style="dim")
    
    platform_list = list(PLATFORMS.keys())
    
    for i, platform_key in enumerate(platform_list, 1):
        platform_info = PLATFORMS[platform_key]
        table.add_row(f"{i})", platform_info['name'], platform_info['description'])
    
    console.print(table)
    console.print()
    
    while True:
        try:
            choice = IntPrompt.ask(
                "Enter your choice", 
                default=1, 
                console=console,
                show_default=True
            )
            
            if 1 <= choice <= len(platform_list):
                selected_platform = platform_list[choice - 1]
                console.print(f"[green]Selected:[/green] {PLATFORMS[selected_platform]['name']}")
                return selected_platform
            else:
                console.print(f"[red]Invalid choice. Please enter a number between 1 and {len(platform_list)}.[/red]")
                
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Installation cancelled.[/yellow]")
            return None

def _select_scope() -> Optional[str]:
    """Interactive scope selection"""
    console.print()
    console.print("[bold cyan]Select installation scope:[/bold cyan]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("", style="cyan bold", width=4)
    table.add_column("Scope", style="bold")
    table.add_column("Description", style="dim")
    
    table.add_row("1)", "Local project", "Install in current project only (./.claude/agents)")
    table.add_row("2)", "Global installation", "Install for all projects (~/.claude/agents)")
    
    console.print(table)
    console.print()
    
    while True:
        try:
            choice = IntPrompt.ask(
                "Enter your choice", 
                default=1, 
                console=console,
                show_default=True
            )
            
            if choice == 1:
                console.print("[green]Selected:[/green] Local project")
                return "local"
            elif choice == 2:
                console.print("[green]Selected:[/green] Global installation")
                return "global"
            else:
                console.print("[red]Invalid choice. Please enter 1 or 2.[/red]")
                
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Installation cancelled.[/yellow]")
            return None

def _install_agent(agent_name: str, agent_data: Dict, platform: str, scope: str):
    """Install the specified agent"""
    platform_info = PLATFORMS[platform]
    
    # Determine target directory
    if scope == "local":
        target_dir = Path(platform_info['local_path'])
    else:
        target_dir = Path(platform_info['global_path']).expanduser()
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Target file path
    target_file = target_dir / agent_data['filename']
    
    console.print()
    console.print(Panel.fit(
        f"[bold blue]Installing Agent[/bold blue]\n\n"
        f"[dim]Agent:[/dim] {get_agent_display_name(agent_name)}\n"
        f"[dim]Platform:[/dim] {platform_info['name']}\n"
        f"[dim]Scope:[/dim] {scope}\n"
        f"[dim]Target:[/dim] {target_file}",
        border_style="blue"
    ))
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading agent...", total=None)
            
            # Download agent content
            response = requests.get(agent_data['download_url'], timeout=30)
            response.raise_for_status()
            
            progress.update(task, description="Writing agent file...")
            
            # Write to target file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            progress.update(task, completed=True)
        
        console.print()
        console.print(Panel.fit(
            f"[bold green]✅ Installation Successful![/bold green]\n\n"
            f"Agent '{get_agent_display_name(agent_name)}' has been installed to:\n"
            f"[dim]{target_file}[/dim]\n\n"
            f"The agent is now available in {platform_info['name']}.",
            border_style="green"
        ))
        
        # Show usage instructions
        console.print()
        console.print("[bold cyan]Usage Instructions:[/bold cyan]")
        if platform == "claude":
            console.print("• Use [bold]/agents[/bold] command in Claude Code")
            console.print(f"• Or mention: [dim]\"Use the {agent_name} to help me...\"[/dim]")
        
        console.print()
        
    except Exception as e:
        console.print()
        console.print(Panel.fit(
            f"[bold red]❌ Installation Failed[/bold red]\n\n"
            f"Error: {str(e)}",
            border_style="red"
        ))

@cli.command()
@click.argument('agent_name', required=False)
@click.argument('platform', required=False)
@click.argument('scope', required=False)
def uninstall(agent_name, platform, scope):
    """🗑️  Remove an installed agent"""
    console.print("[yellow]Uninstall functionality coming soon![/yellow]")

@cli.command()
def status():
    """📊 Show installation status of agents"""
    console.print("[yellow]Status functionality coming soon![/yellow]")

@cli.command()
def update():
    """🔄 Update agents to latest versions"""
    console.print("[yellow]Update functionality coming soon![/yellow]")

def main():
    """Entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
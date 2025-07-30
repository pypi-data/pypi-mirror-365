# IOWarp Agents CLI

🤖 **Beautiful command-line interface for managing IOWarp scientific AI agents**

[![PyPI version](https://img.shields.io/pypi/v/iowarp-agents.svg)](https://pypi.org/project/iowarp-agents/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎨 **Beautiful UI** - Rich terminal interface with colors, tables, and interactive menus
- 🔍 **Agent Discovery** - Automatically fetches latest agents from GitHub
- 📦 **Easy Installation** - Interactive menus guide you through the process
- 🎯 **Multi-Platform** - Supports Claude Code (more platforms coming soon)
- 🌍 **Flexible Scope** - Install agents locally or globally
- 🚀 **Zero Config** - Works out of the box with sensible defaults

## 🚀 Quick Start

### Installation

```bash
# Install with uvx (recommended)
uvx iowarp-agents

# Or install globally with pip
pip install iowarp-agents
```

### Basic Usage

```bash
# List all available agents
iowarp-agents list

# Install an agent (interactive mode)
iowarp-agents install

# Install specific agent for Claude Code locally
iowarp-agents install workflow-orchestrator claude local

# Install with interactive menus
iowarp-agents install workflow-orchestrator
```

## 📋 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `list` | List all available agents | `iowarp-agents list --detailed` |
| `install` | Install an agent | `iowarp-agents install data-io-expert claude local` |
| `status` | Show installation status | `iowarp-agents status` |
| `update` | Update agents to latest versions | `iowarp-agents update` |

## 🎯 Available Agents

| Agent | Specialization | Use Cases |
|-------|----------------|-----------|
| **data-io-expert** | Scientific data formats & I/O | HDF5, ADIOS, Parquet conversion |
| **analysis-viz-expert** | Data analysis & visualization | Statistical analysis, plotting |
| **hpc-performance-expert** | HPC & performance optimization | SLURM jobs, profiling |
| **research-doc-expert** | Research & documentation | Literature search, experiment tracking |
| **workflow-orchestrator** | Workflow & environment management | Pipeline creation, automation |

## 📦 Installation Examples

### Interactive Installation
```bash
$ iowarp-agents install

Select an agent to install:

1) 💾 Data Io Expert       Scientific data formats and I/O operations
2) 📊 Analysis Viz Expert  Data analysis and visualization  
3) 🚀 Hpc Performance Expert  HPC and performance optimization
4) 📚 Research Doc Expert  Research literature and documentation
5) ⚙️ Workflow Orchestrator  Workflow and environment management

Enter your choice [1]: 2

Select target platform:

1) Claude Code  Claude Code AI assistant with subagent support

Enter your choice [1]: 1

Select installation scope:

1) Local project      Install in current project only (./.claude/agents)  
2) Global installation Install for all projects (~/.claude/agents)

Enter your choice [1]: 1

✅ Installation Successful!

Agent 'Analysis Viz Expert' has been installed to:
./.claude/agents/analysis-viz-expert.md

The agent is now available in Claude Code.
```

### Direct Installation
```bash
# Install workflow orchestrator for Claude Code in current project
$ iowarp-agents install workflow-orchestrator claude local

✅ Installation Successful!

Agent 'Workflow Orchestrator' has been installed to:
./.claude/agents/workflow-orchestrator.md
```

## 🎨 Beautiful Output

The CLI features rich, colorful output with:
- 🎯 **Interactive menus** with numbered options
- 📊 **Beautiful tables** for agent listings  
- 🎨 **Colored panels** for status and results
- ⚡ **Progress indicators** for downloads
- 💡 **Helpful guidance** throughout the process

## 🔧 Advanced Usage

### List Agents with Details
```bash
iowarp-agents list --detailed
```

### Install Multiple Agents
```bash
# Install for different scopes
iowarp-agents install data-io-expert claude global
iowarp-agents install analysis-viz-expert claude local
```

## 🤝 Contributing

We welcome contributions! See our [contribution guide](https://github.com/iowarp/iowarp-agents#contributing) for details.

## 📚 Related Projects

- [IOWarp MCPs](https://github.com/iowarp/iowarp-mcps) - MCP servers for scientific computing
- [IOWarp Agents](https://github.com/iowarp/iowarp-agents) - Specialized AI subagents
- [IOWarp Website](https://iowarp.github.io/iowarp-agents/) - Browse agents online

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

*Part of the [IOWarp](https://github.com/iowarp) ecosystem for scientific computing*
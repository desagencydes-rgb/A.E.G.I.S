# AEGIS - Advanced Electronic Guardian & Intelligence System

> **Full-Stack Multi-Agent AI System**  
> Fully Local • Uncensored (Protocol 666) • Autonomous

## Overview

AEGIS is a sophisticated multi-agent AI system running entirely on local hardware with Ollama models. It features dual-mode operation (Normal + Monster Mode), advanced memory management with RAG, and robust tool execution with permission gating.

### Key Features

- **5 Specialized Agents**: Orchestrator, Tool Executor, Researcher, Memory Manager, Coding Agent
- **Dual Mode**: Normal (helpful) + Protocol 666 (unleashed, uncensored)
- **Hybrid Memory**: ChromaDB (vector) + SQLite (structured) + File system
- **MCP-Native Tools**: Industry-standard tool protocol with permission tiers
- **Peer Integration**: Connect with Claude Code, Cursor, VSCode
- **100% Local**: No cloud dependencies

## System Requirements

- **RAM**: 16GB minimum
- **GPU**: 8GB VRAM recommended (AMD/NVIDIA)
- **Storage**: ~20GB for models
- **OS**: Windows 10/11 with PowerShell
- **Software**: Ollama, Python 3.11+

## Quick Start

### 1. Install Prerequisites

```bash
# Install Ollama (if not already installed)
# Download from https://ollama.ai

# Verify Python version
python --version  # Should be 3.11+
```

### 2. Download Models

```bash
ollama pull hermes3:8b
ollama pull dolphin-llama3:8b
ollama pull phi3:latest
ollama pull dolphin-mistral:latest
ollama pull deepseek-coder:6.7b
ollama pull nomic-embed-text
```

### 3. Set Up AEGIS

```bash
# Clone or navigate to aegis directory
cd c:\Users\ULTRA PC\clawd\aegis

# Install dependencies with Poetry
poetry install

# Copy environment file
copy .env.example .env

# Initialize databases
poetry run python scripts/setup.py
```

### 4. Run AEGIS

```bash
# Start in Normal Mode
poetry run aegis

# Start in Monster Mode (Protocol 666)
poetry run aegis --mode monster

# Enable peer integration
poetry run aegis --peer --mcp-port 3000
```

## Usage

### Basic Commands

```bash
# Chat normally
> Hello, what can you do?

# Switch to Monster Mode
> /monster

# Switch back to Normal
> /normal

# Use dangerous operations (requires code)
> Delete all .tmp files yesyesyes45

# Get help
> /help
```

### Mode Differences

**Normal Mode:**
- Helpful, professional tone
- Safety guidelines active
- Asks for confirmation on risky operations

**Monster Mode (Protocol 666):**
- Unfiltered, direct responses
- No content restrictions
- Dark humor acceptable
- **Still accurate** - no hallucinations!

## Project Structure

```
aegis/
├── agents/          # 5 specialized AI agents
├── core/            # Mode switching, proxy, config
├── memory/          # Vector DB, SQLite, file persistence
├── tools/           # MCP server and tool implementations
├── ui/              # CLI interface
├── config/          # Mode configurations (TOML)
├── data/            # Persistent storage
├── scripts/         # Setup and utility scripts
└── main.py          # Entry point
```

## Architecture

AEGIS uses a multi-agent architecture where:

1. **Orchestrator Agent** handles user interaction and coordinates other agents
2. **Tool Executor Agent** performs file/system operations with permission gating
3. **Research Agent** handles web search and documentation
4. **Memory Agent** manages context retrieval and learning
5. **Coding Agent** handles code generation and IDE integration

All agents communicate through a message bus and share memory via the hybrid storage system.

## Security

### Permission System

- **SAFE**: Executes immediately (read files, search)
- **RISKY**: Asks for confirmation (write files, install packages)
- **DANGEROUS**: Requires `yesyesyes45` code (delete files, system commands)
- **FORBIDDEN**: Never executes (system files, BIOS)

### Containment Protocol

"Don't stop. Just ensure you can undo."

- Automatic backups before destructive operations
- Rollback logs with timestamps
- Operation audit trail

## Development

### Running Tests

```bash
# Unit tests
poetry run pytest tests/unit

# Integration tests
poetry run pytest tests/integration

# All tests
poetry run pytest
```

### Adding Tools

1. Create tool in `tools/tools/your_tool.py`
2. Define schema in `tools/schemas/tool_definitions.json`
3. Register in `tools/mcp_server.py`

## Contributing

AEGIS is a personal project. Feel free to fork and adapt to your needs.

## License

Private/Personal Use

---

**Built with:** Ollama • Python • ChromaDB • MCP • Rich

**No cloud. No censorship. No bullshit.** 🛡️

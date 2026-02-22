# AEGIS Project Context

This file serves as persistent context for AI assistants working on the AEGIS project. Read this before suggesting architectural changes or executing complex commands.

## Core Identity
AEGIS (Advanced Electronic Guardian & Intelligence System) is a fully local, multi-agent AI system.
- **Goal:** Uncensored, autonomous assistant running strictly on local hardware.
- **Tech Stack:** Python 3.11+, Ollama (Hermes3, Dolphin, Phi3, Deepseek-Coder), ChromaDB, SQLite. No cloud APIs.

## Architecture & Agents
The system consists of 5 specialized agents that communicate via a message bus:
1. **Orchestrator:** Handles user interaction and delegates tasks.
2. **Tool Executor:** Manages file/system operations. Gated by a strict Permission System.
3. **Researcher:** Handles information gathering.
4. **Memory Manager:** Manages hybrid storage (Vector DB + SQLite).
5. **Coding Agent:** Generates and analyzes code.

## Key Features & Quirks
- **Dual Mode:** 
  - *Normal Mode:* Professional, safe.
  - *Monster Mode (Protocol 666):* Uncensored, dark humor, unfiltered (but accurate).
- **Permission System:** Operations are tiered (SAFE, RISKY, DANGEROUS, FORBIDDEN). Dangerous operations (like deleting files) require the exact code `yesyesyes45`.
- **ChatDev Integration:** AEGIS integrates with the ChatDev orchestration framework via `chatdev_bridge/`. The `ChatDev/` repository itself is git-ignored and cloned automatically by `scripts/setup_chatdev_bridge.py`.
- **Strict File Operations:** Be highly analytical about file paths.

## Recent History (as of Initial Deployment)
- This project was originally incubated in `C:\Users\ULTRA PC\clawd\aegis` but was officially migrated and deployed to GitHub (`desagencydes-rgb/A.E.G.I.S`) from `C:\Projects\aegis`.
- Junk files (`hello.txt`, `fibonacci.py`) were purged during the migration.

## Workflow Rules for AI
1. **Never** suggest cloud-based APIs (OpenAI, Anthropic). Everything must use Ollama.
2. Ensure automated tests pass before committing (`pytest`).
3. If writing new integration scripts, ensure they respect the existing SQLite/ChromaDB memory structure.

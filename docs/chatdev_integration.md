# ChatDev Integration Guide for AEGIS

Complete guide to using AEGIS agents in ChatDev workflows.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Concepts](#basic-concepts)
4. [Creating Workflows](#creating-workflows)
5. [AEGIS Node Configuration](#aegis-node-configuration)
6. [Permission System](#permission-system)
7. [Protocol 666 (Monster Mode)](#protocol-666-monster-mode)
8. [Memory Integration](#memory-integration)
9. [Workflow Examples](#workflow-examples)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

**1. Run setup:**
```bash
cd aegis
python scripts/setup_chatdev_bridge.py
```

**2. Start ChatDev (optional - for web console):**
```bash
cd ChatDev
uv run python server_main.py --port 6400
```

**3. Use a workflow:**
```python
from runtime.sdk import run_workflow

result = run_workflow(
    yaml_file="workflows/aegis_simple_test.yaml",
    task_prompt="Research Python async/await and create example code"
)

print(result.final_message.text_content())
```

---

## Installation

### Prerequisites
- Python 3.11+
- Ollama with required models
- AEGIS already set up

### Bridge Installation

The setup script handles everything:
```bash
python scripts/setup_chatdev_bridge.py
```

**What it does:**
1. Verifies ChatDev is installed
2. Copies bridge to `ChatDev/node/aegis_bridge/`
3. Validates Python version
4. Tests bridge imports

### Manual Installation

If you prefer manual setup:

```bash
# 1. Copy bridge
cp -r chatdev_bridge ChatDev/node/aegis_bridge

# 2. Verify
ls ChatDev/node/aegis_bridge/
# Should see: __init__.py, aegis_node.py, config.py, etc.

# 3. Test import
python -c "from ChatDev.node.aegis_bridge import AEGISAgentNode; print('✓')"
```

---

## Basic Concepts

### AEGIS Agents as Nodes

Each AEGIS agent becomes a ChatDev node:

```yaml
nodes:
  - id: My Researcher
    type: aegis_agent  # Special node type
    config:
      aegis_agent: researcher  # Which AEGIS agent to use
      permission_mode: safe
      protocol_666: false
```

### Available Agent Types

| Agent Type | Purpose | Typical Permission |
|------------|---------|-------------------|
| `orchestrator` | Coordination, delegation | safe |
| `coding` | Code generation | risky |
| `researcher` | Information gathering | safe |
| `tool_executor` | System operations | safe/risky |
| `security` | Security analysis | safe |
| `code_architect` | System design | safe |
| `code_explorer` | Codebase navigation | safe |
| `reviewer` | Code quality review | safe |
| `feature_dev` | Feature implementation | risky |
| `memory` | Context management | safe |

---

## Creating Workflows

### Method 1: Auto-Generate (Recommended)

```bash
python scripts/workflow_generator.py "Create a data analysis pipeline with 3 agents"
# Generates: workflows/generated_create_a_data_...yaml
```

### Method 2: Use Template

```bash
cp workflow_templates/research_analysis.yaml workflows/my_workflow.yaml
# Edit workflows/my_workflow.yaml
```

### Method 3: Write from Scratch

```yaml
version: 0.4.0

graph:
  id: my_workflow
  description: My custom workflow
  
  start:
    - First Node
  
  end:
    - Last Node
  
  nodes:
    - id: First Node
      type: aegis_agent
      config:
        aegis_agent: researcher
        permission_mode: safe
        protocol_666: false
    
    - id: Last Node
      type: aegis_agent
      config:
        aegis_agent: coding
        permission_mode: risky
        protocol_666: false
  
  edges:
    - from: First Node
      to: Last Node
```

---

## AEGIS Node Configuration

### Full Configuration Options

```yaml
- id: Node Name
  type: aegis_agent
  config:
    # Required
    aegis_agent: researcher  # Agent type
    
    # Permission control
    permission_mode: safe  # safe | risky | dangerous
    
    # Mode switching
    protocol_666: false  # true = monster mode
    
    # Optional
    danger_code: "yesyesyes45"  # For DANGEROUS operations
    
    # Description (shows in UI)
    description: |
      What this agent does in this workflow
```

### Choosing the Right Agent

**Research & Analysis:**
- `researcher` - Web search, documentation
- `code_explorer` - Codebase analysis

**Design & Architecture:**
- `code_architect` - System design
- `feature_dev` - Feature planning

**Implementation:**
- `coding` - Code generation
- `tool_executor` - File operations

**Quality Assurance:**
- `reviewer` - Code review
- `security` - Security analysis

**Coordination:**
- `orchestrator` - Multi-agent coordination
- `memory` - Context management

---

## Permission System

### Permission Tiers

**SAFE** (`permission_mode: safe`)
- Read files
- Search/analyze
- Generate reports
- **Cannot**: Modify anything

**RISKY** (`permission_mode: risky`)
- Write files
- Create directories
- Modify existing code
- **Cannot**: Delete or execute

**DANGEROUS** (`permission_mode: dangerous`)
- Delete files
- Execute system commands
- Modify permissions
- **Requires**: `danger_code: "yesyesyes45"`

**FORBIDDEN** (Cannot be enabled)
- Format disk
- Modify BIOS
- Delete system files
- **Never allowed** regardless of config

### Permission Examples

```yaml
# Safe research
- id: Researcher
  config:
    aegis_agent: researcher
    permission_mode: safe  # ✓ Can read, search

# Writing code
- id: Coder
  config:
    aegis_agent: coding
    permission_mode: risky  # ✓ Can write files

# Dangerous operation with code
- id: Cleanup
  config:
    aegis_agent: tool_executor
    permission_mode: dangerous
    danger_code: "yesyesyes45"  # ✓ Can delete

# Best practice: add human gate before dangerous ops
- id: Human Approval
  type: human
  config:
    description: "Approve file deletion?"
```

### Audit Logging

All permission checks are logged:

```python
from chatdev_bridge.permission_enforcer import PermissionEnforcer

enforcer = PermissionEnforcer("risky")
check = enforcer.check_operation("delete_file", {"path": "/tmp/test"})

# Get audit trail
logs = enforcer.get_audit_log()
for log in logs:
    print(f"{log['operation']} ({log['tier']}) - {log['mode']}")
```

---

## Protocol 666 (Monster Mode)

### What is Protocol 666?

AEGIS's "unleashed" mode - no content filters, direct responses, dark humor allowed.

**Still accurate** - no hallucinations, just uncensored.

### When to Use

✅ **Good use cases:**
- Creative brainstorming
- Security vulnerability hunting
- Finding edge cases
- Unconventional solutions

❌ **Bad use cases:**
- Production code generation
- User-facing documentation
- Legal/compliance work
- Anything requiring professionalism

### Configuration

```yaml
# Enable for specific agent
- id: Creative Agent
  config:
    aegis_agent: researcher
    protocol_666: true  # UNLEASHED

# Disable for others
- id: Production Coder
  config:
    aegis_agent: coding
    protocol_666: false  # Professional
```

### Example: Security Audit

```yaml
# Use monster mode to find ALL vulnerabilities
- id: Aggressive Scanner
  config:
    aegis_agent: security
    permission_mode: safe
    protocol_666: true  # Will be thorough/aggressive
    description: "Hunt down every possible vulnerability"
```

---

## Memory Integration

### How Memory Works

AEGIS agents share memory across workflows via ChromaDB.

**Automatic sync:**
- Agents write to AEGIS memory during execution
- Memory persists across workflow runs
- Future workflows can access past context

### Memory Bridge API

```python
from chatdev_bridge.memory_bridge import AEGISMemoryBridge

bridge = AEGISMemoryBridge()

# Export AEGIS memories for ChatDev
memories = bridge.export_to_chatdev(
    query="Python async patterns",
    limit=5
)

# Import ChatDev memories to AEGIS
bridge.import_from_chatdev(
    memories=[...],
    workflow_id="my_workflow_123"
)

# Get context for agent
context = bridge.get_context_for_agent(
    agent_type="coding",
    current_task="Implement async API",
    limit=3
)
```

### Memory in Workflows

Memory is automatically available to agents:

```yaml
# Agent automatically has access to relevant memories
- id: Informed Coder
  config:
    aegis_agent: coding
    permission_mode: risky
    # Memory retrieval happens automatically based on task context
```

---

## Workflow Examples

### Example 1: Simple Pipeline

```yaml
version: 0.4.0

graph:
  id: simple_pipeline
  start: [Research]
  end: [Code]
  
  nodes:
    - id: Research
      type: aegis_agent
      config:
        aegis_agent: researcher
        permission_mode: safe
    
    - id: Code
      type: aegis_agent
      config:
        aegis_agent: coding
        permission_mode: risky
  
  edges:
    - from: Research
      to: Code
```

### Example 2: With Human Approval

```yaml
nodes:
  - id: Generate Code
    type: aegis_agent
    config:
      aegis_agent: coding
      permission_mode: risky
  
  - id: Human Review
    type: human
    config:
      description: "Review code. Type APPROVED to continue."
  
  - id: Deploy
    type: aegis_agent
    config:
      aegis_agent: tool_executor
      permission_mode: dangerous
      danger_code: "yesyesyes45"

edges:
  - from: Generate Code
    to: Human Review
  - from: Human Review
    to: Deploy
```

### Example 3: Iterative Loop

```yaml
nodes:
  - id: Implement
    type: aegis_agent
    config:
      aegis_agent: coding
      permission_mode: risky
  
  - id: Test
    type: aegis_agent
    config:
      aegis_agent: tool_executor
      permission_mode: safe
  
  - id: Review
    type: human
    config:
      description: "Type PASS if tests pass, otherwise provide feedback"

edges:
  - from: Implement
    to: Test
  - from: Test
    to: Review
  # Loop back if tests fail
  - from: Review
    to: Implement
    condition:
      type: keyword
      config:
        none: ["PASS"]
```

---

## Troubleshooting

### Common Issues

**1. "Agent type 'X' not found"**
```
Solution: Check available agents in BridgeConfig.AGENT_TYPES
Valid types: orchestrator, coding, researcher, etc.
```

**2. "Permission denied" errors**
```
Solution: Increase permission_mode:
- safe → risky (for file writes)
- risky → dangerous (for deletions, requires yesyesyes45)
```

**3. "Workflow execution timeout"**
```
Solution: Complex agents may take time. Be patient or:
- Use simpler agents for quick tasks
- Split into smaller workflows
- Check Ollama is running and responsive
```

**4. "Protocol 666 produces inappropriate output"**
```
Solution: Disable Protocol 666 or add filtering agent:
- Set protocol_666: false
- Add normal-mode agent after monster-mode agent
```

**5. "Memory not persisting"**
```
Solution: Check memory system:
- Verify ChromaDB directory exists
- Check file permissions
- Review memory bridge logs
```

### Debug Mode

Enable debug logging:

```python
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

### Getting Help

1. Check logs: `data/memory/logs/aegis.log`
2. Review workflow YAML syntax
3. Test agents individually
4. Consult [ChatDev docs](../ChatDev/docs/)

---

## Advanced Topics

### Custom Agent Development

Create new AEGIS agents and register them:

```python
# In agents/my_agent.py
class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MyAgent", agent_type="my_agent")
    
    async def process_task(self, task):
        # Your logic
        return {"response": "..."}

# Register in chatdev_bridge/config.py
AGENT_TYPES = {
    ...
    "my_agent": "agents.my_agent.MyCustomAgent"
}
```

### Workflow Optimization

**Parallel Execution:**
```yaml
# Multiple agents can run in parallel if edges allow
start:
  - Agent1
  - Agent2  # Both start simultaneously
```

**Conditional Routing:**
```yaml
edges:
  - from: Analyzer
    to: Path A
    condition:
      type: keyword
      config:
        any: ["complex"]
  
  - from: Analyzer
    to: Path B
    # Default path if condition not met
```

### Performance Tuning

- Use `safe` mode when possible (fastest)
- Avoid Protocol 666 for production (overhead)  
- Keep workflows under 10 agents
- Use caching in agents where applicable

---

## Next Steps

- Explore [workflow templates](../workflow_templates/)
- Try [auto-generation](../scripts/workflow_generator.py)
- Read [ChatDev docs](../ChatDev/docs/user_guide/en/)
- Build custom workflows for your use case

**Happy orchestrating!** 🎭🤖

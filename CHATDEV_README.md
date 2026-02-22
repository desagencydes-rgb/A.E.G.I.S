# AEGIS + ChatDev Integration

**Scale your AI agents into a company of specialists.**

AEGIS agents now run as custom nodes in ChatDev workflows, enabling multi-agent orchestration with visual workflow design, permission enforcement, and Protocol 666 mode switching.

## 🎯 What This Enables

- **Multi-Agent Workflows**: Coordinate 2-10+ AEGIS agents in complex pipelines
- **Visual Design**: Use ChatDev's web console to build workflows graphically
- **Permission System**: Enforce SAFE/RISKY/DANGEROUS tiers at node level
- **Protocol 666 Support**: Selectively unleash agents for creativity/security
- **Memory Sharing**: Agents share context via hybrid memory (ChromaDB + SQLite)
- **Auto-Generation**: Generate workflows from natural language descriptions

## 🚀 Quick Start

### 1. Setup (One-Time)

```bash
# Install bridge to ChatDev
python scripts/setup_chatdev_bridge.py
```

### 2. Run a Workflow

**Option A: Python SDK (Easiest)**
```python
from ChatDev.runtime.sdk import run_workflow

result = run_workflow(
    yaml_file="workflows/aegis_simple_test.yaml",
    task_prompt="Research Python async/await and create example code"
)

print(result.final_message.text_content())
```

**Option B: Web Console**
```bash
# Terminal 1: Start server
cd ChatDev
uv run python server_main.py --port 6400

# Terminal 2: Start frontend
cd ChatDev/frontend
VITE_API_BASE_URL=http://localhost:6400 npm run dev

# Open http://localhost:5173 and upload workflow YAML
```

### 3. Generate Custom Workflows

```bash
python scripts/workflow_generator.py "Create a security audit workflow with 4 agents"
# Generates: workflows/generated_create_a_security_...yaml
```

## 📁 Project Structure

```
aegis/
├── chatdev_bridge/          # Core bridge implementation
│   ├── __init__.py
│   ├── aegis_node.py        # Node wrapper
│   ├── config.py            # Agent mappings
│   ├── permission_enforcer.py
│   └── memory_bridge.py     # Memory sync
│
├── workflows/               # Ready-to-use workflows
│   ├── aegis_simple_test.yaml
│   ├── aegis_software_company.yaml (7 agents)
│   └── aegis_protocol666_creative.yaml
│
├── workflow_templates/      # Customizable templates
│   ├── research_analysis.yaml
│   ├── security_audit.yaml
│   └── code_refactoring.yaml
│
├── scripts/
│   ├── setup_chatdev_bridge.py    # Installation
│   ├── workflow_generator.py      # Auto-generation
│   └── test_chatdev_integration.py # Tests
│
├── docs/
│   └── chatdev_integration.md     # Full guide
│
└── ChatDev/                 # ChatDev repository (git clone)
    └── node/
        └── aegis_bridge/    # Bridge installed here (symlink or copy)
```

## 🎭 Available Agents

| Agent | Purpose | Typical Mode |
|-------|---------|--------------|
| `orchestrator` | Coordination & delegation | safe |
| `coding` | Code generation | risky |
| `researcher` | Information gathering | safe |
| `security` | Security analysis | safe (+ Protocol 666) |
| `code_architect` | System design | safe |
| `code_explorer` | Codebase navigation | safe |
| `reviewer` | Code quality | safe |
| `feature_dev` | Feature implementation | risky |
| `tool_executor` | System operations | safe/risky |
| `memory` | Context management | safe |

## 🔒 Permission Tiers

| Tier | Operations | Required Config |
|------|-----------|-----------------|
| **SAFE** | Read, analyze, search | `permission_mode: safe` |
| **RISKY** | Write files, create dirs | `permission_mode: risky` |
| **DANGEROUS** | Delete, execute commands | `permission_mode: dangerous` + `danger_code: "yesyesyes45"` |
| **FORBIDDEN** | System-critical ops | Never allowed |

## 😈 Protocol 666 (Monster Mode)

Unleash specific agents for:
- 🎨 **Creative brainstorming** (no filters)
- 🔍 **Security hunting** (aggressive vulnerability detection)  
- 💡 **Unconventional solutions** (think outside the box)

**Example:**
```yaml
- id: Creative Agent
  type: aegis_agent
  config:
    aegis_agent: researcher
    protocol_666: true  # UNLEASHED
```

**⚠️ Keep `false` for production code generation!**

## 📋 Example Workflows

### Simple Test (2 Agents)
```yaml
Research (researcher, safe) → Implementation (coding, risky)
```

### Software Company (7 Agents)
```yaml
Requirements → Architecture → Implementation 
  → Security Audit (Protocol 666) → Review → QA → Human Approval
```

### Protocol 666 Creative (3 Agents)
```yaml
Creative Brainstorm (Protocol 666) → Filter (normal) → Implement (normal)
```

## 🛠️ Creating Workflows

### Method 1: Auto-Generate

```bash
python scripts/workflow_generator.py "Create a REST API development pipeline"
```

### Method 2: Use Template

```bash
cp workflow_templates/research_analysis.yaml workflows/my_workflow.yaml
# Edit as needed
```

### Method 3: Write YAML

```yaml
version: 0.4.0

graph:
  id: my_workflow
  start: [Agent1]
  end: [Agent2]
  
  nodes:
    - id: Agent1
      type: aegis_agent
      config:
        aegis_agent: researcher
        permission_mode: safe
        protocol_666: false
    
    - id: Agent2
      type: aegis_agent
      config:
        aegis_agent: coding
        permission_mode: risky
        protocol_666: false
  
  edges:
    - from: Agent1
      to: Agent2
```

## 🧪 Testing

```bash
# Run integration tests
python scripts/test_chatdev_integration.py

# Expected output:
# ✅ ALL TESTS PASSED!
```

## 📚 Documentation

- **[Full Integration Guide](docs/chatdev_integration.md)** - Comprehensive documentation
- **[Workflow Templates](workflow_templates/README.md)** - Pre-built workflow templates
- **[ChatDev Docs](ChatDev/docs/)** - ChatDev documentation

## 🔧 Troubleshooting

**"Agent type not found"**
- Check `chatdev_bridge/config.py` for valid types

**"Permission denied"**
- Increase `permission_mode`: safe → risky → dangerous

**"Workflow times out"**
- Check Ollama is running: `ollama list`
- Use smaller/faster agents for testing

**"Protocol 666 too wild"**
- Disable: `protocol_666: false`
- Add normal-mode filter agent after

## 🎯 Use Cases

✅ **Software Development**
- Full SDLC automation
- Code review pipelines
- Refactoring workflows

✅ **Security & Compliance**
- Vulnerability scanning
- Security audits
- Compliance checks

✅ **Research & Analysis**
- Market research
- Technical investigation
- Data analysis

✅ **DevOps & Automation**
- Deployment pipelines
- Infrastructure management
- Monitoring & alerts

## 🚧 Current Limitations

- ChatDev web console requires manual workflow upload (no auto-registration yet)
- Memory sync is one-way (AEGIS → ChatDev) during execution
- Protocol 666 mode requires manual validation after creative tasks
- Maximum ~10 agents per workflow for performance

## 🗺️ Roadmap

**Phase 4: Production Hardening**
- [ ] Performance optimization
- [ ] Enhanced error handling
- [ ] Workflow validation tools
- [ ] Metrics & monitoring

**Phase 5: Advanced Features**
- [ ] Dynamic workflow modification
- [ ] Agent self-improvement loops
- [ ] Multi-workflow orchestration
- [ ] Web console customization

## 📄 License

This integration inherits licenses from:
- AEGIS (your project's license)
- ChatDev (Apache 2.0)

## 🤝 Contributing

1. Test changes with `scripts/test_chatdev_integration.py`
2. Update documentation
3. Add workflow examples
4. Submit PR

## 💬 Support

- **Docs**: [docs/chatdev_integration.md](docs/chatdev_integration.md)
- **Examples**: [workflows/](workflows/)
- **Templates**: [workflow_templates/](workflow_templates/)

---

**Built with 🤖 by combining AEGIS's specialized agents with ChatDev's orchestration platform.**

*Scale from single agent to company of agents in minutes.*

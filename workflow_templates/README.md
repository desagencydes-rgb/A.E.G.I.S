# Workflow Templates

Pre-built workflow templates for common use cases. Customize and use as starting points for your own workflows.

## Available Templates

### 1. Research & Analysis (`research_analysis.yaml`)
**Agents**: 3 (Researcher → Analyzer → Reporter)  
**Use Cases**:
- Market research
- Technical investigation
- Data analysis
- Competitive analysis

**Features**:
- Comprehensive research phase
- Analytical processing
- Report generation with insights

---

### 2. Security Audit (`security_audit.yaml`)
**Agents**: 5 (Scanner → Hunter → Analyzer → Reporter → Human)  
**Use Cases**:
- Security audits
- Vulnerability scanning
- Penetration testing
- Code security review

**Features**:
- ✅ Protocol 666 for aggressive vulnerability detection
- ✅ Risk prioritization
- ✅ Detailed audit reports
- ✅ Human review gate

---

### 3. Code Refactoring (`code_refactoring.yaml`)
**Agents**: 5 (Analyzer → Architect → Implementer → Reviewer → Human)  
**Use Cases**:
- Code cleanup
- Architecture improvements
- Technical debt reduction
- Code modernization

**Features**:
- ✅ Systematic analysis
- ✅ Architecture design
- ✅ Quality review
- ✅ Iterative approval loop

---

## How to Use Templates

### Option 1: Copy and Customize

```bash
# Copy template to workflows
cp workflow_templates/research_analysis.yaml workflows/my_research.yaml

# Edit for your needs
code workflows/my_research.yaml
```

### Option 2: Use Directly

```python
from runtime.sdk import run_workflow

result = run_workflow(
    yaml_file="workflow_templates/security_audit.yaml",
    task_prompt="Audit the authentication module for vulnerabilities"
)
```

### Option 3: Generate Custom Workflow

```bash
# Use workflow generator with template as inspiration
python scripts/workflow_generator.py "Create a DevOps pipeline workflow"
```

---

## Customization Guide

### Modifying Agent Types

Replace `aegis_agent` values with any of:
- `orchestrator` - Coordination and delegation
- `coding` - Code generation and implementation
- `researcher` - Information gathering
- `tool_executor` - System operations
- `security` - Security analysis
- `code_architect` - System design
- `code_explorer` - Codebase navigation
- `reviewer` - Code quality review
- `feature_dev` - Feature implementation
- `memory` - Context management

### Adjusting Permission Levels

| Mode | Use When |
|------|----------|
| `safe` | Agent only reads/analyzes |
| `risky` | Agent needs to write files |
| `dangerous` | Agent deletes/executes (add yesyesyes45 code) |

### Enabling Protocol 666

Set `protocol_666: true` for:
- 🎨 Creative tasks (brainstorming, design)
- 🔍 Security hunting (find ALL vulnerabilities)
- 💡 Unconventional problem-solving

**⚠️ Warning**: Keep `false` for production code generation

### Adding Loops

Create iterative workflows with conditional edges:

```yaml
edges:
  - from: Agent1
    to: Agent2
  
  # Loop back if condition not met
  - from: Agent2
    to: Agent1
    condition:
      type: keyword
      config:
        none:
          - "DONE"
          - "COMPLETE"
```

---

## Creating New Templates

1. Start with an existing template
2. Define your workflow stages
3. Choose appropriate agent types
4. Set permission levels
5. Add human gates for critical decisions
6. Test with simple examples
7. Save to `workflow_templates/`

---

## Best Practices

### ✅ DO:
- Use SAFE mode by default
- Add human approval for DANGEROUS operations
- Enable Protocol 666 only when beneficial
- Include descriptive node descriptions
- Test workflows with simple tasks first

### ❌ DON'T:
- Give all agents RISKY permissions
- Use Protocol 666 for production code
- Create overly complex workflows (>10 agents)
- Skip human review for destructive operations
- Forget to add loop conditions

---

## Template Naming Convention

```
<purpose>_<variation>.yaml

Examples:
- research_analysis.yaml
- research_deep_dive.yaml
- security_audit.yaml
- security_quick_scan.yaml
```

---

## Community Templates

Want to contribute a template? Submit a PR with:
1. Working `.yaml` file
2. Documentation in this README
3. Example use case
4. Test results

---

## Troubleshooting

**Template won't load?**
- Check YAML syntax with `python -c "import yaml; yaml.safe_load(open('file.yaml'))"`
- Verify all agent types are valid
- Ensure edges reference existing node IDs

**Workflow gets stuck?**
- Check loop conditions
- Verify edge connectivity
- Review agent permissions

**Agents produce unexpected output?**
- Review agent descriptions
- Check permission modes
- Consider disabling Protocol 666 if enabled

---

## Further Reading

- [ChatDev Workflow Authoring Guide](../ChatDev/docs/user_guide/en/workflow_authoring.md)
- [AEGIS Agent Types](../README.md#architecture)
- [Permission System](../chatdev_bridge/permission_enforcer.py)

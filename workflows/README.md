# AEGIS-ChatDev Workflows

Example workflows demonstrating AEGIS agents in ChatDev orchestration.

## Available Workflows

### 1. Simple Test (`aegis_simple_test.yaml`)
**Agents**: 2 (Researcher → Coder)  
**Purpose**: Basic integration test  
**Use Case**: Quick validation of bridge functionality

```yaml
Research Phase (researcher, safe) 
  → Implementation Phase (coding, risky)
```

### 2. Software Company (`aegis_software_company.yaml`)
**Agents**: 7 (Full development pipeline)  
**Purpose**: Complete software development workflow  
**Use Case**: End-to-end project delivery

```yaml
Requirements Analyst (researcher, safe)
  → System Architect (code_architect, safe)
  → Senior Developer (coding, risky)
  → Security Auditor (security, safe, PROTOCOL 666)
  → Code Reviewer (reviewer, safe)
  → QA Engineer (tool_executor, safe)
  → Human Manager (human approval)
```

**Features**:
- ✅ Full SDLC automation
- ✅ Security audit with Protocol 666
- ✅ Human approval gate
- ✅ Iterative loop for revisions

### 3. Protocol 666 Creative (`aegis_protocol666_creative.yaml`)
**Agents**: 3 (Creative → Filter → Implement)  
**Purpose**: Demonstrate selective monster mode usage  
**Use Case**: Creative projects requiring unconventional thinking

```yaml
Creative Brainstorm (researcher, safe, PROTOCOL 666)
  → Professional Filter (code_architect, safe, normal)
  → Implementation (coding, risky, normal)
```

**Features**:
- ✅ Protocol 666 for creativity
- ✅ Normal mode for production
- ✅ Best of both worlds

## Usage

### Option 1: ChatDev Web Console (Recommended)

1. Start ChatDev server:
   ```bash
   cd ChatDev
   uv run python server_main.py --port 6400
   ```

2. Start frontend:
   ```bash
   cd ChatDev/frontend
   VITE_API_BASE_URL=http://localhost:6400 npm run dev
   ```

3. Open browser: `http://localhost:5173`

4. Upload workflow YAML and execute

### Option 2: Python SDK

```python
from runtime.sdk import run_workflow

result = run_workflow(
    yaml_file="workflows/aegis_simple_test.yaml",
    task_prompt="Research Python async and create example code"
)

print(result.final_message.text_content())
```

### Option 3: Standalone Test

```bash
cd aegis
python scripts/test_chatdev_integration.py
```

## Permission Modes

| Mode | Can Execute | Use Case |
|------|-------------|----------|
| `safe` | Read operations only | Research, analysis, review |
| `risky` | Read + write files | Implementation, coding |
| `dangerous` | Deletions, system commands | DevOps, cleanup (requires yesyesyes45) |

## Protocol 666 (Monster Mode)

Enable with `protocol_666: true` in node config.

**When to use**:
- 🎨 Creative brainstorming
- 🔍 Security vulnerability hunting
- 💡 Unconventional problem solving

**When NOT to use**:
- ❌ Production code generation
- ❌ User-facing documentation
- ❌ Sensitive operations

## Creating Custom Workflows

1. Copy an example workflow
2. Modify nodes and edges
3. Set appropriate permission modes
4. Test with simple task first
5. Iterate and refine

See [ChatDev workflow authoring guide](../ChatDev/docs/user_guide/en/workflow_authoring.md) for advanced features.

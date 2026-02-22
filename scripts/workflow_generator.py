"""
Workflow Generator - Auto-generate ChatDev workflows from natural language

Uses AEGIS Coding Agent to generate valid YAML workflow configurations
from user descriptions.
"""

import sys
from pathlib import Path
import uuid
from typing import Optional
from loguru import logger
import asyncio

# Add AEGIS to path
AEGIS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(AEGIS_ROOT))

from agents.coding import CodingAgent
from chatdev_bridge.config import BridgeConfig


class WorkflowGenerator:
    """Auto-generates ChatDev workflows using AEGIS Coding Agent"""
    
    WORKFLOW_TEMPLATE = """version: 0.4.0

graph:
  id: {workflow_id}
  description: {description}
  log_level: INFO
  
  initial_instruction: |
    {initial_instruction}
  
  start:
    - {start_node}
  
  end:
    - {end_node}
  
  nodes:
{nodes}
  
  edges:
{edges}
"""
    
    GENERATION_PROMPT = """You are a ChatDev workflow expert. Generate a valid YAML workflow configuration for the following request:

REQUEST: {user_request}

REQUIREMENTS:
1. Use AEGIS agent nodes (type: aegis_agent)
2. Available agent types: {agent_types}
3. Permission modes: safe (read-only), risky (write files), dangerous (delete/execute)
4. Protocol 666: Set to true for creative/security tasks, false for production
5. Include proper edges connecting nodes
6. Add human approval node for dangerous operations

EXAMPLE NODE:
```yaml
- id: Agent Name
  type: aegis_agent
  config:
    aegis_agent: researcher  # Choose from available types
    permission_mode: safe
    protocol_666: false
    description: What this agent does
```

EXAMPLE EDGE:
```yaml
- from: Node1
  to: Node2
```

Generate ONLY the YAML workflow configuration. Start with 'version: 0.4.0' and include all required sections.
"""
    
    def __init__(self):
        """Initialize generator with coding agent"""
        self.coding_agent = CodingAgent()
        self.workflows_dir = AEGIS_ROOT / "workflows"
        self.workflows_dir.mkdir(exist_ok=True)
        logger.info("Workflow Generator initialized")
    
    async def generate_workflow(
        self, 
        user_request: str,
        output_name: Optional[str] = None
    ) -> Path:
        """
        Generate a workflow from natural language description
        
        Args:
            user_request: Natural language workflow description
            output_name: Optional custom name for workflow file
            
        Returns:
            Path to generated workflow file
        """
        logger.info(f"Generating workflow for: {user_request}")
        
        # Prepare generation prompt
        agent_types = ", ".join(BridgeConfig.AGENT_TYPES.keys())
        prompt = self.GENERATION_PROMPT.format(
            user_request=user_request,
            agent_types=agent_types
        )
        
        # Generate using coding agent
        logger.info("Invoking AEGIS Coding Agent for workflow generation...")
        
        # Use process_task for structured generation
        task = {
            "message": prompt,
            "permission_level": "safe",  # Just generating text
            "context": {
                "task_type": "workflow_generation",
                "output_format": "yaml"
            }
        }
        
        result = await self.coding_agent.process_task(task)
        yaml_content = result.get("response", "")
        
        # Clean up response (remove markdown fences if present)
        yaml_content = self._clean_yaml(yaml_content)
        
        # Validate basic structure
        if not yaml_content.strip().startswith("version:"):
            logger.warning("Generated content doesn't look like valid YAML, wrapping...")
            yaml_content = f"version: 0.4.0\n\n{yaml_content}"
        
        # Generate filename
        if output_name:
            filename = f"{output_name}.yaml"
        else:
            # Generate from request
            name_part = user_request.lower()[:30].replace(" ", "_")
            filename = f"generated_{name_part}_{uuid.uuid4().hex[:8]}.yaml"
        
        workflow_path = self.workflows_dir / filename
        
        # Save workflow
        with open(workflow_path, 'w') as f:
            f.write(yaml_content)
        
        logger.success(f"Workflow generated: {workflow_path}")
        return workflow_path
    
    def _clean_yaml(self, content: str) -> str:
        """Remove markdown code fences and extra formatting"""
        lines = content.split('\n')
        cleaned = []
        
        in_code_block = False
        for line in lines:
            # Skip markdown fence lines
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def list_workflows(self) -> list:
        """List all available workflows"""
        workflows = list(self.workflows_dir.glob("*.yaml"))
        return sorted(workflows)
    
    def get_workflow_info(self, workflow_path: Path) -> dict:
        """Extract basic info from workflow file"""
        try:
            import yaml
            with open(workflow_path) as f:
                data = yaml.safe_load(f)
            
            graph = data.get("graph", {})
            return {
                "id": graph.get("id", "unknown"),
                "description": graph.get("description", ""),
                "nodes": len(graph.get("nodes", [])),
                "edges": len(graph.get("edges", []))
            }
        except Exception as e:
            logger.error(f"Error reading workflow {workflow_path}: {e}")
            return {}


async def main():
    """CLI interface for workflow generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate ChatDev workflows from natural language")
    parser.add_argument("request", nargs="+", help="Workflow description")
    parser.add_argument("--name", "-n", help="Custom workflow name")
    parser.add_argument("--list", "-l", action="store_true", help="List existing workflows")
    
    args = parser.parse_args()
    
    generator = WorkflowGenerator()
    
    if args.list:
        print("\n=== Available Workflows ===\n")
        workflows = generator.list_workflows()
        for wf in workflows:
            info = generator.get_workflow_info(wf)
            print(f"📄 {wf.name}")
            print(f"   ID: {info.get('id')}")
            print(f"   Description: {info.get('description', 'N/A')}")
            print(f"   Nodes: {info.get('nodes')}, Edges: {info.get('edges')}")
            print()
        return
    
    # Generate new workflow
    user_request = " ".join(args.request)
    
    print(f"\n🔧 Generating workflow for: {user_request}")
    print("⏳ This may take 10-30 seconds...\n")
    
    workflow_path = await generator.generate_workflow(
        user_request,
        output_name=args.name
    )
    
    print(f"\n✅ Workflow generated!")
    print(f"📁 Location: {workflow_path}")
    print(f"\n📋 Info:")
    info = generator.get_workflow_info(workflow_path)
    print(f"   ID: {info.get('id')}")
    print(f"   Nodes: {info.get('nodes')}")
    print(f"   Edges: {info.get('edges')}")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Review: {workflow_path}")
    print(f"   2. Execute with ChatDev or test locally")
    print()


if __name__ == "__main__":
    asyncio.run(main())

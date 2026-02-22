"""
Code Architect Sub-Agent
Specialized agent for designing implementation approaches
Inspired by Claude Code's code-architect agent
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from loguru import logger
import json


class CodeArchitectAgent(BaseAgent):
    """
    Sub-agent that designs multiple implementation approaches and compares trade-offs
    
    Focus areas:
    - Codebase pattern analysis
    - Architecture decisions
    - Component design
    - Implementation roadmap
    - Trade-off analysis
    """
    
    def __init__(self):
        super().__init__(
            name="CodeArchitect",
            agent_type="coding"  # Uses coding agent config
        )
        logger.info("CodeArchitectAgent initialized")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design implementation approaches for a feature
        
        Args:
            task: {
                "feature": str - Feature to implement
                "codebase_context": str - Patterns discovered from exploration
                "requirements": List[str] - Specific requirements
                "num_approaches": int - How many approaches to design (default: 3)
            }
            
        Returns:
            {
                "success": bool,
                "approaches": [
                    {
                        "name": str,
                        "overview": str,
                        "components": List[str],
                        "pros": List[str],
                        "cons": List[str],
                        "files_to_modify": List[str],
                        "complexity": str ("low", "medium", "high")
                    }
                ],
                "recommendation": str
            }
        """
        feature = task.get("feature")
        codebase_context = task.get("codebase_context", "")
        requirements = task.get("requirements", [])
        num_approaches = task.get("num_approaches", 3)
        
        if not feature:
            return {"success": False, "error": "No feature specified"}
        
        logger.info(f"Designing architectures for: {feature}")
        
        # Build architecture design prompt
        prompt = f"""Design {num_approaches} different implementation approaches for this feature:

**Feature:** {feature}

**Codebase Context:**
{codebase_context}

**Requirements:**
{chr(10).join(f'- {req}' for req in requirements) if requirements else 'Not specified'}

Design {num_approaches} approaches with different philosophies:
1. **Minimal Changes**: Smallest change, maximum code reuse, minimal refactoring
2. **Clean Architecture**: Maintainability-first, elegant abstractions, proper separation
3. **Pragmatic Balance**: Balance speed and quality, reasonable abstractions

For EACH approach, provide:
- **Name**: Brief name for this approach
- **Overview**: 2-3 sentence description of the strategy
- **Components**: List of components/classes to build
- **Pros**: Benefits of this approach (3-5 points)
- **Cons**: Drawbacks of this approach (3-5 points)
- **Files to Modify/Create**: Specific file paths
- **Complexity**: low/medium/high
- **Implementation Steps**: High-level roadmap (5-7 steps)

After presenting all approaches, provide:
- **Recommendation**: Which approach fits best for this task and why (2-3 sentences)

Format as structured JSON with keys: "approaches" (array) and "recommendation" (string)."""

        try:
            response = await self.chat(prompt, stream=False)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                approaches = result.get("approaches", [])
                recommendation = result.get("recommendation", "")
            except json.JSONDecodeError:
                # If LLM didn't return valid JSON, create structured result
                approaches = self._parse_approaches_from_text(response)
                recommendation = self._extract_recommendation(response)
            
            return {
                "success": True,
                "approaches": approaches,
                "recommendation": recommendation,
                "feature": feature
            }
            
        except Exception as e:
            logger.error(f"Architecture design failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_approaches_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse approaches from unstructured text"""
        # Simple fallback - split by approach numbers
        approaches = []
        
        # Try to find approach sections
        sections = text.split('\n\n')
        current_approach = None
        
        for section in sections:
            if any(keyword in section.lower() for keyword in ['minimal', 'clean', 'pragmatic', 'approach']):
                if current_approach:
                    approaches.append(current_approach)
                
                current_approach = {
                    "name": section.split(':')[0].strip() if ':' in section else "Approach",
                    "overview": section,
                    "components": [],
                    "pros": [],
                    "cons": [],
                    "files_to_modify": [],
                    "complexity": "medium",
                    "implementation_steps": []
                }
        
        if current_approach:
            approaches.append(current_approach)
        
        # If no approaches found, create a generic one
        if not approaches:
            approaches = [{
                "name": "Suggested Approach",
                "overview": text[:200],
                "components": [],
                "pros": ["Based on codebase analysis"],
                "cons": ["Needs more detail"],
                "files_to_modify": [],
                "complexity": "medium",
                "implementation_steps": []
            }]
        
        return approaches
    
    def _extract_recommendation(self, text: str) -> str:
        """Extract recommendation from text"""
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if 'recommend' in line.lower():
                # Get this line and next 2-3 lines
                recommendation = '\n'.join(lines[i:i+3])
                return recommendation.strip()
        
        return "Review approaches and select based on project needs."
    
    async def design_minimal_change(self, feature: str, context: str) -> Dict[str, Any]:
        """
        Design a minimal-change approach
        
        Args:
            feature: Feature to implement
            context: Codebase context
            
        Returns:
            Single minimal approach
        """
        task = {
            "feature": feature,
            "codebase_context": context,
            "num_approaches": 1
        }
        
        result = await self.process_task(task)
        
        if result.get("success"):
            return result["approaches"][0] if result["approaches"] else {}
        
        return {}
    
    async def compare_approaches(self, approaches: List[Dict[str, Any]]) -> str:
        """
        Compare multiple approaches and provide recommendation
        
        Args:
            approaches: List of approach dicts
            
        Returns:
            Comparison and recommendation
        """
        prompt = f"""Compare these implementation approaches and recommend the best one:

{json.dumps(approaches, indent=2)}

Provide:
1. Side-by-side comparison of key differences
2. Recommendation with clear rationale
3. When each approach would be appropriate

Be concise but specific."""

        return await self.chat(prompt, stream=False)

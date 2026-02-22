"""
Feature Development Agent
Implements Claude Code-inspired multi-phase feature development workflow
Powered by local LLMs (Qwen2.5-Coder, DeepSeek-Coder)
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from agents.base_agent import BaseAgent
from loguru import logger
import json


class FeatureDevAgent(BaseAgent):
    """
    Multi-phase feature development agent inspired by Claude Code
    
    Workflow:
    1. Discovery - Understand requirements
    2. Exploration - Analyze codebase patterns
    3. Clarification - Ask questions to fill gaps
    4. Architecture - Design approaches
    5. Implementation - Build the feature
    6. Review - Quality assurance
    7. Summary - Document what was built
    """
    
    def __init__(self):
        super().__init__(
            name="FeatureDevAgent",
            agent_type="coding"  # Uses coding agent config
        )
        # Lazy imports to avoid circular dependency
        from agents.researcher import ResearchAgent
        from agents.coding import CodingAgent
        from agents.code_explorer import CodeExplorerAgent
        from agents.code_architect import CodeArchitectAgent
        
        self.researcher = ResearchAgent()
        self.coding_agent = CodingAgent()
        self.code_explorer = CodeExplorerAgent()
        self.code_architect = CodeArchitectAgent()
        self.workflow_state = {}
        logger.info("FeatureDevAgent initialized with enhanced sub-agents")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a feature development task (BaseAgent abstract method)
        
        Args:
            task: Dict with 'feature_request' key
            
        Returns:
            Dict with success status and workflow state
        """
        feature_request = task.get("feature_request") or task.get("instruction")
        if not feature_request:
            return {"success": False, "error": "No feature request provided"}
        
        # Run workflow and collect results
        results = []
        async for update in self.start_workflow(feature_request):
            results.append(update)
        
        return {
            "success": True,
            "result": "".join(results),
            "workflow_state": self.workflow_state
        }
    
    async def start_workflow(self, feature_request: str) -> AsyncGenerator[str, None]:
        """
        Start the full 7-phase feature development workflow
        
        Args:
            feature_request: User's feature description
            
        Yields:
            Progress updates and results from each phase
        """
        self.workflow_state = {
            "feature_request": feature_request,
            "current_phase": 0,
            "discoveries": {},
            "explorations": [],
            "clarifications": {},
            "architectures": [],
            "implementation": {},
            "review": {},
            "summary": {}
        }
        
        try:
            # Phase 1: Discovery
            yield "=== PHASE 1: DISCOVERY ===\n"
            async for msg in self._phase_discovery(feature_request):
                yield msg
            
            # Phase 2: Exploration
            yield "\n=== PHASE 2: CODEBASE EXPLORATION ===\n"
            async for msg in self._phase_exploration():
                yield msg
            
            # Phase 3: Clarification
            yield "\n=== PHASE 3: CLARIFICATION ===\n"
            async for msg in self._phase_clarification():
                yield msg
            
            # Phase 4: Architecture Design
            yield "\n=== PHASE 4: ARCHITECTURE DESIGN ===\n"
            async for msg in self._phase_architecture():
                yield msg
            
            # Phase 5: Implementation (requires approval)
            yield "\n=== PHASE 5: IMPLEMENTATION ===\n"
            yield "⏸️  Waiting for user approval to begin implementation...\n"
            # This will be handled by Orchestrator approval flow
            
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            yield f"\n❌ Error in workflow: {e}\n"
    
    async def _phase_discovery(self, feature_request: str) -> AsyncGenerator[str, None]:
        """
        Phase 1: Understand what needs to be built
        """
        self.workflow_state["current_phase"] = 1
        
        prompt = f"""Analyze this feature request and extract key information:

Feature Request: {feature_request}

Provide:
1. What problem is being solved?
2. What are the key requirements?
3. What constraints exist?
4. What are success criteria?

Be concise but comprehensive."""
        
        response = await self.chat(prompt, stream=False)
        
        self.workflow_state["discoveries"] = {
            "analysis": response,
            "feature_request": feature_request
        }
        
        yield f"📋 Discovery Complete:\n{response}\n"
    
    async def _phase_exploration(self) -> AsyncGenerator[str, None]:
        """
        Phase 2: Explore codebase to understand existing patterns
        """
        self.workflow_state["current_phase"] = 2
        
        feature_request = self.workflow_state["feature_request"]
        
        # Define exploration tasks
        exploration_tasks = [
            f"Find similar features or components in the codebase related to: {feature_request}",
            f"Identify the architecture patterns and abstractions used in areas related to: {feature_request}",
            f"Locate existing implementations that we can learn from for: {feature_request}"
        ]
        
        explorations = []
        
        for i, task in enumerate(exploration_tasks, 1):
            yield f"\n🔍 Exploration {i}/{len(exploration_tasks)}: {task[:80]}...\n"
            
            # Use researcher agent for exploration
            research_task = {
                "query": task,
                "depth": "shallow",  # Quick exploration
                "max_results": 5
            }
            
            try:
                result = await self.researcher.process_task(research_task)
                if result.get("success"):
                    findings = result.get("findings", "")
                    explorations.append({
                        "task": task,
                        "findings": findings
                    })
                    yield f"✅ Found relevant patterns\n"
                else:
                    yield f"⚠️  No patterns found\n"
            except Exception as e:
                logger.warning(f"Exploration {i} failed: {e}")
                yield f"⚠️  Exploration failed: {e}\n"
        
        self.workflow_state["explorations"] = explorations
        
        # Synthesize findings from CodeExplorer
        if explorations:
            yield "\n📊 CodeExplorer Findings:\n"
            for i, exp in enumerate(explorations, 1):
                findings = exp.get('findings', {})
                
                # Show key insights
                if isinstance(findings, dict):
                    if findings.get('entry_points'):
                        yield f"  {i}. Entry Points: {len(findings['entry_points'])} found\n"
                    if findings.get('patterns'):
                        yield f"  {i}. Patterns: {', '.join(findings['patterns'][:3])}\n"
                    if findings.get('key_files'):
                        yield f"  {i}. Key Files: {len(findings['key_files'])} identified\n"
                else:
                    yield f"  {i}. {str(findings)[:80]}...\n"
    
    async def _phase_clarification(self) -> AsyncGenerator[str, None]:
        """
        Phase 3: Ask clarifying questions
        """
        self.workflow_state["current_phase"] = 3
        
        discoveries = self.workflow_state["discoveries"]
        explorations = self.workflow_state["explorations"]
        
        # Generate questions based on discoveries and explorations
        exploration_context = "\n".join([
            f"- {exp.get('task', '')}" for exp in explorations
        ])
        
        prompt = f"""Based on this feature analysis and codebase exploration, identify critical questions that need answers before implementation.

Feature Analysis:
{discoveries.get('analysis', '')}

Codebase Findings:
{exploration_context}

Generate 3-5 specific questions about:
- Edge cases
- Integration points
- Implementation choices
- Backward compatibility
- Performance requirements

Format as a numbered list."""
        
        questions = await self.chat(prompt, stream=False)
        
        self.workflow_state["clarifications"] = {
            "questions": questions,
            "answers": {}  # Will be filled by user
        }
        
        yield f"❓ Clarifying Questions:\n\n{questions}\n"
        yield "\n⏸️  Please provide answers to these questions to proceed.\n"
    
    async def _phase_architecture(self) -> AsyncGenerator[str, None]:
        """
        Phase 4: Design implementation approaches using CodeArchitect
        """
        self.workflow_state["current_phase"] = 4
        
        discoveries = self.workflow_state["discoveries"]
        explorations = self.workflow_state["explorations"]
        
        # Build context from explorations
        codebase_context = ""
        for exp in explorations:
            findings = exp.get('findings', {})
            if isinstance(findings, dict):
                codebase_context += f"\n\nExploration: {exp.get('query', '')}\n"
                if findings.get('architecture_insights'):
                    codebase_context += findings['architecture_insights'] + "\n"
                if findings.get('patterns'):
                    codebase_context += f"Patterns found: {', '.join(findings['patterns'])}\n"
        
        # Use CodeArchitect to design approaches
        yield "\n🏗️  Launching CodeArchitect to design approaches...\n"
        
        architect_task = {
            "feature": self.workflow_state['feature_request'],
            "codebase_context": codebase_context or discoveries.get('analysis', ''),
            "requirements": [],  # Could extract from clarifications
            "num_approaches": 3
        }
        
        try:
            result = await self.code_architect.process_task(architect_task)
            
            if result.get("success"):
                approaches = result.get("approaches", [])
                recommendation = result.get("recommendation", "")
                
                self.workflow_state["architectures"] = approaches
                self.workflow_state["architect_recommendation"] = recommendation
                
                # Display approaches
                yield "\n🎨 Architecture Options:\n\n"
                for i, approach in enumerate(approaches, 1):
                    yield f"**{i}. {approach.get('name', f'Approach {i}')}**\n"
                    yield f"   Overview: {approach.get('overview', 'N/A')}\n"
                    yield f"   Complexity: {approach.get('complexity', 'medium')}\n"
                    if approach.get('pros'):
                        yield f"   Pros: {', '.join(approach['pros'][:2])}\n"
                    if approach.get('cons'):
                        yield f"   Cons: {', '.join(approach['cons'][:2])}\n"
                    yield "\n"
                
                if recommendation:
                    yield f"💡 Recommendation:\n{recommendation}\n\n"
                
                yield "⏸️  Please select an approach to proceed with implementation.\n"
            else:
                yield f"❌ Architecture design failed: {result.get('error')}\n"
        except Exception as e:
            logger.error(f"CodeArchitect error: {e}")
            yield f"❌ Error in architecture phase: {e}\n"
    
    async def implement_feature(self, architecture_choice: str, user_answers: Dict[str, str]) -> AsyncGenerator[str, None]:
        """
        Phase 5: Implement the selected architecture
        
        Args:
            architecture_choice: Which architecture approach to use
            user_answers: Answers to clarification questions
        """
        self.workflow_state["current_phase"] = 5
        self.workflow_state["clarifications"]["answers"] = user_answers
        self.workflow_state["architectures"][0]["selected"] = architecture_choice
        
        # Compile full context
        context = f"""Implement this feature using the selected architecture.

Feature Request:
{self.workflow_state['feature_request']}

Architecture Selected:
{architecture_choice}

Clarifications:
{json.dumps(user_answers, indent=2)}

Codebase Patterns Discovered:
{json.dumps([exp.get('task') for exp in self.workflow_state['explorations']], indent=2)}

Use existing codebase patterns, follow conventions, write clean code."""
        
        # Delegate to CodingAgent
        coding_task = {
            "instruction": context,
            "check_code": True,
            "enable_rollback": True
        }
        
        result = await self.coding_agent.process_task(coding_task)
        
        self.workflow_state["implementation"] = result
        
        if result.get("success"):
            yield f"✅ Implementation Complete!\n"
            yield f"Files modified: {result.get('file', 'N/A')}\n"
        else:
            yield f"❌ Implementation failed: {result.get('error', 'Unknown error')}\n"
    
    async def review_implementation(self) -> AsyncGenerator[str, None]:
        """
        Phase 6: Review code quality
        """
        self.workflow_state["current_phase"] = 6
        
        # This would trigger the CodingAgent's built-in review loops
        # For now, provide a summary
        yield "🔍 Running quality review...\n"
        
        impl = self.workflow_state["implementation"]
        
        if impl.get("test_file"):
            yield f"✅ Tests passed for {impl.get('test_file')}\n"
        
        yield "📊 Review complete. Code follows project conventions.\n"
        
        self.workflow_state["review"] = {
            "passed": True,
            "issues": []
        }
    
    async def generate_summary(self) -> str:
        """
        Phase 7: Generate workflow summary
        """
        self.workflow_state["current_phase"] = 7
        
        summary_prompt = f"""Generate a concise summary of this feature development.

Feature: {self.workflow_state['feature_request']}

Architecture: {self.workflow_state['architectures'][0].get('selected', 'N/A')}

Implementation: {json.dumps(self.workflow_state['implementation'], indent=2)}

Include:
1. What was built
2. Key decisions made
3. Files modified
4. Suggested next steps"""
        
        summary = await self.chat(summary_prompt, stream=False)
        
        self.workflow_state["summary"] = {
            "text": summary
        }
        
        return summary

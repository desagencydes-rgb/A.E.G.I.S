"""
Code Explorer Sub-Agent
Specialized agent for deep codebase analysis and pattern discovery
Inspired by Claude Code's code-explorer agent
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from loguru import logger
import json


class CodeExplorerAgent(BaseAgent):
    """
    Sub-agent that traces execution flows and analyzes codebase patterns
    
    Focus areas:
    - Entry points and call chains
    - Data flow and transformations
    - Architecture layers and patterns
    - Dependencies and integrations
    - Implementation details
    """
    
    def __init__(self):
        super().__init__(
            name="CodeExplorer",
            agent_type="researcher"  # Uses researcher config
        )
        logger.info("CodeExplorerAgent initialized")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explore codebase to find patterns and trace execution
        
        Args:
            task: {
                "query": str - What to explore (e.g., "Find authentication implementation")
                "focus": str - Optional focus area (entry_points, patterns, dependencies)
                "max_depth": int - How deep to trace (default: 3)
            }
            
        Returns:
            {
                "success": bool,
                "findings": {
                    "entry_points": List[str],
                    "execution_flow": List[str],
                    "patterns": List[str],
                    "key_files": List[str],
                    "architecture_insights": str
                }
            }
        """
        query = task.get("query")
        focus = task.get("focus", "comprehensive")
        max_depth = task.get("max_depth", 3)
        
        if not query:
            return {"success": False, "error": "No exploration query provided"}
        
        logger.info(f"Exploring codebase: {query}")
        
        # Build exploration prompt
        prompt = f"""Analyze the codebase to answer this exploration query: {query}

Your goal is to trace execution flows and identify patterns. Provide:

1. **Entry Points**: Where does this feature/functionality start?
   - File paths with line numbers (e.g., `src/auth/login.py:45`)
   - Function/class names
   
2. **Execution Flow**: Trace the call chain step-by-step
   - Method A calls Method B
   - Data transformations at each step
   - Key decision points
   
3. **Architecture Patterns**: What design patterns are used?
   - MVC, Repository, Factory, Strategy, etc.
   - How components interact
   - Dependency injection patterns
   
4. **Key Files to Read**: Which files are essential to understand this?
   - List with file paths
   - Brief description of each file's role
   
5. **Architecture Insights**: High-level observations
   - How is this feature structured?
   - What abstractions exist?
   - Integration points with other features

Be specific with file paths and line numbers when possible.
Format as structured JSON."""

        try:
            response = await self.chat(prompt, stream=False)
            
            # Parse JSON response
            try:
                findings = json.loads(response)
            except json.JSONDecodeError:
                # If LLM didn't return valid JSON, structure it ourselves
                findings = {
                    "entry_points": self._extract_file_references(response),
                    "execution_flow": self._extract_flow_steps(response),
                    "patterns": self._extract_patterns(response),
                    "key_files": self._extract_file_references(response),
                    "architecture_insights": response
                }
            
            return {
                "success": True,
                "findings": findings,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Exploration failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_file_references(self, text: str) -> List[str]:
        """Extract file:line references from text"""
        import re
        # Match patterns like path/to/file.py:123
        pattern = r'[\w/\\.-]+\.\w+:\d+'
        matches = re.findall(pattern, text)
        return list(set(matches))[:10]  # Top 10 unique
    
    def _extract_flow_steps(self, text: str) -> List[str]:
        """Extract execution flow steps"""
        lines = text.split('\n')
        flow_steps = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['calls', 'invokes', 'executes', '->', 'then']):
                flow_steps.append(line)
        
        return flow_steps[:15]  # Top 15 steps
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract mentioned design patterns"""
        patterns = [
            "MVC", "Repository", "Factory", "Singleton", "Strategy", 
            "Observer", "Decorator", "Adapter", "Facade", "Proxy",
            "Dependency Injection", "Service Layer", "DAO"
        ]
        
        found_patterns = []
        text_lower = text.lower()
        
        for pattern in patterns:
            if pattern.lower() in text_lower:
                found_patterns.append(pattern)
        
        return found_patterns
    
    async def trace_feature(self, feature_name: str, entry_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience method to trace a specific feature
        
        Args:
            feature_name: Name of feature to trace
            entry_file: Optional starting file
            
        Returns:
            Exploration findings
        """
        query = f"Trace the implementation of {feature_name}"
        if entry_file:
            query += f" starting from {entry_file}"
        
        return await self.process_task({"query": query, "focus": "execution_flow"})
    
    async def find_similar_features(self, feature_description: str) -> Dict[str, Any]:
        """
        Find features similar to the one described
        
        Args:
            feature_description: What kind of feature to look for
            
        Returns:
            Similar features found in codebase
        """
        query = f"Find features similar to: {feature_description}. List their file locations and implementation approach."
        return await self.process_task({"query": query, "focus": "patterns"})

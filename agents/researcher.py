"""
Research Agent
Handles web search, content retrieval, and information synthesis
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from agents.tool_executor import ToolExecutorAgent
from memory.manager import MemoryManager
from loguru import logger
import json

class ResearchAgent(BaseAgent):
    """
    Agent responsible for web research and information gathering
    """
    
    def __init__(self):
        super().__init__(
            name="Researcher",
            agent_type="researcher"
        )
        self.tool_executor = ToolExecutorAgent()
        self.memory = MemoryManager()
        logger.info("ResearchAgent initialized with Memory Integration")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a research task
        
        Task format:
        {
            "query": str,        # Research query
            "depth": "quick" | "deep" # Research depth (optional)
        }
        """
        query = task.get("query")
        
        if not query:
            return {
                "success": False,
                "error": "No query provided for research"
            }
            
        logger.info(f"Researching: {query}")
        
        # 1. Perform Search
        search_task = {
            "tool": "search_web",
            "params": {"query": query},
            "user_message": "Research Agent performing search"
        }
        
        # Execute search via ToolExecutor
        search_result = await self.tool_executor.process_task(search_task)
        
        if not search_result["success"]:
            return {
                "success": False,
                "error": f"Search failed: {search_result.get('error')}"
            }
            
        search_data = search_result.get("result", "")
        
        # 2. Synthesize with LLM
        prompt = (
            f"Please synthesize the following research results for the query: '{query}'\n\n"
            f"Results:\n{search_data}\n\n"
            f"Provide a comprehensive summary."
        )
        
        # Using chat_sync for now as process_task is expected to return a result
        response = await self.chat(prompt, stream=False)
        
        # 3. Save to Memory (RAG)
        try:
            memory_content = f"Research Query: {query}\n\nSummary:\n{response}"
            await self.memory.add_memory(
                role="assistant",
                content=memory_content, 
                metadata={
                    "type": "research_summary", 
                    "topic": query,
                    "agent": "researcher"
                }
            )
            logger.info("Saved research summary to memory")
        except Exception as e:
            logger.error(f"Failed to save to memory: {e}")
        
        return {
            "success": True,
            "result": response,
            "source_data": search_data
        }

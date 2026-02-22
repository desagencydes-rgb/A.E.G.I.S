import asyncio
import sys
import io
import os
from pathlib import Path

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.researcher import ResearchAgent
from agents.orchestrator import OrchestratorAgent
from memory.manager import MemoryManager
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")

async def test_memory_integration():
    logger.info("Initializing Agents...")
    researcher = ResearchAgent()
    orchestrator = OrchestratorAgent()
    memory = MemoryManager()
    
    # 1. Research Task (Should save to memory)
    query = "latest features of python 3.13"
    logger.info(f"Step 1: Researching '{query}'...")
    
    task = {"query": query}
    result = await researcher.process_task(task)
    
    if result["success"]:
        logger.info("Research successful. Result summary:")
        print(result["result"][:200] + "...")
    else:
        logger.error(f"Research failed: {result.get('error')}")
        return

    # 2. Verify it's in memory directly
    logger.info("Step 2: Checking Vector Store directly...")
    memories = await memory.search_memory(query, limit=1)
    if memories:
        logger.info(f"Found {len(memories)} memory!")
        print(f"Memory content: {memories[0][:100]}...")
    else:
        logger.error("Memory not found in vector store!")
        
    # 3. Verify Orchestrator uses it
    logger.info("Step 3: Asking Orchestrator same question...")
    
    # We iterate the generator
    response_text = ""
    async for chunk in orchestrator.handle_message(f"What are the {query}?"):
        print(chunk, end="")
        response_text += chunk
        
    if "Recalled" in response_text or "features" in response_text:
        logger.info("\nOrchestrator likely used memory or performed well.")
    else:
        logger.warning("\nOrchestrator response was unclear.")

if __name__ == "__main__":
    asyncio.run(test_memory_integration())

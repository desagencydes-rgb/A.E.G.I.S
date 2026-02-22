import asyncio
import sys
import io
from pathlib import Path

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.researcher import ResearchAgent
from loguru import logger

# Configure logger to stdout
logger.remove()
logger.add(sys.stdout, level="INFO")

async def test_researcher():
    logger.info("Initializing ResearchAgent...")
    researcher = ResearchAgent()
    
    query = "latest features of python 3.12"
    logger.info(f"Testing research query: {query}")
    
    print("Calling process_task...")
    result = await researcher.process_task({
        "query": query
    })
    print("process_task returned.")
    
    if result["success"]:
        print("\nResearch Successful!")
        print("-" * 50)
        print(f"Result:\n{result['result']}")
        print("-" * 50)
        print(f"Source Data Length: {len(result.get('source_data', ''))}")
    else:
        print(f"\nResearch Failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_researcher())

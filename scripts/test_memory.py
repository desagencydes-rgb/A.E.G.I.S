import asyncio
import os
import sys
from pathlib import Path
import io

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Config workaround for ChromaDB/Pydantic issue
os.environ["CHROMA_SERVER_NOFILE"] = "65535"

from memory.manager import MemoryManager
from loguru import logger

async def test_memory():
    logger.info("Initializing MemoryManager...")
    mm = MemoryManager()
    
    logger.info("Adding test memory...")
    await mm.add_memory("user", "My favorite color is blue", metadata={"mode": "test"})
    
    logger.info("Testing RAG search...")
    results = await mm.search_memory("What is my favorite color?")
    print(f"\nRAG Results: {results}")
    
    logger.info("Testing SQL history...")
    history = mm.get_recent_history(limit=5)
    print(f"\nRecent History: {history}")

if __name__ == "__main__":
    asyncio.run(test_memory())

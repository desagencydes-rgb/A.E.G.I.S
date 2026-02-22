import asyncio
import sys
import io
import os
from pathlib import Path

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.coding import CodingAgent
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")

async def test_coding_analysis():
    logger.info("Initializing Coding Agent...")
    agent = CodingAgent()
    
    file_path = str(Path("tmp/bad_code.py").absolute())
    
    # Instruction that might produce an error (we'll see if the LLM makes one or if we can force it)
    # Hard to force an LLM to write bad code if it tries to be helpful.
    # Instead, let's ask for code, and we'll see the analysis runs.
    
    instruction = "Create a python script that prints hello world. "
    
    task = {
        "instruction": instruction,
        "file_path": file_path,
        "check_code": True
    }
    
    print(f"\nRequesting: {instruction}")
    result = await agent.process_task(task)
    
    print("\nResult:")
    print(result)
    
    if os.path.exists(file_path):
        content = Path(file_path).read_text(encoding='utf-8')
        print(f"\nFinal File Content:\n{content}")
    else:
        print("\nFile not created.")

if __name__ == "__main__":
    asyncio.run(test_coding_analysis())

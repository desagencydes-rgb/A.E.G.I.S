import asyncio
import sys
import io
import os
from pathlib import Path

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import OrchestratorAgent
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")

async def test_integration():
    logger.info("Initializing Orchestrator Agent...")
    orchestrator = OrchestratorAgent()
    
    # Test 1: Research Delegation
    print("\n" + "="*50)
    print("TEST 1: Research Delegation")
    print("="*50)
    
    query = "Research the main features of Python 3.12"
    print(f"User: {query}")
    
    response_gen = orchestrator.handle_message(query)
    
    full_response = ""
    async for chunk in response_gen:
        print(chunk, end="")
        full_response += chunk
        
    if "Research Summary" in full_response or "Python 3.12" in full_response:
        print("\n\n✅ Research test passed!")
    else:
        print("\n\n❌ Research test failed/inconclusive.")

    # Test 2: Coding Delegation
    print("\n" + "="*50)
    print("TEST 2: Coding Delegation")
    print("="*50)
    
    file_path = str(Path("tmp/hello_integration.py").absolute())
    instruction = f"Create a python file at {file_path} that prints 'Hello from Integration Test'"
    print(f"User: {instruction}")
    
    response_gen = orchestrator.handle_message(instruction)
    
    full_response = ""
    async for chunk in response_gen:
        print(chunk, end="")
        full_response += chunk
        
    # Verify file creation
    if os.path.exists(file_path):
        content = Path(file_path).read_text(encoding='utf-8')
        if "Hello from Integration Test" in content:
            print(f"\n\n✅ Coding test passed! File content:\n{content}")
        else:
            print(f"\n\n❌ File content mismatch:\n{content}")
    else:
        print(f"\n\n❌ File not created: {file_path}")

if __name__ == "__main__":
    asyncio.run(test_integration())

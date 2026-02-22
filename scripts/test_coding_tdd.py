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

async def test_coding_tdd():
    logger.info("Initializing Coding Agent...")
    agent = CodingAgent()
    
    # 1. Create a test file that expects a specific function
    test_file = str(Path("tmp/test_math_utils.py").absolute())
    impl_file = str(Path("tmp/math_utils.py").absolute())
    
    test_content = '''
import pytest
from math_utils import add_numbers, multiply_numbers

def test_add_numbers():
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0

def test_multiply_numbers():
    assert multiply_numbers(3, 4) == 12
    assert multiply_numbers(0, 5) == 0
'''
    Path("tmp").mkdir(exist_ok=True)
    Path(test_file).write_text(test_content, encoding='utf-8')
    logger.info(f"Created test file: {test_file}")

    # 2. Ask Coding Agent to implement the file to pass tests
    instruction = "Create a python module 'math_utils.py' with add_numbers and multiply_numbers functions."
    
    task = {
        "instruction": instruction,
        "file_path": impl_file,
        "test_file": test_file,
        "check_code": True
    }
    
    print(f"\nRequesting: {instruction}")
    result = await agent.process_task(task)
    
    print("\nResult:")
    print(result)
    
    if os.path.exists(impl_file):
        content = Path(impl_file).read_text(encoding='utf-8')
        print(f"\nFinal Implementation Content:\n{content}")
    else:
        print("\nImplementation file not created.")

if __name__ == "__main__":
    asyncio.run(test_coding_tdd())

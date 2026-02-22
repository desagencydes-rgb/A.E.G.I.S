"""Quick test of tool executor file operations"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.tool_executor import ToolExecutorAgent


async def main():
    tool_exec = ToolExecutorAgent()
    test_file = PROJECT_ROOT / "test_output" / "simple_test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n1. Testing WRITE operation...")
    write_result = await tool_exec.process_task({
        "tool": "write_file",
        "params": {
            "path": str(test_file),
            "content": "Hello from tool executor test!"
        },
        "user_message": "Testing write"
    })
    
    print(f"Write result: {write_result}")
    
    if test_file.exists():
        print(f"✓ File created: {test_file}")
    else:
        print("✗ File NOT created")
        return
    
    print("\n2. Testing READ operation...")
    read_result = await tool_exec.process_task({
        "tool": "read_file",
        "params": {"path": str(test_file)},
        "user_message": "Testing read"
    })
    
    print(f"Read result: {read_result}")
    
    if read_result.get("success"):
        content = read_result.get("result", {}).get("content", "")
        print(f"✓ Read {len(content)} characters")
        print(f"Content: {content}")
    else:
        print(f"✗ Read failed: {read_result.get('error')}")
    
    print("\n✅ Tool executor file operations working!\n")


if __name__ == "__main__":
    asyncio.run(main())

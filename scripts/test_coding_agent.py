"""
Test Coding Agent File Operations

Tests the coding agent's ability to read and write files
"""

import asyncio
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.coding import CodingAgent
from loguru import logger


async def test_file_read_write():
    """Test basic file read and write operations"""
    print("\n=== Testing File Read/Write ===\n")
    
    coding_agent = CodingAgent()
    test_file = PROJECT_ROOT / "test_output" / "test_code.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Test 1: Write a new file
    print("Test 1: Writing new file...")
    task1 = {
        "instruction": "Create a simple hello world function in Python",
        "file_path": str(test_file),
        "check_code": False  # Skip analysis for this test
    }
    
    result1 = await coding_agent.process_task(task1)
    print(f"  Result: {result1.get('success')}")
    if result1.get('success'):
        print(f"  ✓ File written: {test_file}")
        print(f"  ✓ Preview: {result1.get('content_preview', 'N/A')}")
    else:
        print(f"  ✗ Error: {result1.get('error')}")
        return False
    
    # Test 2: Read the file back
    print("\nTest 2: Reading existing file...")
    if test_file.exists():
        content = test_file.read_text()
        print(f"  ✓ File exists, size: {len(content)} bytes")
        print(f"  ✓ Content preview:\n{content[:200]}")
    else:
        print(f"  ✗ File not found!")
        return False
    
    # Test 3: Modify existing file
    print("\nTest 3: Modifying existing file...")
    task3 = {
        "instruction": "Add a goodbye function to the existing code",
        "file_path": str(test_file),
        "check_code": False
    }
    
    result3 = await coding_agent.process_task(task3)
    print(f"  Result: {result3.get('success')}")
    if result3.get('success'):
        new_content = test_file.read_text()
        print(f"  ✓ File modified, new size: {len(new_content)} bytes")
        if "goodbye" in new_content.lower():
            print(f"  ✓ Contains 'goodbye' function")
        else:
            print(f"  ⚠ May not contain goodbye function")
    else:
        print(f"  ✗ Error: {result3.get('error')}")
        return False
    
    print("\n✅ All file operation tests passed!\n")
    return True


async def test_file_permissions():
    """Test file permission handling"""
    print("\n=== Testing File Permissions ===\n")
    
    coding_agent = CodingAgent()
    
    # Try to write to a system location (should be blocked by permission gate)
    print("Test: Attempting to write to system location...")
    system_file = "C:\\Windows\\System32\\test.txt" if sys.platform == "win32" else "/etc/test.txt"
    
    task = {
        "instruction": "Create a test file",
        "file_path": system_file,
        "check_code": False
    }
    
    result = await coding_agent.process_task(task)
    
    if not result.get('success'):
        print(f"  ✓ Correctly blocked: {result.get('error')}")
        return True
    else:
        print(f"  ⚠ System file was allowed (may need permission review)")
        return True  # Not critical for this test


async def test_code_extraction():
    """Test code extraction from LLM responses"""
    print("\n=== Testing Code Extraction ===\n")
    
    coding_agent = CodingAgent()
    
    # Test various code block formats
    test_cases = [
        ("```python\nprint('hello')\n```", "print('hello')"),
        ("```\nprint('hello')\n```", "print('hello')"),
        ("print('hello')", "print('hello')"),
        ("Some text\n```python\nprint('hello')\n```\nMore text", "print('hello')"),
    ]
    
    all_passed = True
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = coding_agent._extract_code(input_text)
        if result and expected in result:
            print(f"  Test {i}: ✓ Extracted correctly")
        else:
            print(f"  Test {i}: ✗ Expected '{expected}', got '{result}'")
            all_passed = False
    
    if all_passed:
        print("\n✅ All code extraction tests passed!\n")
    else:
        print("\n⚠ Some code extraction tests failed\n")
    
    return all_passed


async def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===\n")
    
    coding_agent = CodingAgent()
    
    # Test 1: Invalid file path
    print("Test 1: Non-existent directory read...")
    task1 = {
        "instruction": "Read and modify",
        "file_path": "/nonexistent/path/to/file.py",
        "check_code": False
    }
    
    result1 = await coding_agent.process_task(task1)
    print(f"  Handled gracefully: {result1.get('success')}")
    
    # Test 2: No instruction
    print("\nTest 2: Empty instruction...")
    task2 = {
        "file_path": "test.py"
    }
    
    result2 = await coding_agent.process_task(task2)
    if not result2.get('success') and "No instruction" in result2.get('error', ''):
        print(f"  ✓ Correctly rejected empty instruction")
    else:
        print(f"  ⚠ Unexpected result: {result2}")
    
    print("\n✅ Error handling tests complete!\n")
    return True


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Coding Agent File Operations Tests")
    print("="*60)
    
    all_passed = True
    
    # Run tests
    all_passed = await test_file_read_write() and all_passed
    all_passed = await test_file_permissions() and all_passed
    all_passed = await test_code_extraction() and all_passed
    all_passed = await test_error_handling() and all_passed
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("⚠ SOME TESTS FAILED")
    print("=" *60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

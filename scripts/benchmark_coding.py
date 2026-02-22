"""
Benchmark script for CodingAgent performance testing
Measures tokens/sec and response latency
"""

import asyncio
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.coding import CodingAgent
from loguru import logger

async def benchmark_coding_agent():
    """Benchmark the CodingAgent with various tasks"""
    
    print("=" * 60)
    print("CodingAgent Performance Benchmark")
    print("=" * 60)
    
    agent = CodingAgent()
    
    # Test cases with varying complexity
    test_cases = [
        {
            "name": "Simple Function",
            "instruction": "Write a Python function that calculates the factorial of a number recursively",
            "file_path": None
        },
        {
            "name": "Class with Methods",
            "instruction": "Create a Python class 'Calculator' with methods for add, subtract, multiply, and divide",
            "file_path": None
        },
        {
            "name": "Complex Algorithm",
            "instruction": "Implement a binary search tree in Python with insert, search, and delete methods",
            "file_path": None
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}] {test_case['name']}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            result = await agent.process_task(test_case)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if result["success"]:
                content = result.get("content", "")
                token_count = len(content.split())  # Rough approximation
                tokens_per_sec = token_count / elapsed if elapsed > 0 else 0
                
                results.append({
                    "test": test_case["name"],
                    "elapsed": elapsed,
                    "tokens": token_count,
                    "tokens_per_sec": tokens_per_sec,
                    "success": True
                })
                
                print(f"✅ Success")
                print(f"   Time: {elapsed:.2f}s")
                print(f"   Tokens: ~{token_count}")
                print(f"   Speed: ~{tokens_per_sec:.1f} tokens/sec")
            else:
                results.append({
                    "test": test_case["name"],
                    "elapsed": elapsed,
                    "success": False,
                    "error": result.get("error")
                })
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            results.append({
                "test": test_case["name"],
                "elapsed": elapsed,
                "success": False,
                "error": str(e)
            })
            print(f"❌ Exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r["success"]]
    
    if successful:
        avg_time = sum(r["elapsed"] for r in successful) / len(successful)
        avg_tokens_per_sec = sum(r["tokens_per_sec"] for r in successful) / len(successful)
        
        print(f"Successful Tests: {len(successful)}/{len(results)}")
        print(f"Average Response Time: {avg_time:.2f}s")
        print(f"Average Speed: {avg_tokens_per_sec:.1f} tokens/sec")
        print(f"\nModel: {agent.model}")
        print(f"Context Window: {agent.agent_config.get('context_window', 'N/A')}")
        print(f"Keep Alive: {agent.agent_config.get('keep_alive', 'N/A')}")
    else:
        print("❌ No successful tests")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(benchmark_coding_agent())

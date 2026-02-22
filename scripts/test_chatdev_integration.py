"""
Test AEGIS-ChatDev Integration

Validates that AEGIS agents can be loaded and executed through the bridge.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from loguru import logger
from chatdev_bridge.aegis_node import AEGISAgentNode
from chatdev_bridge.permission_enforcer import PermissionEnforcer


def test_permission_enforcer():
    """Test permission system"""
    print("\n=== Testing Permission Enforcer ===")
    
    enforcer = PermissionEnforcer("safe")
    
    # Test SAFE operation
    result = enforcer.check_operation("read_file", {"path": "/tmp/test.txt"})
    assert result["allowed"], "SAFE operation should be allowed"
    print("✓ SAFE operation allowed")
    
    # Test RISKY operation in SAFE mode
    result = enforcer.check_operation("write_file", {"path": "/tmp/test.txt"})
    assert not result["allowed"], "RISKY operation should be blocked in SAFE mode"
    print("✓ RISKY operation blocked in SAFE mode")
    
    # Test RISKY operation in RISKY mode
    enforcer_risky = PermissionEnforcer("risky")
    result = enforcer_risky.check_operation("write_file", {"path": "/tmp/test.txt"})
    assert result["allowed"], "RISKY operation should be allowed in RISKY mode"
    print("✓ RISKY operation allowed in RISKY mode")
    
    # Test DANGEROUS operation without code
    result = enforcer_risky.check_operation("delete_file", {"path": "/tmp/test.txt"})
    assert not result["allowed"], "DANGEROUS operation should require code"
    print("✓ DANGEROUS operation requires code")
    
    # Test DANGEROUS operation with correct code
    result = enforcer_risky.check_operation("delete_file", {
        "path": "/tmp/test.txt",
        "danger_code": "yesyesyes45"
    })
    assert result["allowed"], "DANGEROUS operation should be allowed with correct code"
    print("✓ DANGEROUS operation allowed with yesyesyes45")
    
    # Test FORBIDDEN operation
    result = enforcer_risky.check_operation("format_disk", {})
    assert not result["allowed"], "FORBIDDEN operation should never be allowed"
    print("✓ FORBIDDEN operation blocked")
    
    print("\n✅ All permission tests passed!\n")


def test_aegis_node_init():
    """Test AEGIS node initialization"""
    print("\n=== Testing AEGIS Node Initialization ===")
    
    # Test valid configuration
    config = {
        "aegis_agent": "researcher",
        "permission_mode": "safe",
        "protocol_666": False
    }
    
    try:
        node = AEGISAgentNode("test_researcher", config)
        assert node.agent_type == "researcher"
        assert node.permission_mode == "safe"
        print("✓ Researcher node initialized")
    except Exception as e:
        print(f"✗ Failed to initialize researcher node: {e}")
        raise
    
    # Test coding agent
    config = {
        "aegis_agent": "coding",
        "permission_mode": "risky",
        "protocol_666": False
    }
    
    try:
        node = AEGISAgentNode("test_coder", config)
        assert node.agent_type == "coding"
        assert node.permission_mode == "risky"
        print("✓ Coding node initialized")
    except Exception as e:
        print(f"✗ Failed to initialize coding node: {e}")
        raise
    
    print("\n✅ All initialization tests passed!\n")


async def test_aegis_node_execution():
    """Test AEGIS node execution"""
    print("\n=== Testing AEGIS Node Execution ===")
    
    # Create researcher node
    config = {
        "aegis_agent": "researcher",
        "permission_mode": "safe",
        "protocol_666": False
    }
    
    node = AEGISAgentNode("test_researcher", config)
    
    # Test message
    input_message = {
        "role": "user",
        "content": "What is async/await in Python? Give a brief explanation."
    }
    
    try:
        print("Executing researcher agent...")
        result = await node.execute(input_message)
        
        assert result["role"] == "assistant", "Result should have assistant role"
        assert "content" in result, "Result should have content"
        assert len(result["content"]) > 0, "Content should not be empty"
        
        print(f"\n📝 Agent Response Preview:")
        print(result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"])
        print(f"\n✓ Researcher agent executed successfully")
        print(f"✓ Response length: {len(result['content'])} characters")
        
        return result
        
    except Exception as e:
        print(f"✗ Failed to execute researcher node: {e}")
        raise


async def test_full_workflow_simulation():
    """Simulate a simple workflow: Research -> Code"""
    print("\n=== Testing Full Workflow Simulation ===")
    
    # Node 1: Researcher
    researcher_config = {
        "aegis_agent": "researcher",
        "permission_mode": "safe",
        "protocol_666": False
    }
    
    researcher = AEGISAgentNode("researcher", researcher_config)
    
    # Execute research
    print("\n[1/2] Running Research Phase...")
    research_input = {
        "role": "user",
        "content": "Research: What is async/await in Python and why is it useful?"
    }
    
    research_result = await researcher.execute(research_input)
    print(f"✓ Research completed ({len(research_result['content'])} chars)")
    
    # Node 2: Coder (uses research result)
    coder_config = {
        "aegis_agent": "coding",
        "permission_mode": "safe",  # Keep safe for test
        "protocol_666": False
    }
    
    coder = AEGISAgentNode("coder", coder_config)
    
    # Execute coding
    print("\n[2/2] Running Implementation Phase...")
    code_input = {
        "role": "user",
        "content": f"Based on this research:\n\n{research_result['content'][:500]}...\n\nCreate a simple example demonstrating async/await."
    }
    
    code_result = await coder.execute(code_input)
    print(f"✓ Implementation completed ({len(code_result['content'])} chars)")
    
    print("\n📊 Workflow Results:")
    print(f"  Research output: {len(research_result['content'])} chars")
    print(f"  Code output: {len(code_result['content'])} chars")
    print("\n✅ Full workflow simulation passed!\n")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AEGIS-ChatDev Integration Tests")
    print("="*60)
    
    try:
        # Test 1: Permission system
        test_permission_enforcer()
        
        # Test 2: Node initialization
        test_aegis_node_init()
        
        # Test 3: Node execution
        asyncio.run(test_aegis_node_execution())
        
        # Test 4: Full workflow simulation
        asyncio.run(test_full_workflow_simulation())
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
        print("Next steps:")
        print("1. Install ChatDev dependencies (if not done)")
        print("2. Copy bridge to ChatDev/node/aegis_bridge/")
        print("3. Test with actual ChatDev runtime")
        
    except Exception as e:
        logger.exception("Test failed")
        print(f"\n❌ TESTS FAILED: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

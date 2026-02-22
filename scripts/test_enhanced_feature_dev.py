"""
Test script for Enhanced Feature Development Agent with Sub-Agents
Tests CodeExplorer and CodeArchitect integration
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.feature_dev import FeatureDevAgent
from loguru import logger

async def test_enhanced_workflow():
    """Test the enhanced feature development workflow with sub-agents"""
    
    logger.info("=" * 60)
    logger.info("ENHANCED FEATURE DEVELOPMENT AGENT TEST")
    logger.info("=" * 60)
    
    agent = FeatureDevAgent()
    
    # Test feature that will benefit from codebase exploration
    feature_request = """
    Add user authentication to AEGIS:
    - Support username/password login
    - Store credentials securely (hashed)
    - Maintain session state
    - Add logout functionality
    """
    
    print("\n🚀 Starting Enhanced Feature Development Workflow\n")
    print(f"Feature Request: {feature_request.strip()}\n")
    print("-" * 60)
    
    try:
        async for update in agent.start_workflow(feature_request):
            print(update, end="", flush=True)
        
        print("\n" + "=" * 60)
        print("✅ Enhanced workflow test completed!")
        print("=" * 60)
        
        # Show enhanced workflow state
        print("\n📊 Workflow State Summary:")
        print(f"  Current Phase: {agent.workflow_state.get('current_phase')}/7")
        print(f"  Discoveries: {'✓' if agent.workflow_state.get('discoveries') else '✗'}")
        
        explorations = agent.workflow_state.get('explorations', [])
        print(f"  CodeExplorer Analyses: {len(explorations)}")
        if explorations:
            for i, exp in enumerate(explorations[:2], 1):  # Show first 2
                findings = exp.get('findings', {})
                if isinstance(findings, dict):
                    print(f"    {i}. Found {len(findings.get('patterns', []))} patterns, {len(findings.get('key_files', []))} key files")
        
        architectures = agent.workflow_state.get('architectures', [])
        print(f"  CodeArchitect Designs: {len(architectures)}")
        if architectures and isinstance(architectures, list):
            for i, arch in enumerate(architectures[:3], 1):  # Show all 3
                if isinstance(arch, dict):
                    print(f"    {i}. {arch.get('name', 'Approach ' + str(i))} - Complexity: {arch.get('complexity', 'N/A')}")
        
        recommendation = agent.workflow_state.get('architect_recommendation', '')
        if recommendation:
            print(f"  Recommendation: {recommendation[:100]}...")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_enhanced_workflow())

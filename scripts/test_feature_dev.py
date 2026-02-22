"""
Test script for Feature Development Agent
Validates the 7-phase workflow with a simple feature request
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.feature_dev import FeatureDevAgent
from loguru import logger

async def test_feature_dev_workflow():
    """Test the feature development workflow"""
    
    logger.info("=" * 60)
    logger.info("FEATURE DEVELOPMENT AGENT TEST")
    logger.info("=" * 60)
    
    agent = FeatureDevAgent()
    
    # Simple test feature
    feature_request = """
    Add a simple caching layer to the AEGIS bot:
    - Cache LLM responses to avoid redundant API calls
    - Use in-memory cache with TTL (time-to-live)
    - Add cache hit/miss statistics
    """
    
    print("\n🚀 Starting Feature Development Workflow\n")
    print(f"Feature Request: {feature_request.strip()}\n")
    print("-" * 60)
    
    try:
        async for update in agent.start_workflow(feature_request):
            print(update, end="", flush=True)
        
        print("\n" + "=" * 60)
        print("✅ Workflow test completed successfully!")
        print("=" * 60)
        
        # Show workflow state
        print("\n📊 Workflow State Summary:")
        print(f"  Current Phase: {agent.workflow_state.get('current_phase')}/7")
        print(f"  Discoveries: {'✓' if agent.workflow_state.get('discoveries') else '✗'}")
        print(f"  Explorations: {len(agent.workflow_state.get('explorations', []))} tasks")
        print(f"  Clarifications Generated: {'✓' if agent.workflow_state.get('clarifications') else '✗'}")
        print(f"  Architectures Generated: {'✓' if agent.workflow_state.get('architectures') else '✗'}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_feature_dev_workflow())

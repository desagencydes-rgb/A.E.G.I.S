"""
AEGIS Agent Node - Custom ChatDev Node

Wraps AEGIS agents as ChatDev nodes, enabling them to run in workflows.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

# Add AEGIS to path
AEGIS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(AEGIS_ROOT))

from chatdev_bridge.config import BridgeConfig
from chatdev_bridge.permission_enforcer import PermissionEnforcer


class AEGISAgentNode:
    """
    Custom ChatDev node that wraps AEGIS agents
    
    Supports:
    - All 10 AEGIS agent types
    - Permission enforcement (safe/risky/dangerous)
    - Protocol 666 mode switching  
    - Async/sync bridging
    """
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        """
        Initialize AEGIS agent node
        
        Args:
            node_id: Unique node ID in workflow
            config: Node configuration from YAML:
                - aegis_agent: Agent type (orchestrator, coding, researcher, etc.)
                - permission_mode: 'safe', 'risky', or 'dangerous'
                - protocol_666: bool, enable monster mode
                - danger_code: Optional yesyesyes45 code for dangerous ops
        """
        self.node_id = node_id
        self.config = config
        
        # Extract AEGIS-specific config
        self.agent_type = config.get("aegis_agent", "orchestrator")
        self.permission_mode = config.get("permission_mode", "safe")
        self.protocol_666 = config.get("protocol_666", False)
        self.danger_code = config.get("danger_code", None)
        
        # Validate
        if self.agent_type not in BridgeConfig.AGENT_TYPES:
            raise ValueError(f"Unknown AEGIS agent type: {self.agent_type}")
        
        if not BridgeConfig.validate_permission_level(self.permission_mode):
            raise ValueError(f"Invalid permission level: {self.permission_mode}")
        
        # Initialize permission enforcer
        self.permission_enforcer = PermissionEnforcer(self.permission_mode)
        
        # Load AEGIS agent class
        AgentClass = BridgeConfig.get_agent_class(self.agent_type)
        
        # Initialize agent
        self.agent = AgentClass()
        
        # Set mode if orchestrator
        if hasattr(self.agent, 'mode_manager') and self.protocol_666:
            from core.mode import Mode
            self.agent.mode_manager.switch_mode(Mode.MONSTER)
            logger.info(f"AEGIS Agent '{self.agent_type}' initialized in MONSTER MODE (Protocol 666)")
        else:
            logger.info(f"AEGIS Agent '{self.agent_type}' initialized in NORMAL mode")
    
    async def execute(self, input_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute AEGIS agent asynchronously
        
        Args:
            input_message: Message from previous node, format:
                {
                    "role": "user|assistant",
                    "content": "text content",
                    "attachments": []  # optional
                }
        
        Returns:
            Output message in same format
        """
        try:
            # Extract content
            content = input_message.get("content", "")
            
            logger.info(f"AEGIS Node '{self.node_id}' ({self.agent_type}) processing: {content[:100]}...")
            
            # Prepare task for AEGIS agent
            task = {
                "message": content,
                "permission_level": self.permission_mode,
                "danger_code": self.danger_code,
                "attachments": input_message.get("attachments", [])
            }
            
            # Execute agent in thread pool (sync -> async bridge)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._execute_sync,
                task
            )
            
            # Format response for ChatDev
            response = {
                "role": "assistant",
                "content": result.get("response", ""),
                "metadata": {
                    "agent_type": self.agent_type,
                    "permission_mode": self.permission_mode,
                    "protocol_666": self.protocol_666,
                    "audit_log": self.permission_enforcer.get_audit_log()
                }
            }
            
            logger.success(f"AEGIS Node '{self.node_id}' completed successfully")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in AEGIS Node '{self.node_id}': {e}")
            return {
                "role": "assistant",
                "content": f"ERROR: {str(e)}",
                "metadata": {"error": True}
            }
    
    def _execute_sync(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute AEGIS agent synchronously (runs in thread pool)
        
        This bridges the sync AEGIS code to async ChatDev runtime
        """
        # Most AEGIS agents have a process_task method
        if hasattr(self.agent, 'process_task'):
            result = self.agent.process_task(task)
            return result
        
        # Fallback: use chat method for simpler agents
        elif hasattr(self.agent, 'chat'):
            import asyncio
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run async chat in this thread's loop
                response = loop.run_until_complete(
                    self.agent.chat(task["message"], stream=False)
                )
                return {"response": response}
            finally:
                loop.close()
        
        else:
            raise NotImplementedError(f"Agent {self.agent_type} doesn't implement process_task or chat")


# Registration function for ChatDev
def register_aegis_node():
    """
    Register AEGISAgentNode with ChatDev's node registry
    
    Call this in ChatDev/node/__init__.py or similar
    """
    try:
        # This will work when installed in ChatDev
        from runtime.registry import register_node_type
        register_node_type("aegis_agent", AEGISAgentNode)
        logger.success("AEGISAgentNode registered with ChatDev")
    except ImportError:
        logger.warning("ChatDev runtime not available - node registration skipped")


if __name__ == "__main__":
    # Test AEGIS node standalone
    print("Testing AEGIS Node Wrapper...")
    
    # Test configuration
    test_config = {
        "aegis_agent": "researcher",
        "permission_mode": "safe",
        "protocol_666": False
    }
    
    # Create node
    node = AEGISAgentNode("test_node", test_config)
    
    # Test message
    test_message = {
        "role": "user",
        "content": "What are the benefits of async/await in Python?"
    }
    
    # Execute (need to run in async context)
    async def test():
        result = await node.execute(test_message)
        print("\n=== RESULT ===")
        print(result["content"])
    
    asyncio.run(test())

"""
Memory Bridge - Synchronizes memory between AEGIS and ChatDev

Handles bidirectional memory sync and format translation.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
from loguru import logger

# Add AEGIS to path
AEGIS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(AEGIS_ROOT))

from memory.manager import MemoryManager


class AEGISMemoryBridge:
    """
    Bridges AEGIS's hybrid memory system with ChatDev's memory stores
    
    Supports:
    - Export AEGIS memories to ChatDev format
    - Import ChatDev memories to AEGIS
    - Bidirectional sync
    - Format translation
    """
    
    def __init__(self):
        """Initialize memory bridge"""
        self.aegis_memory = MemoryManager()
        logger.info("AEGIS Memory Bridge initialized")
    
    def export_to_chatdev(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Export AEGIS memories in ChatDev-compatible format
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of memory items in ChatDev format
        """
        # Search AEGIS memory
        aegis_results = self.aegis_memory.search_memory(query, limit)
        
        # Convert to ChatDev format
        chatdev_memories = []
        for item in aegis_results:
            chatdev_memory = {
                "content": item.get("content", ""),
                "metadata": {
                    "source": "aegis",
                    "role": item.get("role", "assistant"),
                    "timestamp": item.get("metadata", {}).get("timestamp"),
                    "similarity": item.get("distance", 0.0)
                }
            }
            chatdev_memories.append(chatdev_memory)
        
        logger.debug(f"Exported {len(chatdev_memories)} memories to ChatDev format")
        return chatdev_memories
    
    def import_from_chatdev(
        self, 
        memories: List[Dict[str, Any]], 
        workflow_id: Optional[str] = None,
        node_id: Optional[str] = None
    ):
        """
        Import ChatDev memories into AEGIS
        
        Args:
            memories: List of memory items from ChatDev
            workflow_id: Optional workflow ID for tracking
            node_id: Optional node ID for tracking
        """
        for mem in memories:
            # Extract content and metadata
            content = mem.get("content", "")
            mem_metadata = mem.get("metadata", {})
            
            # Augment with workflow tracking
            aegis_metadata = {
                **mem_metadata,
                "source": "chatdev",
                "workflow_id": workflow_id,
                "node_id": node_id
            }
            
            # Add to AEGIS memory
            self.aegis_memory.add_memory(
                role=mem_metadata.get("role", "assistant"),
                content=content,
                metadata=aegis_metadata
            )
        
        logger.debug(f"Imported {len(memories)} memories from ChatDev")
    
    def sync_bidirectional(
        self,
        chatdev_memories: List[Dict[str, Any]],
        query: str,
        workflow_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Bidirectional sync: import ChatDev memories to AEGIS, 
        then export relevant AEGIS memories back
        
        Args:
            chatdev_memories: Memories from ChatDev workflow
            query: Query to retrieve relevant AEGIS memories
            workflow_id: Workflow ID for tracking
            
        Returns:
            Combined memories from both systems
        """
        # Import ChatDev memories
        self.import_from_chatdev(chatdev_memories, workflow_id=workflow_id)
        
        # Export relevant AEGIS memories
        aegis_memories = self.export_to_chatdev(query, limit=10)
        
        # Combine (deduplicate by content)
        seen_content = set()
        combined = []
        
        for mem in chatdev_memories + aegis_memories:
            content_hash = hash(mem["content"][:100])  # Hash first 100 chars
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                combined.append(mem)
        
        logger.info(f"Bidirectional sync: {len(combined)} unique memories")
        return combined
    
    def get_context_for_agent(
        self,
        agent_type: str,
        current_task: str,
        limit: int = 5
    ) -> str:
        """
        Get relevant context from AEGIS memory for an agent
        
        Args:
            agent_type: Type of agent (e.g., 'coding', 'researcher')
            current_task: Current task description
            limit: Max memories to retrieve
            
        Returns:
            Formatted context string
        """
        # Search for relevant memories
        query = f"{agent_type} {current_task}"
        memories = self.aegis_memory.search_memory(query, limit)
        
        if not memories:
            return ""
        
        # Format as context
        context_parts = ["=== Relevant Context from AEGIS Memory ===\n"]
        
        for i, mem in enumerate(memories, 1):
            context_parts.append(f"\n[Memory {i}]")
            context_parts.append(f"Role: {mem.get('role', 'unknown')}")
            context_parts.append(f"Content: {mem.get('content', '')[:200]}...")
            context_parts.append("")
        
        context = "\n".join(context_parts)
        logger.debug(f"Retrieved {len(memories)} memories for context")
        return context

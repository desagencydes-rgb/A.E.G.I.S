"""
Configuration for AEGIS-ChatDev Bridge
"""

from pathlib import Path
from typing import Dict, Any
import os


class BridgeConfig:
    """Configuration settings for the bridge"""
    
    # AEGIS project root
    AEGIS_ROOT = Path(__file__).parent.parent
    
    # ChatDev root
    CHATDEV_ROOT = AEGIS_ROOT / "ChatDev"
    
    # Agent type mappings
    AGENT_TYPES = {
        "orchestrator": "agents.orchestrator.OrchestratorAgent",
        "coding": "agents.coding.CodingAgent",
        "researcher": "agents.researcher.ResearchAgent",
        "tool_executor": "agents.tool_executor.ToolExecutorAgent",
        "memory": "agents.memory.MemoryAgent",
        "security": "agents.security_agent.SecurityAgent",
        "code_architect": "agents.code_architect.CodeArchitectAgent",
        "code_explorer": "agents.code_explorer.CodeExplorerAgent",
        "reviewer": "agents.reviewer.ReviewerAgent",
        "feature_dev": "agents.feature_dev.FeatureDevAgent",
    }
    
    # Permission level mappings
    PERMISSION_LEVELS = {
        "safe": 0,
        "risky": 1,
        "dangerous": 2,
        "forbidden": 3
    }
    
    # Memory paths
    MEMORY_DB_PATH = AEGIS_ROOT / "data" / "memory" / "chroma_db"
    SQLITE_PATH = AEGIS_ROOT / "data" / "memory" / "aegis.db"
    
    @classmethod
    def get_agent_class(cls, agent_type: str):
        """Dynamically import and return agent class"""
        import sys
        sys.path.insert(0, str(cls.AEGIS_ROOT))
        
        module_path, class_name = cls.AGENT_TYPES[agent_type].rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    
    @classmethod
    def validate_permission_level(cls, level: str) -> bool:
        """Check if permission level is valid"""
        return level in cls.PERMISSION_LEVELS

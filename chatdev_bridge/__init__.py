"""
AEGIS-ChatDev Bridge Package

Enables AEGIS agents to run as custom nodes in ChatDev workflows.
"""

__version__ = "0.1.0"

from .aegis_node import AEGISAgentNode
from .config import BridgeConfig
from .permission_enforcer import PermissionEnforcer
from .memory_bridge import AEGISMemoryBridge

__all__ = ["AEGISAgentNode", "BridgeConfig", "PermissionEnforcer", "AEGISMemoryBridge"]

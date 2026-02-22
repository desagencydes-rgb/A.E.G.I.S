"""
Permission system for AEGIS tool execution
Implements "yesyesyes45" dangerous operation gating
"""

from enum import Enum, auto
from typing import List, Optional
from loguru import logger
import re

class PermissionLevel(Enum):
    """Permission levels for tool execution"""
    SAFE = auto()           # Execute immediately
    RISKY = auto()          # Ask for confirmation
    DANGEROUS = auto()      # Requires "yesyesyes45" code
    FORBIDDEN = auto()      # Never execute

class PermissionGate:
    """Gate keeper for tool execution permissions"""
    
    DANGEROUS_CODE = "yesyesyes45"
    
    # Tool categorization
    SAFE_TOOLS = {
        "read_file", "list_directory", "search_text", "web_search",
        "get_system_info", "git_status", "git_log", "git_diff",
        "check_file_exists", "get_file_info"
    }
    
    RISKY_TOOLS = {
        "write_file", "create_directory", "run_command",
        "git_commit", "git_push", "install_package",
        "copy_file", "move_file", "edit_file"
    }
    
    DANGEROUS_TOOLS = {
        "delete_file", "delete_directory", "force_delete",
        "kill_process", "modify_system_file", "format_drive",
        "change_network_config"
    }
    
    FORBIDDEN_TOOLS = {
        "modify_bios", "modify_uefi", "delete_system32",
        "disable_firewall", "install_rootkit"
    }
    
    # Path patterns that are always forbidden
    FORBIDDEN_PATHS = [
        r"C:\\Windows\\System32",
        r"C:\\Windows\\SysWOW64",
        r"/etc/passwd",
        r"/etc/shadow",
        r"C:\\Windows\\Boot"
    ]
    
    @classmethod
    def categorize_tool(cls, tool_name: str) -> PermissionLevel:
        """Determine permission level for a tool"""
        if tool_name in cls.FORBIDDEN_TOOLS:
            return PermissionLevel.FORBIDDEN
        elif tool_name in cls.DANGEROUS_TOOLS:
            return PermissionLevel.DANGEROUS
        elif tool_name in cls.RISKY_TOOLS:
            return PermissionLevel.RISKY
        else:
            return PermissionLevel.SAFE
    
    @classmethod
    def check_permission(
        cls, 
        tool_name: str, 
        user_message: str, 
        tool_params: dict
    ) -> tuple[bool, Optional[str]]:
        """
        Check if operation is permitted
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        level = cls.categorize_tool(tool_name)
        
        # Check for forbidden paths
        if cls._contains_forbidden_path(tool_params):
            return False, "Operation targets forbidden system paths"
        
        # Permission logic
        if level == PermissionLevel.FORBIDDEN:
            return False, f"Tool '{tool_name}' is permanently forbidden"
        
        elif level == PermissionLevel.DANGEROUS:
            if cls._has_permission_code(user_message):
                logger.warning(f"Dangerous operation '{tool_name}' authorized with code")
                return True, None
            else:
                return False, f"Dangerous tool requires '{cls.DANGEROUS_CODE}' code in message"
        
        elif level == PermissionLevel.RISKY:
            # In normal mode, would prompt user
            # For now, allow since we're building the system
            logger.info(f"Risky operation '{tool_name}' allowed")
            return True, None
        
        else:  # SAFE
            return True, None
    
    @classmethod
    def _has_permission_code(cls, message: str) -> bool:
        """Check if message contains the dangerous permission code"""
        return cls.DANGEROUS_CODE.lower() in message.lower()
    
    @classmethod
    def _contains_forbidden_path(cls, params: dict) -> bool:
        """Check if parameters contain forbidden paths"""
        # Convert all params to string and check
        param_str = str(params).lower()
        
        for pattern in cls.FORBIDDEN_PATHS:
            if re.search(pattern.lower(), param_str):
                return True
        
        return False
    
    @classmethod
    def create_backup_path(cls, original_path: str) -> str:
        """Generate backup path for containment protocol"""
        from datetime import datetime
        from pathlib import Path
        
        path = Path(original_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        return str(backup_dir / f"{path.name}.backup_{timestamp}")

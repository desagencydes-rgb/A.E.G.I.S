"""
Permission Enforcement for AEGIS Agents in ChatDev Workflows

Enforces AEGIS permission tiers (SAFE/RISKY/DANGEROUS/FORBIDDEN) within ChatDev.
"""

from typing import Dict, Any, Optional
from loguru import logger
import json


class PermissionEnforcer:
    """Enforces AEGIS permission system in ChatDev workflows"""
    
    SAFE_CODE = None  # No code required
    YESYESYES_CODE = "yesyesyes45"  # Required for DANGEROUS operations
    
    def __init__(self, permission_mode: str = "safe"):
        """
        Initialize enforcer
        
        Args:
            permission_mode: One of 'safe', 'risky', 'dangerous'
        """
        self.permission_mode = permission_mode.lower()
        self.audit_log = []
        
        logger.info(f"PermissionEnforcer initialized in '{self.permission_mode}' mode")
    
    def check_operation(self, operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if an operation is allowed
        
        Args:
            operation: Operation name (e.g., 'write_file', 'delete_file')
            context: Operation context with details
            
        Returns:
            Dict with 'allowed' (bool) and 'reason' (str)
        """
        # Classify operation
        tier = self._classify_operation(operation, context)
        
        # Log attempt
        self._log_attempt(operation, tier, context)
        
        # Check permission
        if tier == "safe":
            return {"allowed": True, "reason": "SAFE operation"}
        
        elif tier == "risky":
            if self.permission_mode in ["risky", "dangerous"]:
                return {"allowed": True, "reason": f"RISKY operation allowed in {self.permission_mode} mode"}
            else:
                return {
                    "allowed": False, 
                    "reason": f"RISKY operation blocked in {self.permission_mode} mode. Set permission_mode to 'risky' or higher."
                } 
        
        elif tier == "dangerous":
            # Check for yesyesyes45 code in context
            provided_code = context.get("danger_code", "")
            if provided_code == self.YESYESYES_CODE:
                return {"allowed": True, "reason": "DANGEROUS operation allowed with correct code"}
            else:
                return {
                    "allowed": False,
                    "reason": f"DANGEROUS operation requires yesyesyes45 code. This must be provided in workflow config or human approval."
                }
        
        else:  # forbidden
            return {
                "allowed": False,
                "reason": "FORBIDDEN operation - never allowed"
            }
    
    def _classify_operation(self, operation: str, context: Dict[str, Any]) -> str:
        """
        Classify operation into permission tier
        
        Returns: 'safe', 'risky', 'dangerous', or 'forbidden'
        """
        # FORBIDDEN operations
        forbidden_patterns = [
            "format_disk",
            "rm_rf_root",
            "modify_bios",
            "delete_system32",
            "kill_process_1"  # init process
        ]
        
        if any(pattern in operation.lower() for pattern in forbidden_patterns):
            return "forbidden"
        
        # Check file paths for system files
        if "path" in context:
            path = str(context["path"]).lower()
            system_paths = ["c:\\windows", "/system", "/boot", "system32"]
            if any(sys_path in path for sys_path in system_paths):
                return "forbidden"
        
        # DANGEROUS operations
        dangerous_ops = [
            "delete_file",
            "delete_directory",
            "execute_system_command",
            "install_package",
            "modify_registry",
            "change_permissions"
        ]
        
        if operation in dangerous_ops:
            return "dangerous"
        
        # RISKY operations
        risky_ops = [
            "write_file",
            "create_file",
            "modify_file",
            "create_directory",
            "move_file",
            "copy_file"
        ]
        
        if operation in risky_ops:
            return "risky"
        
        # Default to SAFE
        return "safe"
    
    def _log_attempt(self, operation: str, tier: str, context: Dict[str, Any]):
        """Log permission attempt to audit trail"""
        log_entry = {
            "operation": operation,
            "tier": tier,
            "mode": self.permission_mode,
            "context": context
        }
        
        self.audit_log.append(log_entry)
        logger.debug(f"Permission check: {operation} ({tier}) in {self.permission_mode} mode")
    
    def get_audit_log(self) -> list:
        """Return full audit log"""
        return self.audit_log
    
    def clear_audit_log(self):
        """Clear audit log"""
        self.audit_log = []

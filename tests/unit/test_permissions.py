"""
Unit tests for Permission System
Tests permission levels (SAFE/RISKY/DANGEROUS/FORBIDDEN)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.permissions import PermissionLevel, PermissionGate


def get_permission_level(tool_name: str, params: dict) -> PermissionLevel:
    """Helper function to get permission level for a tool"""
    return PermissionGate.categorize_tool(tool_name)


class TestPermissionLevels:
    """Tests for permission level detection"""
    
    def test_safe_operations(self):
        """Test that safe operations are correctly identified"""
        assert get_permission_level("read_file", {"path": "test.txt"}) == PermissionLevel.SAFE
        assert get_permission_level("search_web", {"query": "test"}) == PermissionLevel.SAFE
        assert get_permission_level("list_directory", {"path": "."}) == PermissionLevel.SAFE
    
    def test_risky_operations(self):
        """Test that risky operations are correctly identified"""
        assert get_permission_level("write_file", {"path": "test.txt"}) == PermissionLevel.RISKY
        assert get_permission_level("install_package", {"package": "requests"}) == PermissionLevel.RISKY
    
    def test_dangerous_operations(self):
        """Test that dangerous operations are correctly identified"""
        assert get_permission_level("delete_file", {"path": "test.txt"}) == PermissionLevel.DANGEROUS
        assert get_permission_level("kill_process", {"pid": "123"}) == PermissionLevel.DANGEROUS
    
    def test_forbidden_operations(self):
        """Test that forbidden paths are blocked"""
        # System files - check_permission validates paths, categorize_tool does not
        allowed, _ = PermissionGate.check_permission("write_file", "", {"path": "C:\\Windows\\System32\\test.dll"})
        assert allowed is False
        allowed, _ = PermissionGate.check_permission("delete_file", "", {"path": "/etc/passwd"})
        assert allowed is False


class TestPermissionGate:
    """Tests for permission gate"""
    
    @pytest.fixture
    def gate(self):
        return PermissionGate()
    
    def test_check_permission_safe(self, gate):
        """Test safe operations are allowed"""
        allowed, reason = PermissionGate.check_permission("read_file", "", {"path": "test.txt"})
        assert allowed is True
    
    def test_check_permission_dangerous_without_code(self, gate):
        """Test dangerous operations require special code"""
        allowed, reason = PermissionGate.check_permission("delete_file", "", {"path": "test.txt"})
        assert allowed is False
        assert "yesyesyes45" in reason.lower() or "code" in reason.lower()
    
    def test_check_permission_dangerous_with_code(self, gate):
        """Test dangerous operations work with code"""
        allowed, reason = PermissionGate.check_permission("delete_file", "yesyesyes45", {"path": "test.txt"})
        assert allowed is True
    
    def test_check_permission_forbidden(self, gate):
        """Test forbidden operations are never allowed"""
        allowed, reason = PermissionGate.check_permission("write_file", "yesyesyes45", {"path": "C:\\Windows\\System32\\test.dll"})
        assert allowed is False
        assert "forbidden" in reason.lower() or "cannot" in reason.lower() or "system" in reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

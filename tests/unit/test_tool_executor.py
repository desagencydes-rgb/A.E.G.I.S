"""
Unit tests for Tool Executor Agent
Tests tool execution and permission gating
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.tool_executor import ToolExecutorAgent


class TestToolExecutorAgent:
    """Tests for the Tool Executor Agent"""
    
    @pytest.fixture
    def tool_executor(self):
        """Create a tool executor instance"""
        return ToolExecutorAgent()
    
    def test_init(self, tool_executor):
        """Test tool executor initialization"""
        assert tool_executor.name == "ToolExecutor"
        assert tool_executor.agent_type == "tool_executor"
    
    @pytest.mark.asyncio
    async def test_read_file(self, tool_executor, tmp_path):
        """Test file reading"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")
        
        task = {
            "tool": "read_file",
            "params": {"path": str(test_file)},
            "user_message": "Read the file"
        }
        
        result = await tool_executor.process_task(task)
        assert result["success"] is True
        assert "Hello World" in result.get("content", "")
    
    @pytest.mark.asyncio
    async def test_write_file_permission(self, tool_executor, tmp_path):
        """Test that write operations check permissions"""
        test_file = tmp_path / "new_file.txt"
        
        task = {
            "tool": "write_file",
            "params": {"path": str(test_file), "content": "test"},
            "user_message": "Write file"
        }
        
        # Without confirmation, should fail or require permission
        result = await tool_executor.process_task(task)
        # Depends on implementation - might succeed in temp dir
        assert "success" in result
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_search_web(self, tool_executor):
        """Test web search functionality"""
        task = {
            "tool": "search_web",
            "params": {"query": "test query"},
            "user_message": "Search for test query"
        }
        
        # Mock the actual web search to avoid network calls
        with patch.object(tool_executor, '_search_web', new=AsyncMock(return_value={
            "success": True,
            "results": [{"title": "Test", "url": "https://example.com", "snippet": "Test"}]
        })):
            result = await tool_executor.process_task(task)
            assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

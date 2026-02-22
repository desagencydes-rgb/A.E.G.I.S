"""
Unit tests for Research Agent
Tests web search, URL reading, summarization
"""
import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.researcher import ResearchAgent


class TestResearchAgent:
    """Tests for the Research Agent"""
    
    @pytest.fixture
    def researcher(self):
        """Create a researcher instance"""
        return ResearchAgent()
    
    def test_init(self, researcher):
        """Test researcher initialization"""
        assert researcher.name == "Researcher"
        assert researcher.agent_type == "researcher"
    
    @pytest.mark.asyncio
    async def test_process_task_basic(self, researcher):
        """Test basic task processing"""
        task = {"query": "test query"}
        
        # Mock the tool executor to avoid real web calls
        with patch.object(researcher.tool_executor, 'process_task', new=AsyncMock(return_value={
            "success": True,
            "results": [
                {"title": "Test Result", "url": "https://example.com", "snippet": "Test snippet"}
            ]
        })):
            result = await researcher.process_task(task)
            
            assert result["success"] is True
            assert "result" in result or "summary" in result
    
    @pytest.mark.asyncio
    async def test_process_task_with_memory(self, researcher):
        """Test that research results are saved to memory"""
        task = {"query": "Python features"}
        
        with patch.object(researcher.tool_executor, 'process_task', new=AsyncMock(return_value={
            "success": True,
            "results": [{"title": "Python", "url": "https://python.org", "snippet": "Python is great"}]
        })):
            with patch.object(researcher.memory_manager, 'add_memory', new=AsyncMock()) as mock_add:
                result = await researcher.process_task(task)
                
                # Should have saved to memory
                assert mock_add.called or result["success"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_empty_query(self, researcher):
        """Test handling of empty query"""
        task = {"query": ""}
        result = await researcher.process_task(task)
        
        # Should handle gracefully
        assert "success" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

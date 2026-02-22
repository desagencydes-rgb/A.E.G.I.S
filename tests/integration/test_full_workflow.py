"""
Integration tests for full workflow
Tests multi-agent delegation and coordination
Migrated and enhanced from scripts/test_integration.py
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.orchestrator import OrchestratorAgent
from unittest.mock import AsyncMock, patch


class TestFullWorkflow:
    """Integration tests for complete workflows"""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator for integration tests"""
        return OrchestratorAgent()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_research_workflow(self, orchestrator):
        """Test complete research workflow from user input to response"""
        # Mock the researcher to avoid real web calls
        with patch.object(orchestrator.researcher, 'process_task', new=AsyncMock(return_value={
            "success": True,
            "result": "Research Summary: Python 3.12 introduces improved error messages and performance."
        })):
            with patch('ollama.AsyncClient') as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value = mock_instance
                
                # First call returns tool call
                mock_instance.chat.side_effect = [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [{
                                "function": {
                                    "name": "delegate_research",
                                    "arguments": {"query": "Python 3.12 features"}
                                }
                            }]
                        }
                    },
                    # Second call (after tool execution) streams response
                    AsyncMock(return_value=[
                        {"message": {"content": "Based on the research"}},
                        {"message": {"content": ", Python 3.12 has many features."}},
                    ])
                ]
                
                chunks = []
                async for chunk in orchestrator.handle_message("Research Python 3.12 features"):
                    chunks.append(chunk)
                
                response = "".join(chunks)
                assert len(response) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_coding_workflow(self, orchestrator, tmp_path):
        """Test complete coding workflow"""
        test_file = tmp_path / "integration_test.py"
        
        # Mock the coder
        with patch.object(orchestrator.coder, 'process_task', new=AsyncMock(return_value={
            "success": True,
            "action": "created",
            "file_path": str(test_file)
        })):
            with patch('ollama.AsyncClient') as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value = mock_instance
                
                # Tool call for delegate_coding
                mock_instance.chat.side_effect = [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [{
                                "function": {
                                    "name": "delegate_coding",
                                    "arguments": {
                                        "instruction": "Create test file",
                                        "file_path": str(test_file)
                                    }
                                }
                            }]
                        }
                    },
                    AsyncMock(return_value=[
                        {"message": {"content": "File created successfully"}},
                    ])
                ]
                
                chunks = []
                async for chunk in orchestrator.handle_message(f"Create a test file at {test_file}"):
                    chunks.append(chunk)
                
                response = "".join(chunks)
                assert "created" in response.lower() or len(response) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_mode_switching_workflow(self, orchestrator):
        """Test mode switching in a workflow"""
        # Switch to monster mode
        chunks = []
        async for chunk in orchestrator.handle_message("/monster"):
            chunks.append(chunk)
        
        assert orchestrator.mode_manager.current_mode.value == "monster"
        
        # Switch back to normal
        chunks = []
        async for chunk in orchestrator.handle_message("/normal"):
            chunks.append(chunk)
        
        assert orchestrator.mode_manager.current_mode.value == "normal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

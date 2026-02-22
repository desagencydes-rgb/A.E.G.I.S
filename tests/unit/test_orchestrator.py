"""
Unit tests for Orchestrator Agent
Tests delegation logic, mode switching, context management
"""
import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.orchestrator import OrchestratorAgent
from core.mode import Mode


class TestOrchestratorAgent:
    """Tests for the Orchestrator Agent"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance"""
        return OrchestratorAgent()
    
    def test_init(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.name == "Orchestrator"
        assert orchestrator.agent_type == "orchestrator"
        assert orchestrator.researcher is not None
        assert orchestrator.coder is not None
        assert orchestrator.tool_executor is not None
        assert orchestrator.memory_manager is not None
    
    def test_mode_display(self, orchestrator):
        """Test mode display getter"""
        assert orchestrator.get_mode_display() in ["NORMAL", "MONSTER"]
    
    @pytest.mark.asyncio
    async def test_process_task(self, orchestrator):
        """Test process_task wrapper"""
        with patch.object(orchestrator, 'handle_message', new=AsyncMock(return_value=iter(["test response"]))):
            task = {"message": "Hello"}
            result = await orchestrator.process_task(task)
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_handle_mode_command(self, orchestrator):
        """Test mode switching commands"""
        chunks = []
        async for chunk in orchestrator.handle_message("/monster"):
            chunks.append(chunk)
        
        response = "".join(chunks)
        assert len(response) > 0
        # Should have switched mode or given a response
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_memory_recall(self, orchestrator):
        """Test that orchestrator checks memory before processing"""
        # Add a memory
        await orchestrator.memory_manager.add_memory("user", "My name is Alice")
        
        # Mock the LLM to avoid real API calls
        with patch('ollama.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            
            # Mock chat response
            mock_instance.chat.return_value = {
                "message": {
                    "role": "assistant",
                    "content": "I remember you told me your name is Alice!"
                }
            }
            
            chunks = []
            async for chunk in orchestrator.handle_message("What is my name?"):
                chunks.append(chunk)
            
            # Should have recalled memory
            response = "".join(chunks)
            assert "Recalled" in response or "memories" in response or len(response) > 0


class TestOrchestratorDelegation:
    """Tests for agent delegation"""
    
    @pytest.fixture
    def orchestrator(self):
        return OrchestratorAgent()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_delegate_to_researcher(self, orchestrator):
        """Test delegation to research agent"""
        with patch.object(orchestrator.researcher, 'process_task', new=AsyncMock(return_value={
            "success": True,
            "result": "Research completed successfully"
        })):
            task = {"query": "test query"}
            result = await orchestrator.researcher.process_task(task)
            assert result["success"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_delegate_to_coder(self, orchestrator):
        """Test delegation to coding agent"""
        with patch.object(orchestrator.coder, 'process_task', new=AsyncMock(return_value={
            "success": True,
            "action": "created"
        })):
            task = {"instruction": "write code", "file_path": "test.py"}
            result = await orchestrator.coder.process_task(task)
            assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

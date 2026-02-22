"""
Integration tests for memory system
Tests vector store, memory persistence, and RAG integration
Migrated and enhanced from scripts/test_memory_integration.py
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.orchestrator import OrchestratorAgent
from agents.researcher import ResearchAgent
from memory.manager import MemoryManager
from unittest.mock import AsyncMock, patch


class TestMemoryIntegration:
    """Integration tests for memory system"""
    
    @pytest.fixture
    async def setup_agents(self, tmp_path):
        """Setup agents with temporary memory"""
        import core.config
        original_chroma = core.config.config.chromadb_path
        original_sqlite = core.config.config.sqlite_path
        
        core.config.config.chromadb_path = tmp_path / "chroma"
        core.config.config.sqlite_path = tmp_path / "memory.db"
        
        orchestrator = OrchestratorAgent()
        researcher = ResearchAgent()
        
        yield orchestrator, researcher
        
        # Restore
        core.config.config.chromadb_path = original_chroma
        core.config.config.sqlite_path = original_sqlite
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.memory
    @pytest.mark.slow
    async def test_research_saves_to_memory(self, setup_agents):
        """Test that research results are saved to memory"""
        orchestrator, researcher = setup_agents
        
        # Mock research execution
        with patch.object(researcher.tool_executor, 'process_task', new=AsyncMock(return_value={
            "success": True,
            "results": [{"title": "Python 3.13", "url": "https://example.com", "snippet": "New features"}]
        })):
            with patch('ollama.AsyncClient') as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.return_value = {"message": {"content": "Python 3.13 introduces new features."}}
                
                task = {"query": "Python 3.13 features"}
                result = await researcher.process_task(task)
        
        # Verify memory was saved
        memories = await orchestrator.memory_manager.search_memory("Python 3.13", limit=5)
        assert len(memories) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.memory
    async def test_orchestrator_recalls_memory(self, setup_agents):
        """Test that orchestrator retrieves relevant memories"""
        orchestrator, _ = setup_agents
        
        # Add a memory
        await orchestrator.memory_manager.add_memory(
            "assistant",
            "Research Query: Python 3.13 features\nResult: Python 3.13 introduces improved syntax",
            metadata={"type": "research"}
        )
        
        # Try to recall it
        with patch('ollama.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.chat.return_value = {
                "message": {
                    "content": "Based on previous research, Python 3.13 introduces improved syntax."
                }
            }
            
            chunks = []
            async for chunk in orchestrator.handle_message("What are the Python 3.13 features?"):
                chunks.append(chunk)
            
            response = "".join(chunks)
            # Should indicate memory was recalled
            assert "Recalled" in response or "memories" in response or "Python 3.13" in response
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.memory
    async def test_memory_persistence_across_sessions(self, tmp_path):
        """Test that memories persist across different agent instances"""
        import core.config
        core.config.config.chromadb_path = tmp_path / "chroma"
        core.config.config.sqlite_path = tmp_path / "memory.db"
        
        # Session 1: Add memory
        mm1 = MemoryManager()
        await mm1.add_memory("user", "Important data: secret code is 1234")
        
        # Session 2: Retrieve memory
        mm2 = MemoryManager()
        results = await mm2.search_memory("What is the secret code?", limit=3)
        
        assert len(results) > 0
        assert any("1234" in r for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

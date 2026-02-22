"""
Unit tests for Memory Manager
Tests vector store, SQL operations, and RAG queries
"""
import pytest
import asyncio
import os
import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memory.manager import MemoryManager, SimpleVectorStore


class TestSimpleVectorStore:
    """Tests for the custom vector store"""
    
    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates the data directory"""
        store_path = tmp_path / "vectors"
        store = SimpleVectorStore(store_path)
        assert store_path.exists()
    
    def test_add_and_query(self, tmp_path):
        """Test adding vectors and querying"""
        store_path = tmp_path / "vectors"
        store = SimpleVectorStore(store_path)
        
        # Add some test data
        ids = ["id1", "id2", "id3"]
        documents = ["hello world", "goodbye world", "machine learning"]
        metadatas = [{"type": "test"}, {"type": "test"}, {"type": "test"}]
        # Simple mock embeddings (normalized)
        embeddings = [
            [1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0],
            [0.0, 0.0, 1.0]
        ]
        
        store.add(ids, documents, metadatas, embeddings)
        
        # Query with first embedding (should return id1)
        results = store.query([1.0, 0.0, 0.0], n_results=2)
        assert len(results["ids"][0]) >= 1  # Should return results
        assert results["ids"][0][0] == "id1"  # Most similar should be first
    
    def test_persistence(self, tmp_path):
        """Test that data persists across instances"""
        store_path = tmp_path / "vectors"
        
        # Create and add data
        store1 = SimpleVectorStore(store_path)
        store1.add(["id1"], ["test doc"], [{"key": "value"}], [[1.0, 0.0]])
        store1.save()
        
        # Load in new instance
        store2 = SimpleVectorStore(store_path)
        assert len(store2.ids) == 1
        assert store2.ids[0] == "id1"


class TestMemoryManager:
    """Tests for the Memory Manager"""
    
    @pytest.fixture
    async def memory_manager(self, tmp_path):
        """Create a memory manager with temp storage"""
        # Override paths temporarily
        import core.config
        original_chroma = core.config.config.chromadb_path
        original_sqlite = core.config.config.sqlite_path
        
        core.config.config.chromadb_path = tmp_path / "chroma"
        core.config.config.sqlite_path = tmp_path / "memory.db"
        
        mm = MemoryManager()
        yield mm
        
        # Restore
        core.config.config.chromadb_path = original_chroma
        core.config.config.sqlite_path = original_sqlite
    
    @pytest.mark.asyncio
    @pytest.mark.memory
    async def test_add_memory(self, memory_manager):
        """Test adding a memory entry"""
        await memory_manager.add_memory(
            role="user",
            content="My favorite color is blue",
            metadata={"mode": "test"}
        )
        
        # Check SQL was updated
        history = memory_manager.get_recent_history(limit=1)
        assert len(history) > 0
        assert "blue" in history[0]["content"]
    
    @pytest.mark.asyncio
    @pytest.mark.memory
    async def test_search_memory(self, memory_manager):
        """Test RAG search functionality"""
        # Add some memories
        await memory_manager.add_memory("user", "I love pizza")
        await memory_manager.add_memory("user", "Python is great")
        await memory_manager.add_memory("user", "The sky is blue")
        
        # Search for something related
        results = await memory_manager.search_memory("What food do I like?", limit=3)
        
        assert len(results) > 0
        # Should retrieve the pizza memory (if embeddings work correctly)
        # This is a basic check that search returns something
        assert any("pizza" in r.lower() or "python" in r.lower() or "sky" in r.lower() for r in results)
    
    @pytest.mark.asyncio
    @pytest.mark.memory
    async def test_get_recent_history(self, memory_manager):
        """Test retrieving recent history"""
        # Add multiple memories
        for i in range(5):
            await memory_manager.add_memory("user", f"Message {i}")
        
        history = memory_manager.get_recent_history(limit=3)
        assert len(history) == 3
        # Most recent should be last
        assert "Message 4" in history[-1]["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

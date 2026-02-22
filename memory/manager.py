"""
Memory Manager for AEGIS
Handles hybrid memory system:
1. Short-term: Context window management
2. Long-term (Vector): ChromaDB for semantic search using nomic-embed-text
3. Long-term (SQL): SQLite for structured logs and metadata
"""

"""
Memory Manager for AEGIS
Handles hybrid memory system:
1. Short-term: Context window management
2. Long-term (Vector): Simple JSON+NumPy vector store (ChromaDB replacement due to dependency issues)
3. Long-term (SQL): SQLite for structured logs and metadata
"""

import sqlite3
import json
import numpy as np
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
import ollama

from core.config import config

class SimpleVectorStore:
    """
    Lightweight vector store using JSON and NumPy
    Replaces ChromaDB to avoid Pydantic dependency hell
    """
    def __init__(self, path: Path):
        self.path = path
        self.data_path = path / "vectors.json"
        self.embeddings = []
        self.documents = []
        self.metadatas = []
        self.ids = []
        
        # Ensure directory exists
        path.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self.load()
    
    def load(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])
                    self.ids = data.get("ids", [])
                    # Load embeddings as numpy array
                    emb_list = data.get("embeddings", [])
                    if emb_list:
                        self.embeddings = np.array(emb_list)
                    else:
                        self.embeddings = np.empty((0, 0)) # Placeholder
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                self.embeddings = []

    def save(self):
        try:
            # Convert numpy to list for JSON
            emb_list = self.embeddings.tolist() if len(self.embeddings) > 0 else []
            
            data = {
                "documents": self.documents,
                "metadatas": self.metadatas,
                "ids": self.ids,
                "embeddings": emb_list
            }
            
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")

    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict], embeddings: List[List[float]]):
        """Add items to store"""
        # Convert new embeddings to numpy
        new_embs = np.array(embeddings)
        
        if len(self.embeddings) == 0:
            self.embeddings = new_embs
        else:
            self.embeddings = np.vstack([self.embeddings, new_embs])
            
        self.ids.extend(ids)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        
        self.save()

    def query(self, query_embedding: List[float], n_results: int = 5) -> Dict:
        """Find nearest neighbors using cosine similarity"""
        if len(self.embeddings) == 0:
            return {"documents": [], "metadatas": [], "distances": []}
            
        # Normalize query
        query_vec = np.array(query_embedding)
        norm_q = np.linalg.norm(query_vec)
        if norm_q == 0:
            return {"documents": [], "metadatas": [], "distances": []}
            
        query_vec = query_vec / norm_q
        
        # Normalize stored embeddings
        # Note: In production this should be cached
        norms = np.linalg.norm(self.embeddings, axis=1)
        # Avoid division by zero
        norms[norms == 0] = 1e-10
        stored_vecs = self.embeddings / norms[:, np.newaxis]
        
        # Cosine similarity
        similarities = np.dot(stored_vecs, query_vec)
        
        # Get top N indices
        # argsort sorts ascending, so take last n_results and reverse
        if n_results > len(similarities):
            n_results = len(similarities)
            
        top_indices = np.argsort(similarities)[-n_results:][::-1]
        
        results = {
            "ids": [[self.ids[i] for i in top_indices]],
            "documents": [[self.documents[i] for i in top_indices]],
            "metadatas": [[self.metadatas[i] for i in top_indices]],
            "distances": [[float(1 - similarities[i]) for i in top_indices]] # Convert sim to distance
        }
        
        return results

class MemoryManager:
    """
    Manages all memory operations for AEGIS agents
    """
    
    def __init__(self):
        # Initialize paths
        self.chroma_path = config.chromadb_path
        self.sqlite_path = config.sqlite_path
        
        # Initialize SQLite
        self._init_sqlite()
        
        # Initialize Vector Store
        self.vector_store = SimpleVectorStore(self.chroma_path)
        
        # Initialize Embedding Client
        self.ollama_client = ollama.Client(host=config.ollama_host)
        
        logger.info("MemoryManager initialized successfully (Simple Vector Store)")

    def _init_sqlite(self):
        """Ensure SQLite tables exist"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # Conversations (Chat history)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT,
            content TEXT,
            agent_name TEXT,
            mode TEXT,
            tool_calls TEXT
        )
        """)
        
        conn.commit()
        conn.close()

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama"""
        try:
            response = self.ollama_client.embeddings(
                model=config.models.get("embedding", {}).get("model", "nomic-embed-text"),
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []

    async def add_memory(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a new memory entry (both SQL and Vector)
        """
        if not content.strip():
            return

        timestamp = datetime.now().isoformat()
        metadata = metadata or {}
        mode = metadata.get("mode", "unknown")
        agent = metadata.get("agent", "unknown")
        
        # 1. Store in SQLite
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversation_history (role, content, agent_name, mode) VALUES (?, ?, ?, ?)",
            (role, content, agent, mode)
        )
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 2. Store in Vector Store
        # We only embed significant content
        if len(content.split()) > 3:
            embedding = self._get_embedding(content)
            if embedding:
                self.vector_store.add(
                    ids=[f"mem_{row_id}_{timestamp}"],
                    documents=[content],
                    metadatas=[{
                        "role": role,
                        "timestamp": timestamp,
                        "mode": mode,
                        "type": "conversation"
                    }],
                    embeddings=[embedding]
                )

    async def search_memory(self, query: str, limit: int = 5) -> List[str]:
        """
        Retrieve relevant memories for a query (RAG)
        """
        if not query.strip():
            return []
            
        embedding = self._get_embedding(query)
        if not embedding:
            return []
            
        results = self.vector_store.query(
            query_embedding=embedding,
            n_results=limit
        )
        
        # Flatten results
        memories = []
        if results['documents']:
            for doc_list in results['documents']:
                memories.extend(doc_list)
                
        return memories

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent raw chat history from SQL"""
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?", 
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        # Return in correct order (oldest first)
        history = [{"role": row["role"], "content": row["content"]} for row in rows]
        return history[::-1]

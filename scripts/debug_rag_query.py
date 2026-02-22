
import asyncio
from memory.manager import MemoryManager
from core.config import config
import logging

# Configure basic logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_search():
    print("Initializing MemoryManager...")
    mm = MemoryManager()
    
    query = "what's my \"bruh\" code?"
    print(f"\nQuerying: '{query}'")
    
    # Direct vector store query inspection
    embedding = mm._get_embedding(query)
    if embedding:
        results = mm.vector_store.query(embedding, n_results=5)
        print("\nRaw Vector Results:")
        for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
            print(f"  [dist={dist:.4f}] {doc} (Meta: {meta})")
    
    # Manager search wrapper
    print("\nMemoryManager.search_memory Results:")
    results = await mm.search_memory(query, limit=5)
    for res in results:
        print(f"  - {res}")

if __name__ == "__main__":
    asyncio.run(debug_search())

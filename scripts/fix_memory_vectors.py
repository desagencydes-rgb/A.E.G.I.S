
import json
import numpy as np
from pathlib import Path
import sys

def fix_vectors():
    # Path to vectors.json
    # Assuming running from project root
    path = Path("data/vector_db/vectors.json")
    if not path.exists():
        print(f"File not found: {path}")
        return

    print(f"Loading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ids = data.get("ids", [])
    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])
    embeddings = data.get("embeddings", [])

    # The ID to remove
    target_id = "mem_2_2026-02-07T17:09:28.440136"
    
    if target_id not in ids:
        print(f"Target ID {target_id} not found.")
        return

    index = ids.index(target_id)
    print(f"Found target at index {index}")
    print(f"Document: {documents[index]}")

    # Remove item
    print("Removing item...")
    del ids[index]
    del documents[index]
    del metadatas[index]
    del embeddings[index]

    # Save back
    new_data = {
        "ids": ids,
        "documents": documents,
        "metadatas": metadatas,
        "embeddings": embeddings
    }

    print("Saving updated vectors.json...")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f)
    
    print("Done!")

if __name__ == "__main__":
    fix_vectors()

#!/usr/bin/env python3
"""Task 3: Build FAISS index from knowledge_base/."""
from src.indexer import build_index

if __name__ == "__main__":
    build_index()
    print("Index built successfully → data/faiss.index")

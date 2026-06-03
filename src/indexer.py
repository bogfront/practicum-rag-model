"""Build and update the FAISS vector index from the knowledge base."""
import time
import logging
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config import (
    KNOWLEDGE_BASE_DIR,
    FAISS_INDEX_PATH,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def load_documents(kb_dir: str = KNOWLEDGE_BASE_DIR) -> list[dict]:
    """Load all .txt and .md files from the knowledge base directory."""
    docs = []
    for path in sorted(Path(kb_dir).glob("**/*")):
        if path.suffix in (".txt", ".md") and path.name != "terms_map.json":
            text = path.read_text(encoding="utf-8").strip()
            if text:
                docs.append({"text": text, "source": str(path.name)})
    log.info("Loaded %d documents from %s", len(docs), kb_dir)
    return docs


def split_documents(docs: list[dict]) -> list[dict]:
    """Split documents into chunks, preserving source metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for doc in docs:
        parts = splitter.split_text(doc["text"])
        for i, part in enumerate(parts):
            chunks.append({
                "text": part,
                "source": doc["source"],
                "chunk_id": f"{doc['source']}::chunk_{i}",
            })
    log.info("Split into %d chunks", len(chunks))
    return chunks


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_index(kb_dir: str = KNOWLEDGE_BASE_DIR, index_path: str = FAISS_INDEX_PATH) -> FAISS:
    """Build FAISS index from scratch and save it."""
    t0 = time.time()
    docs = load_documents(kb_dir)
    chunks = split_documents(docs)

    texts = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "chunk_id": c["chunk_id"]} for c in chunks]

    embeddings = get_embeddings()
    log.info("Generating embeddings for %d chunks …", len(texts))
    store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    store.save_local(index_path)

    elapsed = time.time() - t0
    log.info(
        "Index built: %d chunks, saved to %s (%.1fs)",
        len(texts), index_path, elapsed,
    )
    return store


def load_index(index_path: str = FAISS_INDEX_PATH) -> FAISS:
    embeddings = get_embeddings()
    return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)


def update_index(new_docs_dir: str, index_path: str = FAISS_INDEX_PATH) -> int:
    """Add new documents from new_docs_dir to the existing index."""
    new_docs = load_documents(new_docs_dir)
    if not new_docs:
        log.info("No new documents found in %s", new_docs_dir)
        return 0
    chunks = split_documents(new_docs)
    texts = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "chunk_id": c["chunk_id"]} for c in chunks]

    store = load_index(index_path)
    embeddings = get_embeddings()
    new_vecs = embeddings.embed_documents(texts)
    store.add_texts(texts, metadatas=metadatas, embeddings=new_vecs)
    store.save_local(index_path)
    log.info("Added %d new chunks to index", len(chunks))
    return len(chunks)


if __name__ == "__main__":
    build_index()

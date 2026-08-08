import chromadb
import hashlib

from config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    KNOWLEDGE_FILE
)

def load_knowledge() -> str:
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return file.read()

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 30):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap
    return chunks

def create_chunk_index(index, chunk):
    text = f"{index}-{chunk}"
    return hashlib.md5(text.encode()).hexdigest()

def get_collection():
    chroma = chromadb.PersistentClient(
        path=CHROMA_PATH
    )
    collection = chroma.get_or_create_collection(
        name=COLLECTION_NAME
    )
    return collection

def build_rag_database() -> None:
    collection = get_collection()
    knowledge = load_knowledge()

    chunks = chunk_text(knowledge, chunk_size=300, overlap=50)

    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        ids.append(create_chunk_index(index, chunk))
        documents.append(chunk)
        metadatas.append({
            "source": str(KNOWLEDGE_FILE),
            "chunk_index": index
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    print(f"RAG database ready with {len(chunks)} chunk(s).")

def search_knowledge(
    query: str,
    top_k: int = 3
) -> list[str]:
    collection = get_collection()
    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    documents = results.get("documents")

    return [] if not documents or not documents[0] else documents[0]
    
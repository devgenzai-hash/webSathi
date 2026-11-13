import io
import httpx
import hashlib
import re
from typing import List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

# Initialize clients (lazy loaded)
_chroma_client: Optional[chromadb.PersistentClient] = None


def get_embeddings_via_api(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using NVIDIA NIM / OpenAI-compatible API.
    Falls back to a simple hash-based embedding if API is unavailable."""
    api_key = settings.NVIDIA_NIM_API_KEY or settings.OPENAI_API_KEY
    base_url = "https://integrate.api.nvidia.com/v1" if settings.NVIDIA_NIM_API_KEY else "https://api.openai.com/v1"
    model = "nvidia/nv-embedqa-e5-v5" if settings.NVIDIA_NIM_API_KEY else "text-embedding-3-small"
    
    if not api_key:
        # Fallback: simple hash-based embeddings for testing
        return _simple_embeddings(texts)
    
    try:
        with httpx.Client(timeout=60.0) as client:
            # Process in batches of 16
            all_embeddings = []
            for i in range(0, len(texts), 16):
                batch = texts[i:i+16]
                response = client.post(
                    f"{base_url}/embeddings",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={"input": batch, "model": model, "encoding_format": "float"},
                )
                response.raise_for_status()
                data = response.json()
                batch_embeddings = [item["embedding"] for item in data["data"]]
                all_embeddings.extend(batch_embeddings)
            return all_embeddings
    except Exception as e:
        print(f"[WARNING] Embedding API failed: {e}. Using fallback embeddings.")
        return _simple_embeddings(texts)


def _simple_embeddings(texts: List[str], dim: int = 48) -> List[List[float]]:
    """Fallback token-hash embeddings for local development without API keys."""
    embeddings = []
    for text in texts:
        embedding = [0.0] * dim
        tokens = re.findall(r"[a-z0-9][a-z0-9_-]{1,}", text.lower())

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            embedding[index] += sign

        norm = sum(x*x for x in embedding) ** 0.5
        if norm == 0:
            embedding[0] = 1.0
        else:
            embedding = [x / norm for x in embedding]
        embeddings.append(embedding)
    return embeddings


def _create_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIR,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = _create_chroma_client()
    return _chroma_client


def _reset_chroma_client() -> chromadb.PersistentClient:
    """Recreate the ChromaDB client after a broken-pipe or OS error (Windows WinError 233)."""
    global _chroma_client
    _chroma_client = None
    print("[WARNING] ChromaDB client reset due to broken pipe — reinitializing.")
    return get_chroma_client()


def get_collection_for_site(site_id: str) -> chromadb.Collection:
    """Each site gets its own isolated collection - strict data separation."""
    collection_name = f"site_{site_id.replace('-', '_')[:50]}"
    for attempt in range(2):
        try:
            client = get_chroma_client()
            return client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except OSError:
            if attempt == 0:
                _reset_chroma_client()
                continue
            raise


def extract_text_from_file(file_path: str, file_type: str, content: bytes) -> str:
    """Extract text content from various file types."""
    if file_type == "pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(content))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        print(text_parts)
        return "\n\n".join(text_parts)
    
    elif file_type == "docx":
        from docx import Document as DocxDocument
        doc = DocxDocument(io.BytesIO(content))
        return "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    elif file_type == "txt" or file_type == "csv":
        return content.decode("utf-8", errors="ignore")
    
    elif file_type == "image":
        # OCR for images (requires tesseract installed)
        try:
            from PIL import Image
            import pytesseract
            image = Image.open(io.BytesIO(content))
            return pytesseract.image_to_string(image)
        except Exception:
            return ""
    
    return ""


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better retrieval."""
    if not text.strip():
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


async def process_document_for_rag(
    document_id: str,
    site_id: str,
    file_path: str,
    file_type: str,
    content: bytes,
) -> int:
    """Process a document: extract text, chunk it, embed it, store in vector DB."""
    # Extract text
    text = extract_text_from_file(file_path, file_type, content)
    if not text.strip():
        raise ValueError("Could not extract any text from the document")
    
    # Chunk text
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Document produced no chunks after processing")
    
    # Generate embeddings via API
    embeddings = get_embeddings_via_api(chunks)
    
    # Store in ChromaDB (isolated per site)
    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "chunk_index": i, "site_id": site_id}
        for i in range(len(chunks))
    ]

    # Retry once on broken-pipe errors (Windows WinError 233 / stale singleton)
    for attempt in range(2):
        try:
            collection = get_collection_for_site(site_id)
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
            )
            break
        except OSError:
            if attempt == 0:
                _reset_chroma_client()
                continue
            raise

    return len(chunks)


def delete_document_embeddings(site_id: str, document_id: str) -> None:
    """Delete all embeddings for a specific document."""
    for attempt in range(2):
        try:
            collection = get_collection_for_site(site_id)
            results = collection.get(where={"document_id": document_id})
            if results["ids"]:
                collection.delete(ids=results["ids"])
            return
        except OSError:
            if attempt == 0:
                _reset_chroma_client()
                continue
            raise


def retrieve_relevant_chunks(site_id: str, query: str, top_k: int = 5) -> List[str]:
    """Retrieve the most relevant document chunks for a query."""
    collection = get_collection_for_site(site_id)
    
    # Check if collection has any documents
    if collection.count() == 0:
        return []
    
    # Generate query embedding
    query_embedding = get_embeddings_via_api([query])
    
    count = collection.count()

    # Query ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(max(top_k, 10), count),
        include=["documents", "distances"],
    )

    relevant_chunks = []
    seen_chunks = set()
    query_words = set(re.findall(r"[a-z0-9][a-z0-9_-]{1,}", query.lower()))

    if results["documents"] and results["documents"][0]:
        for doc, distance in zip(results["documents"][0], results["distances"][0]):
            if not doc:
                continue
            doc_words = set(re.findall(r"[a-z0-9][a-z0-9_-]{1,}", doc.lower()))
            has_keyword_overlap = bool(query_words & doc_words)
            if (distance < 0.9 or has_keyword_overlap) and doc not in seen_chunks:
                relevant_chunks.append(doc)
                seen_chunks.add(doc)

    # Lexical fallback protects existing local collections whose embeddings were
    # created before the token-hash fallback became word-aware.
    lexical_chunks = _keyword_search_collection(collection, query_words, limit=top_k)
    for chunk in lexical_chunks:
        if chunk not in seen_chunks:
            relevant_chunks.append(chunk)
            seen_chunks.add(chunk)
        if len(relevant_chunks) >= max(top_k, 8):
            break
    
    return relevant_chunks[:max(top_k, 8)]


def _keyword_search_collection(collection: chromadb.Collection, query_words: set[str], limit: int) -> List[str]:
    if not query_words:
        return []

    try:
        all_results = collection.get(include=["documents"])
    except Exception:
        return []

    scored: list[tuple[float, str]] = []
    for doc in all_results.get("documents") or []:
        if not doc:
            continue
        doc_words = set(re.findall(r"[a-z0-9][a-z0-9_-]{1,}", doc.lower()))
        overlap = query_words & doc_words
        if not overlap:
            continue
        score = len(overlap) / max(len(query_words), 1)
        scored.append((score, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored[:limit]]


def rerank_chunks(query: str, chunks: List[str], top_k: int = 3) -> List[str]:
    """Simple reranking based on keyword overlap and semantic similarity."""
    if not chunks:
        return []
    
    query_words = set(query.lower().split())
    scored = []
    
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        # Keyword overlap score
        overlap = len(query_words & chunk_words) / max(len(query_words), 1)
        # Length penalty (prefer medium-length chunks)
        length_score = min(len(chunk) / 500, 1.0)
        score = overlap * 0.6 + length_score * 0.4
        scored.append((score, chunk))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]

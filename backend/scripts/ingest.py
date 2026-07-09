from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

BOOK_PATH = "data/source_books/ml_engineer.pdf"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
COLLECTION_NAME = "ml_engineer_kb"   # one collection per role
VECTOR_DB_PATH = "data/chroma"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_pdf_text(path: str) -> list[tuple[int, str]]:
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append((i + 1, text))
    return pages


def chunk_text(pages: list[tuple[int, str]]) -> list[dict]:
    chunks = []
    for page_num, text in pages:
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end].strip()
            if chunk:
                chunks.append({"text": chunk, "page": page_num})
            start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def embed_and_store(chunks: list[dict]) -> None:
    print(f"Loading embedding model '{EMBEDDING_MODEL}'...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [c["text"] for c in chunks]
    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    ids = [f"chunk-{i}" for i in range(len(chunks))]
    metadatas = [{"page": c["page"]} for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    print(f"Stored {collection.count()} chunks in collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    pages = load_pdf_text(BOOK_PATH)
    print(f"Loaded {len(pages)} pages")

    chunks = chunk_text(pages)
    print(f"Created {len(chunks)} chunks")

    embed_and_store(chunks)

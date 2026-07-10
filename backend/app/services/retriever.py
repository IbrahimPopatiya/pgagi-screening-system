import chromadb
from app.core.config import settings
from app.core.roles import ROLE_COLLECTIONS
from app.services.embeddings import get_embedding_model

SIMILARITY_DISTANCE_THRESHOLD = 1.35


def retrieve_chunks(role: str, queries: list[str], top_k_total: int = 5) -> list[dict]:
    collection_name = ROLE_COLLECTIONS.get(role)
    if not collection_name:
        raise ValueError(f"No knowledge base configured for role '{role}'")

    client = chromadb.PersistentClient(path=settings.vector_db_path)
    collection = client.get_collection(collection_name)
    model = get_embedding_model()

    seen_pages = set()
    candidates = []

    for query in queries:
        query_embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=3)

        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            if dist <= SIMILARITY_DISTANCE_THRESHOLD and meta["page"] not in seen_pages:
                seen_pages.add(meta["page"])
                candidates.append({"text": doc, "page": meta["page"], "distance": dist, "source_query": query})

    candidates.sort(key=lambda c: c["distance"])
    return candidates[:top_k_total]

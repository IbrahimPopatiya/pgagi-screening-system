import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_collection("ml_engineer_kb")

model = SentenceTransformer("all-MiniLM-L6-v2")
query = "overfitting and regularization in machine learning models"
query_embedding = model.encode([query]).tolist()

results = collection.query(query_embeddings=query_embedding, n_results=3)

for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
    print(f"\n--- page {meta['page']} | distance {dist:.4f} ---")
    print(doc[:200])

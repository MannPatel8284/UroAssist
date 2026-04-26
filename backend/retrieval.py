import chromadb
from sentence_transformers import SentenceTransformer
from backend.config import config
from backend.urology_vocab import expand_query

embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
chroma_client = chromadb.PersistentClient(path=config.CHROMA_PATH)

def search(query: str, collection: str, top_k: int = 5) -> list[dict]:
    """
    Returns chunks with: text, score, doc_name, page, chunk_index.
    Applies urology_vocab.expand_query() to the query BEFORE embedding.
    """
    expanded_query = expand_query(query)
    query_embedding = embedding_model.encode(expanded_query).tolist()
    
    try:
        chroma_collection = chroma_client.get_collection(name=collection)
    except Exception:
        # Collection might not exist yet
        return []
    
    results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    chunks = []
    if results.get("documents") and results["documents"][0]:
        for i in range(len(results["documents"][0])):
            chunks.append({
                "text": results["documents"][0][i],
                "score": results["distances"][0][i],
                "doc_name": results["metadatas"][0][i]["doc_name"],
                "page": results["metadatas"][0][i]["page"],
                "chunk_index": results["metadatas"][0][i]["chunk_index"]
            })
    return chunks

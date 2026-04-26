import argparse
import fitz
import os
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import config

embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
chroma_client = chromadb.PersistentClient(path=config.CHROMA_PATH)

def ingest_pdf(file_path: str, doc_id: str, collection: str) -> dict:
    """
    collection: 'clinical' or 'coding'
    Returns: {'doc_id': str, 'doc_name': str, 'num_chunks': int, 'collection': str}
    """
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Failed to open PDF file {file_path}: {e}")

    if len(doc) == 0:
        raise ValueError(f"PDF file {file_path} is empty.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )

    doc_name = os.path.basename(file_path)
    
    chunks = []
    metadatas = []
    ids = []
    
    chunk_idx = 0
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if not text.strip():
            continue
            
        page_chunks = text_splitter.split_text(text)
        for i, chunk in enumerate(page_chunks):
            chunks.append(chunk)
            metadatas.append({
                "doc_id": doc_id,
                "doc_name": doc_name,
                "page": page_num + 1,
                "chunk_index": chunk_idx
            })
            ids.append(f"{doc_id}_{chunk_idx}")
            chunk_idx += 1

    if not chunks:
        raise ValueError(f"No valid text found in PDF file {file_path}.")

    embeddings = embedding_model.encode(chunks).tolist()
    
    chroma_collection = chroma_client.get_or_create_collection(name=collection)
    
    chroma_collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    return {
        'doc_id': doc_id,
        'doc_name': doc_name,
        'num_chunks': len(chunks),
        'collection': collection
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a PDF into ChromaDB.")
    parser.add_argument("path", help="Path to the PDF file")
    parser.add_argument("--collection", required=True, choices=["clinical", "coding"], help="Collection to ingest into")
    args = parser.parse_args()

    doc_id = str(uuid.uuid4())
    try:
        result = ingest_pdf(args.path, doc_id, args.collection)
        print(f"Successfully ingested {result['doc_name']} into {result['collection']} ({result['num_chunks']} chunks)")
    except Exception as e:
        print(f"Error ingesting PDF: {e}")

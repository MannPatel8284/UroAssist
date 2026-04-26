import os
import uuid
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import config
from backend.models import (
    UploadResponse, ChatRequest, CodingRequest, 
    CodingResponse, DocumentInfo
)
from backend.ingestion import ingest_pdf, chroma_client
from backend.retrieval import search
from backend.llm import stream_answer
from backend.coding_helper import suggest_codes

app = FastAPI(title="UroAssist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    collections = {}
    try:
        for c in chroma_client.list_collections():
            collections[c.name] = c.count()
    except Exception:
        pass
        
    return {
        "status": "ok",
        "anthropic_configured": bool(config.ANTHROPIC_API_KEY),
        "collections": collections
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form(...)
):
    if collection not in ["clinical", "coding"]:
        raise HTTPException(status_code=400, detail="Invalid collection")
        
    temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        doc_id = str(uuid.uuid4())
        result = ingest_pdf(temp_path, doc_id, collection)
        return UploadResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/documents", response_model=List[DocumentInfo])
def list_documents(collection: str):
    if collection not in ["clinical", "coding"]:
        raise HTTPException(status_code=400, detail="Invalid collection")
        
    try:
        chroma_col = chroma_client.get_collection(name=collection)
        results = chroma_col.get(include=["metadatas"])
        
        docs = {}
        for meta in results["metadatas"]:
            doc_id = meta["doc_id"]
            if doc_id not in docs:
                docs[doc_id] = {
                    "doc_id": doc_id,
                    "doc_name": meta["doc_name"],
                    "collection": collection,
                    "num_chunks": 0
                }
            docs[doc_id]["num_chunks"] += 1
            
        return list(docs.values())
    except Exception:
        return []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if request.mode not in ["triage", "intake"]:
        raise HTTPException(status_code=400, detail="Invalid mode for chat endpoint")
        
    chunks = search(request.question, collection="clinical", top_k=5)
    
    async def event_generator():
        try:
            async for text_delta in stream_answer(request.question, chunks, request.mode):
                # Yield text events
                # Data should not have newlines breaking SSE formatting directly, 
                # but standard SSE typically sends json chunks. 
                # We can just yield data: {text_delta}\n\n
                yield f"data: {json.dumps({'text': text_delta})}\n\n"
            
            # Send sources event at the end
            sources = []
            for chunk in chunks:
                sources.append({
                    "doc_name": chunk["doc_name"],
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"]
                })
            yield f"event: sources\ndata: {json.dumps(sources)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/code", response_model=CodingResponse)
def code_endpoint(request: CodingRequest):
    try:
        result = suggest_codes(request.clinical_note)
        return CodingResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

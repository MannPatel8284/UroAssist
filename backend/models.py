from typing import Literal, List, Optional
from pydantic import BaseModel

class UploadResponse(BaseModel):
    doc_id: str
    doc_name: str
    num_chunks: int
    collection: str

class ChatRequest(BaseModel):
    mode: Literal["triage", "intake", "coding"]
    question: str

class CodingRequest(BaseModel):
    clinical_note: str

class CodingItem(BaseModel):
    code: str
    description: str
    rationale: str
    modifiers: Optional[List[str]] = None

class Source(BaseModel):
    doc_name: str
    page: int
    chunk_index: int

class CodingResponse(BaseModel):
    icd10: List[CodingItem]
    cpt: List[CodingItem]
    rationale: str
    sources: List[Source]

class DocumentInfo(BaseModel):
    doc_id: str
    doc_name: str
    collection: str
    num_chunks: int

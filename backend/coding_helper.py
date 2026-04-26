import json
import re
from anthropic import Anthropic
from backend.config import config
from backend.retrieval import search
from backend.llm import CODING_PROMPT, format_context

sync_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

def suggest_codes(clinical_note: str) -> dict:
    chunks = search(clinical_note, collection="coding", top_k=5)
    context = format_context(chunks)
    prompt = CODING_PROMPT.format(context=context, question=clinical_note)
    
    response = sync_client.messages.create(
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        model=config.LLM_MODEL,
    )
    
    response_text = response.content[0].text
    
    # Strip markdown code fences if present
    response_text = re.sub(r'^```json', '', response_text, flags=re.MULTILINE)
    response_text = re.sub(r'^```', '', response_text, flags=re.MULTILINE)
    response_text = response_text.strip()
    
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        return {
            "icd10": [],
            "cpt": [],
            "rationale": "Error parsing LLM response. The output was not valid JSON.",
            "sources": []
        }
        
    # Append sources based on chunks
    sources = []
    for i, chunk in enumerate(chunks, 1):
        sources.append({
            "doc_name": chunk["doc_name"],
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"]
        })
        
    data["sources"] = sources
    
    return data

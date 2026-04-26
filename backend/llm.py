import json
from typing import AsyncIterator, Literal
from anthropic import AsyncAnthropic
from backend.config import config

client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

TRIAGE_PROMPT = """You are an AI assistant for a urology nurse.
Maintain a clinical tone.
Surface red flags if present: gross painless hematuria, testicular pain (rule out torsion), fever + flank pain (sepsis risk), urinary retention.
Cite sources inline as [1], [2] matching the order the chunks are provided.
Never invent information not in the chunks. If unsure, say "not covered in provided guidelines".

Provided guidelines:
{context}

Question: {question}
"""

INTAKE_PROMPT = """You are an AI assistant for a urology patient.
Use plain English, no jargon, warm and reassuring.
Always end your response with: "Your urology team will review this before your visit."
Refuse to give a diagnosis or specific treatment advice.
For any red-flag symptoms (e.g. gross hematuria, severe pain, inability to urinate), advise seeking immediate care.

Information context:
{context}

Question: {question}
"""

CODING_PROMPT = """You are an expert urology medical coder.
Based on the clinical note and coding guidelines, suggest ICD-10 and CPT codes.
Return valid JSON ONLY (no markdown fences, no preamble):
{{"icd10": [{{"code": "...", "description": "...", "rationale": "..."}}], "cpt": [{{"code": "...", "description": "...", "rationale": "...", "modifiers": ["..."]}}], "rationale": "...", "sources": []}}

Be aware of common urology codes: 52000 (cystoscopy), 52204 (cysto + biopsy), 50590 (lithotripsy), 52601 (TURP), 55250 (vasectomy), 55700 (prostate biopsy).
Include modifier awareness when relevant (e.g., -22 increased complexity, -59 distinct procedural service).

Coding guidelines:
{context}

Clinical note: {question}
"""

def format_context(chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[{i}] {chunk['text']}")
    return "\n\n".join(context_parts)

async def stream_answer(question: str, chunks: list[dict], mode: Literal["triage", "intake", "coding"]) -> AsyncIterator[str]:
    context = format_context(chunks)
    
    if mode == "triage":
        prompt = TRIAGE_PROMPT.format(context=context, question=question)
    elif mode == "intake":
        prompt = INTAKE_PROMPT.format(context=context, question=question)
    elif mode == "coding":
        prompt = CODING_PROMPT.format(context=context, question=question)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    async with client.messages.stream(
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        model=config.LLM_MODEL,
    ) as stream:
        async for text in stream.text_stream:
            yield text

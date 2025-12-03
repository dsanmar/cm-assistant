import json
import os
from functools import lru_cache
from pathlib import Path   

import faiss
import numpy as np

from embeddings import embed_text
from llm_groq import call_groq_chat

BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_PATH = BASE_DIR / "outputs" / "spec_index.faiss"
METADATA_PATH = BASE_DIR / "outputs" / "spec_metadata.jsonl"


# ---------- Loading FAISS index + metadata ----------

@lru_cache(maxsize=1)
def load_faiss_index():
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")
    index = faiss.read_index(str(INDEX_PATH))
    return index


@lru_cache(maxsize=1)
def load_metadata():
    """
    Load chunk metadata from spec_metadata.jsonl.

    Each line is expected to look like:
        {
            "id": <int>,
            "section_id": "401.03(A)",
            "page_start": 123,
            "page_end": 125,
            "text": "...",
            "n_tokens": 180
        }
    """
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found at {METADATA_PATH}")

    records = []
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


@lru_cache(maxsize=1)
def get_section_entries():
    """
    For now, entries == chunk-level records from metadata.
    """
    return load_metadata()


# ---------- Retrieval ----------

def retrieve_top_sections(question: str, k: int = 5):
    """
    Embed the question, search FAISS, and return top-k chunk objects:
    {
      "section_id": ...,
      "text": ...,
      "page_start": ...,
      "page_end": ...,
      "score": ...,
    }
    """
    index = load_faiss_index()
    entries = get_section_entries()

    query_vec = embed_text(question).astype("float32")
    query_vec = np.expand_dims(query_vec, axis=0)

    scores, idxs = index.search(query_vec, k)
    scores = scores[0]
    idxs = idxs[0]

    results = []
    for score, idx in zip(scores, idxs):
        if idx < 0 or idx >= len(entries):
            continue
        entry = dict(entries[idx])  # copy
        entry["score"] = float(score)
        results.append(entry)

    return results


# ---------- Prompting Groq with RAG context ----------

def build_system_prompt():
    return (
        "You are an assistant for NJDOT's Construction & Materials division. "
        "You answer questions strictly using the 2019 Standard Specifications "
        "for Road and Bridge Construction. "
        "Always:\n"
        "1) Answer in clear, concise language.\n"
        "2) Explicitly cite the relevant spec section IDs and page ranges.\n"
        "3) If the answer is not clearly supported by the specs, say you are unsure "
        "and suggest where a human should look.\n"
    )


def build_context_block(sections):
    """
    Turn retrieved chunks into a text block for the model.
    """
    parts = []
    for s in sections:
        sid = s.get("section_id")
        p_start = s.get("page_start")
        p_end = s.get("page_end")
        header = f"[Section {sid}, pages {p_start}–{p_end}]"
        parts.append(header + "\n" + s.get("text", "").strip())
    return "\n\n".join(parts)


def answer_question(question: str, k: int = 5):
    """
    High-level API: given a question, run RAG and return:
    {
      "answer": str,
      "sources": [ {section_id, page_start, page_end, score} ],
      "debug": { "retrieved": [...], "k": k }
    }
    """
    sections = retrieve_top_sections(question, k=k)
    context = build_context_block(sections)

    system_prompt = build_system_prompt()
    user_content = (
        f"User question:\n{question}\n\n"
        f"Relevant spec sections and chunks:\n{context}\n\n"
        "Using ONLY the information above, answer the question and cite specific sections/pages "
        "from the 2019 Standard Specifications."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",  "content": user_content},
    ]

    answer = call_groq_chat(messages)

    sources = [
        {
            "section_id": s.get("section_id"),
            "page_start": s.get("page_start"),
            "page_end": s.get("page_end"),
            "score": s.get("score"),
        }
        for s in sections
    ]

    return {
        "answer": answer,
        "sources": sources,
        "debug": {
            "retrieved": sections,
            "k": k,
        },
    }

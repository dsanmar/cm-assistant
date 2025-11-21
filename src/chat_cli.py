"""
chat_cli.py
-----------
Simple RAG chatbot over the FULL 2019 NJDOT Standard Specifications,
using a local Ollama model (llama3.1)

Usage:
    cd src
    python chat_cli.py

Prereqs:
    - Ollama installed and server running:
        brew services start ollama
    - Model pulled:
        ollama pull llama3.1
"""

from pathlib import Path
import json
from typing import List, Dict

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import requests

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "outputs" / "spec_index.faiss"
META_PATH = ROOT / "outputs" / "spec_metadata.jsonl"

# -----------------------------
# Load FAISS index + metadata
# -----------------------------
print("[info] Loading FAISS index and metadata ...")
index = faiss.read_index(str(INDEX_PATH))

metadata: List[Dict] = []
with open(META_PATH, "r", encoding="utf-8") as f:
    for line in f:
        metadata.append(json.loads(line))
print(f"[info] Loaded {len(metadata)} chunks.")

# -----------------------------
# Load embedding model
# (must match build_index.py)
# -----------------------------
print("[info] Loading embedding model (all-MiniLM-L6-v2) ...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Ollama config
# -----------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1"  # change here if you use a different model


def retrieve(query: str, k: int = 6) -> List[Dict]:
    """
    Return top-k chunks (with distances) for a user query using FAISS.
    """
    q_vec = embed_model.encode([query]).astype("float32")
    D, I = index.search(q_vec, k)
    hits = []
    for score, idx in zip(D[0], I[0]):
        doc = metadata[idx].copy()
        doc["score"] = float(score)
        hits.append(doc)
    return hits


def build_context(hits: List[Dict]) -> str:
    """
    Format retrieved chunks into a context string for the LLM.
    Each chunk includes its section ID and page range.
    """
    parts = []
    for h in hits:
        header = f"[Section {h['section_id']} | pages {h['page_start']}-{h['page_end']}]"
        parts.append(header + "\n" + h["content"])
    return "\n\n----\n\n".join(parts)


def ask_ollama(question: str, context: str) -> str:
    """
    Call the local Ollama model with a RAG-style prompt.
    We pack system instructions + context + question into a single prompt.
    """
    system_instructions = (
        "You are an assistant helping new hires at NJDOT's Construction & Materials (C&M) division.\n"
        "You answer questions ONLY using the provided context from the "
        "2019 Standard Specifications for Road and Bridge Construction.\n"
        "Rules:\n"
        "- Do NOT invent rules that are not in the context.\n"
        "- If the answer is not clearly present, say you are not sure and suggest which section "
        "or division they might check.\n"
        "- Always mention section IDs (e.g., 401.03.07) and page ranges when possible.\n"
    )

    prompt = (
        system_instructions
        + "\n\nCONTEXT (excerpted from the 2019 Standard Specifications):\n"
        + context
        + "\n\nQUESTION:\n"
        + question
        + "\n\nINSTRUCTIONS FOR YOUR ANSWER:\n"
        "- Answer concisely in plain language.\n"
        "- Cite the relevant section IDs and page ranges in your answer.\n"
        "- If multiple sections apply, list them.\n"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,  # easier for a simple script
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        # Ollama returns the answer text in the "response" field
        answer = data.get("response", "").strip()
        if not answer:
            answer = "[error] Empty response from Ollama."
        return answer
    except requests.exceptions.RequestException as e:
        return f"[error] Failed to reach Ollama at {OLLAMA_URL}: {e}"


def main():
    print("\nNJDOT 2019 Spec Assistant (Full Document RAG Demo - Ollama Edition)")
    print("Ask a question about the specifications, or type 'exit' to quit.\n")

    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[bye]")
            break

        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            print("[bye]")
            break

        # 1) Retrieve relevant chunks
        hits = retrieve(q, k=6)
        context = build_context(hits)

        # 2) Ask the local LLM
        print("\n[info] Querying Ollama model ...")
        answer = ask_ollama(q, context)

        # 3) Show answer
        print("\nAssistant:\n" + answer + "\n")

        # Show which sections were used
        used_secs = {h["section_id"] for h in hits}
        print("[debug] Top sections used:", ", ".join(sorted(used_secs)), "\n")


if __name__ == "__main__":
    main()

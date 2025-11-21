"""
build_index.py
--------------
Builds a vector index for ALL sections of the 2019 NJDOT Standard Specifications.

Input:
    outputs/sections.jsonl

Outputs:
    outputs/spec_index.faiss
    outputs/spec_metadata.jsonl
"""

from pathlib import Path
import json
from typing import List, Dict

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
SECTIONS_PATH = ROOT / "outputs" / "sections.jsonl"

INDEX_PATH = ROOT / "outputs" / "spec_index.faiss"
META_PATH = ROOT / "outputs" / "spec_metadata.jsonl"


def load_sections() -> List[Dict]:
    sections = []
    with open(SECTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            sections.append(json.loads(line))
    return sections


def simple_chunk(text: str, max_chars: int = 1200, overlap: int = 200):
    """
    Very simple character-based chunker with overlap.


    """
    text = text.strip()
    if not text:
        return

    if len(text) <= max_chars:
        yield text
        return

    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        yield chunk.strip()
        start = end - overlap


def build_index():
    print(f"[info] Loading sections from {SECTIONS_PATH}")
    sections = load_sections()
    print(f"[info] Total sections found: {len(sections)}")

    documents: List[Dict] = []
    for sec in sections:
        sec_id = sec.get("section_id", "UNKNOWN")
        page_start = sec.get("page_start")
        page_end = sec.get("page_end")
        text = sec.get("text", "")

        for chunk_text in simple_chunk(text):
            documents.append(
                {
                    "section_id": sec_id,
                    "page_start": page_start,
                    "page_end": page_end,
                    "content": chunk_text,
                }
            )

    print(f"[info] Total chunks to index: {len(documents)}")

    # Load embedding model
    print("[info] Loading embedding model (all-MiniLM-L6-v2) ...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    dim = model.get_sentence_embedding_dimension()

    # Compute embeddings
    texts = [d["content"] for d in documents]
    print("[info] Computing embeddings ...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    embeddings = np.asarray(embeddings, dtype="float32")

    # Build FAISS index
    print("[info] Building FAISS index ...")
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    print(f"[✓] Saved FAISS index → {INDEX_PATH}")

    # Save metadata
    with open(META_PATH, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"[✓] Saved metadata → {META_PATH}")
    print("[done] Index build complete.")


if __name__ == "__main__":
    build_index()

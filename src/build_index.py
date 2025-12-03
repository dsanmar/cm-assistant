"""
build_index.py
--------------
Builds FAISS index + metadata for the NJDOT 2019 Standard Specs,
using precomputed sections from outputs/sections.jsonl.

Input:
    outputs/sections.jsonl  (from extract_sections.py)

Outputs:
    outputs/spec_index.faiss
    outputs/spec_metadata.jsonl

Each line in spec_metadata.jsonl:
    {
        "id": <int>,              # index in FAISS
        "section_id": "401.03(A)",
        "page_start": 123,
        "page_end": 125,
        "text": "chunk text",
        "n_tokens": 180
    }
"""

from pathlib import Path
import json
from typing import List, Dict

import numpy as np
import faiss
from tqdm import tqdm

from embeddings import embed_text

# src/ → project root
ROOT = Path(__file__).resolve().parents[1]
SECTIONS_PATH = ROOT / "outputs" / "sections.jsonl"
INDEX_PATH = ROOT / "outputs" / "spec_index.faiss"
META_PATH = ROOT / "outputs" / "spec_metadata.jsonl"

# Rough “token” size: we just treat whitespace-separated words as tokens
MAX_TOKENS = 256       # target size of each chunk
OVERLAP_TOKENS = 50    # overlap between chunks for context


def load_sections() -> List[Dict]:
    sections = []
    with open(SECTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                sections.append(json.loads(line))
    return sections


def split_into_chunks(text: str) -> List[str]:
    """
    Split text into overlapping chunks by word count to keep
    each chunk roughly <= MAX_TOKENS.
    """
    tokens = text.split()
    if not tokens:
        return []

    chunks = []
    start = 0
    n = len(tokens)

    while start < n:
        end = min(start + MAX_TOKENS, n)
        chunk_tokens = tokens[start:end]
        chunk = " ".join(chunk_tokens).strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        # move start forward with overlap
        start = end - OVERLAP_TOKENS

    return chunks


def main():
    sections = load_sections()
    print(f"[info] Loaded {len(sections)} sections from {SECTIONS_PATH}")

    vectors = []
    metadata = []
    idx = 0

    for sec in tqdm(sections, desc="Chunking + embedding"):
        section_id = sec.get("section_id")
        page_start = sec.get("page_start")
        page_end = sec.get("page_end")
        text = sec.get("text", "")

        for chunk in split_into_chunks(text):
            vec = embed_text(chunk)
            vectors.append(vec)

            meta_rec = {
                "id": idx,
                "section_id": section_id,
                "page_start": page_start,
                "page_end": page_end,
                "text": chunk,
                "n_tokens": len(chunk.split()),
            }
            metadata.append(meta_rec)
            idx += 1

    if not vectors:
        raise RuntimeError("No vectors were created; check sections or chunking logic.")

    mat = np.stack(vectors, axis=0).astype("float32")
    dim = mat.shape[1]
    print(f"[info] Built matrix with shape {mat.shape} (num_chunks x dim)")

    # Because we normalized embeddings in embeddings.py, we can use inner product
    index = faiss.IndexFlatIP(dim)
    index.add(mat)
    faiss.write_index(index, str(INDEX_PATH))
    print(f"[✓] Wrote FAISS index → {INDEX_PATH}")

    with open(META_PATH, "w", encoding="utf-8") as f:
        for rec in metadata:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[✓] Wrote metadata ({len(metadata)} records) → {META_PATH}")


if __name__ == "__main__":
    main()


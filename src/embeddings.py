"""
Shared embedding utilities for the NJDOT C&M Spec Assistant.

This uses a SentenceTransformer model to turn text into vectors
for FAISS and retrieval.
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# Can swap this model later
_MODEL_NAME = "all-MiniLM-L6-v2"

# Load once at import time
_embedder = SentenceTransformer(_MODEL_NAME)


def embed_text(text: str) -> np.ndarray:
    """
    Embed a single text into a 1D numpy array (float32).

    We normalize the embeddings so that cosine similarity can be
    approximated using dot product (IndexFlatIP).
    """
    if not text:
        text = ""
    # encode returns a 2D array when given a list
    emb = _embedder.encode([text], normalize_embeddings=True)
    vec = emb[0].astype("float32")
    return vec
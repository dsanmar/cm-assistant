"""
parse_pdf.py
------------
Reads the NJDOT 2019 Standard Specifications PDF and saves
cleaned page text (for ALL divisions) into outputs/pages.jsonl.

Each line in pages.jsonl:
    {"page": <int>, "text": "<cleaned text>"}
"""

from pathlib import Path
import json
import re

import fitz  # PyMuPDF
from tqdm import tqdm


# Root = project root 
ROOT = Path(__file__).resolve().parents[1]

PDF_PATH = ROOT / "data" / "Standard_Specs_2019.pdf"
OUT_PATH = ROOT / "outputs" / "pages.jsonl"

# Heuristic header/footer patterns
HEADER_RE = re.compile(r"2019 STANDARD SPECIFICATIONS.*", re.I)
FOOTER_RE = re.compile(r"NEW JERSEY DEPARTMENT OF TRANSPORTATION.*", re.I)


def clean_page_text(txt: str) -> str:
    """
    Remove headers, footers, and compress whitespace into single spaces.
    """
    lines = []
    for line in txt.splitlines():
        if HEADER_RE.search(line) or FOOTER_RE.search(line):
            continue
        stripped = line.strip()
        if stripped:
            lines.append(stripped)

    joined = " ".join(lines)
    # collapse multiple spaces
    joined = re.sub(r"\s{2,}", " ", joined)
    return joined.strip()


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"[info] Opening PDF: {PDF_PATH}")
    doc = fitz.open(PDF_PATH)

    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for i, page in enumerate(tqdm(doc, desc="Extracting pages"), start=1):
            raw = page.get_text("text")
            text = clean_page_text(raw)
            rec = {"page": i, "text": text}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"[✓] Wrote cleaned pages → {OUT_PATH}")


if __name__ == "__main__":
    main()

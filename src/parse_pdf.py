"""
Reads the NJDOT 2019 PDF and saves clean page text
"""

import fitz  # PyMuPDF
import json, re
from pathlib import Path
from tqdm import tqdm

PDF_PATH = Path("../data/Standard Specifications for Road and Bridge Construction 2019 ORIGINAL.pdf")
OUT_PATH = Path("../outputs/pages.jsonl")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

HEADER_RE = re.compile(r"2019 STANDARD SPECIFICATIONS.*", re.I)
FOOTER_RE = re.compile(r"NEW JERSEY DEPARTMENT OF TRANSPORTATION.*", re.I)

def clean_page_text(txt: str) -> str:
    """Remove headers, footers, and excess whitespace."""
    lines = []
    for line in txt.splitlines():
        if HEADER_RE.search(line) or FOOTER_RE.search(line):
            continue
        lines.append(line.strip())
    joined = " ".join(l for l in lines if l)
    return re.sub(r"\s{2,}", " ", joined)

def main():
    doc = fitz.open(PDF_PATH)
    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for i, page in enumerate(tqdm(doc, desc="Extracting pages"), start=1):
            text = clean_page_text(page.get_text("text"))
            rec = {"page": i, "text": text}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[✓] Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()

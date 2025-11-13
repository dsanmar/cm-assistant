"""
Splits cleaned page text into structured sections. 
  - Detects section headings (900, 901.01, etc.) and groups text
"""

import json, re
from pathlib import Path
from tqdm import tqdm

PAGES_PATH = Path("../outputs/pages.jsonl")
OUT_PATH = Path("../outputs/sections.jsonl")

# Patterns for NJDOT Section 900 hierarchy
H1 = re.compile(r"^(9\d{2})\s+[A-Z][A-Z\s]+$", re.M)          # e.x 900 MATERIALS
H2 = re.compile(r"^(9\d{2}\.\d{2})\s+[A-Z][A-Z\s]+$", re.M)   # e.x 901.01 DESCRIPTION
H3 = re.compile(r"^(9\d{2}\.\d{2}\([A-Z]\))", re.M)           # e.x 901.01(A)

def load_pages():
    return [json.loads(l) for l in open(PAGES_PATH, "r", encoding="utf-8")]

def main():
    pages = load_pages()
    sections, current = [], None

    for rec in tqdm(pages, desc="Building sections"):
        page, text = rec["page"], rec["text"]
        # Find headings in page
        matches = list(H3.finditer(text)) + list(H2.finditer(text)) + list(H1.finditer(text))
        matches = sorted(matches, key=lambda m: m.start())

        if matches:
            for m in matches:
                sec_id = m.group(1)
                if current:
                    current["page_end"] = page
                    sections.append(current)
                current = {"section_id": sec_id, "page_start": page, "text": ""}
        if current:
            current["text"] += " " + text

    # Final flush
    if current:
        current["page_end"] = pages[-1]["page"]
        sections.append(current)

    # Save
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for s in sections:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"[✓] {len(sections)} sections saved to {OUT_PATH}")

if __name__ == "__main__":
    main()

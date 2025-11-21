"""
extract_sections.py
-------------------
Splits cleaned page text into structured sections for ALL divisions.

Input:
    outputs/pages.jsonl  (from parse_pdf.py)

Output:
    outputs/sections.jsonl

Each line:
    {
      "section_id": "401",            
      "page_start": 123,
      "page_end": 125,
      "text": "full concatenated text for this section/subsection"
    }
"""

from pathlib import Path
import json
import re

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
PAGES_PATH = ROOT / "outputs" / "pages.jsonl"
OUT_PATH = ROOT / "outputs" / "sections.jsonl"

# Patterns for NJDOT hierarchy (generic, not just 900s)
#H1 = re.compile(r"^(\d{3})\s+[A-Z][A-Z0-9 ,()/\-]+$", re.M)
#H2 = re.compile(r"^(\d{3}\.\d{2})\s+[A-Z][A-Z0-9 ,()/\-]+$", re.M)
#H3 = re.compile(r"^(\d{3}\.\d{2}\([A-Z]\))", re.M) 

H3 = re.compile(r"\b(\d{3}\.\d{2}\([A-Z0-9]\))")      # 401.03(A)
H2 = re.compile(r"\b(\d{3}\.\d{2})\s+[A-Z][A-Z\s]+")  # 401.03 DESCRIPTION
H1 = re.compile(r"\b(\d{3})\s+[A-Z][A-Z\s]+")         # 401 HOT MIX ASPHALT


def load_pages():
    pages = []
    with open(PAGES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            pages.append(json.loads(line))
    return pages


def main():
    pages = load_pages()
    sections = []
    current = None

    for rec in tqdm(pages, desc="Building sections"):
        page = rec["page"]
        text = rec["text"]

        # find all headings on this page
        matches = list(H3.finditer(text)) + list(H2.finditer(text)) + list(H1.finditer(text))
        matches = sorted(matches, key=lambda m: m.start())

        if matches:
            for m in matches:
                sec_id = m.group(1)
                # close out previous section
                if current:
                    current["page_end"] = page
                    sections.append(current)
                # start new section record
                current = {"section_id": sec_id, "page_start": page, "text": ""}

        # append page text to current section
        if current:
            current["text"] += " " + text

    # flush last section
    if current:
        current["page_end"] = pages[-1]["page"]
        sections.append(current)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for s in sections:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"[✓] Saved {len(sections)} sections → {OUT_PATH}")


if __name__ == "__main__":
    main()

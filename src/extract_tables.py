"""
Extracts tabular data from Section 900 pages
"""

import camelot
from pathlib import Path
from tqdm import tqdm

# Project paths
ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = Path("../data/Standard Specifications for Road and Bridge Construction 2019 ORIGINAL.pdf")
OUT_DIR = Path("../outputs/tables")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Page window for Section 900 (approx – adjust later if needed)
START_PAGE = 580
END_PAGE = 649  # inclusive


def extract_page(page_num: int, table_index_offset: int) -> int:
    """
    Extract tables from a single PDF page.

    Returns the number of tables saved for this page.
    `table_index_offset` is used to keep numbering continuous across pages.
    """
    saved = 0
    page_str = str(page_num)

    # Try stream first
    try:
        tables = camelot.read_pdf(
            str(PDF_PATH),
            pages=page_str,
            flavor="stream"
        )
    except Exception as e:
        print(f"[page {page_num}] stream flavor failed: {e}")
        tables = []

    # If stream found nothing, try lattice
    if not tables:
        try:
            tables = camelot.read_pdf(
                str(PDF_PATH),
                pages=page_str,
                flavor="lattice"
            )
        except Exception as e:
            print(f"[page {page_num}] lattice flavor also failed: {e}")
            tables = []

    if not tables:
        print(f"[page {page_num}] No tables detected.")
        return 0

    # Save each table as CSV
    for idx, t in enumerate(tables, start=1):
        out_file = OUT_DIR / f"table_{table_index_offset + saved + idx:03}.csv"
        t.to_csv(out_file)
    saved = len(tables)
    print(f"[page {page_num}] Saved {saved} table(s).")

    return saved


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found at: {PDF_PATH}")

    print(f"Extracting tables from pages {START_PAGE}-{END_PAGE} ...")
    total_saved = 0

    # Iterate page by page to avoid one bad page breaking everything
    for page in tqdm(range(START_PAGE, END_PAGE + 1), desc="Pages"):
        try:
            saved_for_page = extract_page(page, total_saved)
            total_saved += saved_for_page
        except Exception as e:
            # Just log and continue
            print(f"[page {page}] ERROR: {e} (skipping this page)")
            continue

    print(f"\n[✓] Finished. Total tables saved: {total_saved}")
    print(f"    Output directory: {OUT_DIR}")


if __name__ == "__main__":
    main()

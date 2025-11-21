"""
inspect_chunks.py
-----------------
Utility to inspect random or targeted text chunks
from spec_metadata.jsonl to verify chunk quality.
"""

import json
import random
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

CHUNKS_PATH = Path("../outputs/spec_metadata.jsonl")

def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def show_random_chunk(chunks):
    chunk = random.choice(chunks)
    console.print(Panel.fit(
        chunk["text"],
        title=f"🔹 Section {chunk.get('section_id')} | Tokens: {chunk.get('n_tokens')}",
        border_style="cyan"
    ))

def show_section(chunks, section_id):
    matches = [c for c in chunks if c["section_id"] == section_id]
    if not matches:
        console.print(f"[red]No chunks found for section {section_id}[/red]")
        return
    for c in matches:
        console.print(Panel.fit(
            c["text"],
            title=f"📘 Section {c['section_id']} (Chunk)",
            border_style="green"
        ))

def main():
    chunks = load_chunks()
    console.print(f"[bold green]Loaded {len(chunks)} chunks.[/bold green]")

    while True:
        console.print("\n[bold yellow]Options:[/bold yellow]")
        console.print("1. Show random chunk")
        console.print("2. Show chunks by section ID (e.g., 106.05)")
        console.print("3. Quit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            show_random_chunk(chunks)
        elif choice == "2":
            sec = input("Enter section ID: ").strip()
            show_section(chunks, sec)
        elif choice == "3":
            break
        else:
            console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    main()

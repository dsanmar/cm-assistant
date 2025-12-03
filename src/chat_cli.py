from rag_pipeline import answer_question

def main():
    print("NJDOT C&M Spec Assistant (CLI)")
    while True:
        q = input("\nAsk a question (or 'quit'): ").strip()
        if q.lower() in {"quit", "exit"}:
            break
        result = answer_question(q)
        print("\nAnswer:\n", result["answer"])
        print("\nSources:")
        for s in result["sources"]:
            print(
                f"  - Section {s['section_id']} (pages {s['page_start']}–{s['page_end']})"
            )

if __name__ == "__main__":
    main()
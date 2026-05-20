import json
import csv
import requests

EVAL_FILE = "evaluation/eval_questions.jsonl"
OUTPUT_FILE = "evaluation/faithfulness_review.csv"
API_URL = "http://localhost:8000/query"


def main():
    rows = []

    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON on line {line_number}")
                continue

            question = item.get("question")
            expected_answer = item.get("expected_answer", "")
            expected_filename = item.get("expected_filename")
            expected_page = item.get("expected_page")

            response = requests.post(
                API_URL,
                json={
                    "query": question,
                    "top_k": 8
                },
                timeout=180
            )

            response.raise_for_status()
            result = response.json()

            generated_answer = result.get("answer", "")
            sources = result.get("sources", [])
            retrieved_context = result.get("retrieved_context", [])

            source_text = "; ".join(
                [
                    f"{s.get('filename')}#page={s.get('page')} score={round(s.get('score', 0), 4)}"
                    for s in sources
                ]
            )

            context_text = "\n\n---\n\n".join(
                [
                    f"[{c.get('source')} | score={round(c.get('score', 0), 4)}]\n{c.get('text')}"
                    for c in retrieved_context
                ]
            )

            rows.append({
                "question": question,
                "expected_answer": expected_answer,
                "expected_filename": expected_filename,
                "expected_page": expected_page,
                "generated_answer": generated_answer,
                "retrieved_sources": source_text,
                "retrieved_context": context_text,
                "answer_correct": "",
                "faithful": "",
                "notes": ""
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "question",
                "expected_answer",
                "expected_filename",
                "expected_page",
                "generated_answer",
                "retrieved_sources",
                "retrieved_context",
                "answer_correct",
                "faithful",
                "notes"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved faithfulness review file to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
import json
import time


def evaluate_retrieval(eval_file, embedder, vector_store, top_k=5):
    total = 0
    correct = 0
    reciprocal_ranks = []
    latencies = []
    skipped = 0
    errors = []

    with open(eval_file, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            # Skip blank lines
            if not line:
                skipped += 1
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append({
                    "line": line_number,
                    "error": str(e),
                    "content": line[:120]
                })
                skipped += 1
                continue

            question = item.get("question")
            expected_filename = item.get("expected_filename")
            expected_page = item.get("expected_page")

            # Skip unanswerable questions for retrieval accuracy
            if not expected_filename or expected_page is None:
                skipped += 1
                continue

            start = time.time()

            query_vector = embedder.embed_query(question)
            results = vector_store.search(query_vector, top_k=top_k)

            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)

            total += 1

            found = False
            rank = None

            for i, result in enumerate(results):
                if (
                    result["filename"] == expected_filename
                    and result["page"] == expected_page
                ):
                    found = True
                    rank = i + 1
                    break

            if found:
                correct += 1
                reciprocal_ranks.append(1 / rank)
            else:
                reciprocal_ranks.append(0)

    recall_at_k = correct / total if total else 0
    mrr = sum(reciprocal_ranks) / total if total else 0
    avg_latency_ms = sum(latencies) / len(latencies) if latencies else 0

    return {
        "total_answerable_questions": total,
        "correct_retrievals": correct,
        "skipped_lines_or_unanswerable_questions": skipped,
        f"recall@{top_k}": round(recall_at_k, 4),
        "mrr": round(mrr, 4),
        "avg_retrieval_latency_ms": round(avg_latency_ms, 2),
        "json_errors": errors[:10]
    }
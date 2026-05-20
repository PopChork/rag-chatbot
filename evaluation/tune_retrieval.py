import csv
import time
from pathlib import Path

from app.services.document_loader import extract_document_text
from app.services.chunker import chunk_pages
from app.services.embedder import Embedder
from app.services.vector_store import VectorStore
from app.services.evaluator import evaluate_retrieval


UPLOAD_DIR = Path("data/uploads")
EVAL_FILE = "evaluation/eval_questions.jsonl"
OUTPUT_FILE = "evaluation/tuning_results.csv"


CONFIGS = [
    {"chunk_size": 400, "chunk_overlap": 50, "top_k": 5},
    {"chunk_size": 500, "chunk_overlap": 75, "top_k": 5},
    {"chunk_size": 600, "chunk_overlap": 100, "top_k": 5},
    {"chunk_size": 700, "chunk_overlap": 100, "top_k": 5},
    {"chunk_size": 800, "chunk_overlap": 120, "top_k": 5},
    {"chunk_size": 900, "chunk_overlap": 150, "top_k": 5},
    {"chunk_size": 1000, "chunk_overlap": 150, "top_k": 5},

    {"chunk_size": 600, "chunk_overlap": 100, "top_k": 3},
    {"chunk_size": 600, "chunk_overlap": 100, "top_k": 8},
    {"chunk_size": 600, "chunk_overlap": 100, "top_k": 10},

    {"chunk_size": 800, "chunk_overlap": 80, "top_k": 5},
    {"chunk_size": 800, "chunk_overlap": 160, "top_k": 5},
    {"chunk_size": 800, "chunk_overlap": 200, "top_k": 5},
]


def load_documents():
    files = []

    for path in UPLOAD_DIR.iterdir():
        if path.suffix.lower() in [".pdf", ".txt"]:
            files.append(path)

    if not files:
        raise RuntimeError(f"No PDF/TXT files found in {UPLOAD_DIR}")

    return sorted(files)


def ingest_documents(embedder, vector_store, files, chunk_size, chunk_overlap):
    total_chunks = 0
    ingest_start = time.time()

    for path in files:
        file_bytes = path.read_bytes()

        pages = extract_document_text(
            file_bytes=file_bytes,
            filename=path.name
        )

        chunks = chunk_pages(
            pages=pages,
            filename=path.name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        if not chunks:
            print(f"[WARN] No chunks created for {path.name}")
            continue

        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedder.embed_texts(texts)

        vector_store.upsert_chunks(chunks, embeddings)

        total_chunks += len(chunks)

    ingest_latency_ms = round((time.time() - ingest_start) * 1000, 2)

    return total_chunks, ingest_latency_ms


def main():
    files = load_documents()
    embedder = Embedder()

    rows = []

    for config in CONFIGS:
        chunk_size = config["chunk_size"]
        chunk_overlap = config["chunk_overlap"]
        top_k = config["top_k"]

        collection_name = f"rag_tune_cs{chunk_size}_ov{chunk_overlap}_k{top_k}"

        print("=" * 80)
        print(f"Running config: {config}")
        print(f"Collection: {collection_name}")

        vector_store = VectorStore(
            vector_size=embedder.embedding_dim,
            collection_name=collection_name
        )

        vector_store.reset_collection()

        total_chunks, ingest_latency_ms = ingest_documents(
            embedder=embedder,
            vector_store=vector_store,
            files=files,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        metrics = evaluate_retrieval(
            eval_file=EVAL_FILE,
            embedder=embedder,
            vector_store=vector_store,
            top_k=top_k
        )

        recall_key = f"recall@{top_k}"

        row = {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "top_k": top_k,
            "collection_name": collection_name,
            "total_chunks": total_chunks,
            "ingest_latency_ms": ingest_latency_ms,
            "total_answerable_questions": metrics.get("total_answerable_questions"),
            "correct_retrievals": metrics.get("correct_retrievals"),
            "recall": metrics.get(recall_key),
            "mrr": metrics.get("mrr"),
            "avg_retrieval_latency_ms": metrics.get("avg_retrieval_latency_ms"),
            "skipped": metrics.get("skipped_lines_or_unanswerable_questions"),
            "json_error_count": len(metrics.get("json_errors", []))
        }

        rows.append(row)

        print(row)

    rows = sorted(
        rows,
        key=lambda x: (
            x["recall"],
            x["mrr"],
            -x["avg_retrieval_latency_ms"]
        ),
        reverse=True
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "chunk_size",
                "chunk_overlap",
                "top_k",
                "collection_name",
                "total_chunks",
                "ingest_latency_ms",
                "total_answerable_questions",
                "correct_retrievals",
                "recall",
                "mrr",
                "avg_retrieval_latency_ms",
                "skipped",
                "json_error_count"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 80)
    print(f"Saved tuning results to {OUTPUT_FILE}")
    print("Best config:")
    print(rows[0])


if __name__ == "__main__":
    main()
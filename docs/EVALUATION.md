# Evaluation Guide

This project includes two evaluation workflows:

1. Retrieval evaluation, which checks whether the correct source page appears in the retrieved top-k chunks.
2. Manual faithfulness review, which checks whether generated answers are correct and supported by retrieved context.

## Evaluation Dataset

Evaluation questions are stored in:

```text
evaluation/eval_questions.jsonl
```

Each line is a JSON object. Answerable questions should include:

```json
{
  "question": "What are the core components of an AI agent?",
  "expected_answer": "The core components include the LLM, reasoning and policy, tools, memory, planning, and reflection.",
  "expected_filename": "example.pdf",
  "expected_page": 10
}
```

Questions without `expected_filename` or `expected_page` are skipped during retrieval accuracy evaluation. This allows the file to contain unanswerable or open-ended review cases without distorting retrieval metrics.

## Retrieval Metrics

The retrieval evaluator reports:

| Metric | Meaning |
|---|---|
| `total_answerable_questions` | Number of evaluation questions with expected source filename and page |
| `correct_retrievals` | Number of questions where the expected source page appeared in the top-k results |
| `recall@k` | `correct_retrievals / total_answerable_questions` |
| `mrr` | Mean Reciprocal Rank of the expected source page |
| `avg_retrieval_latency_ms` | Average retrieval time per question |
| `skipped_lines_or_unanswerable_questions` | Blank, malformed, or unanswerable lines skipped |
| `json_errors` | JSON parsing errors, capped in the response |

## Running Retrieval Evaluation Through the API

Start the backend and make sure the relevant documents have already been indexed into Qdrant.

```bash
curl -X POST "http://localhost:8000/evaluate/retrieval"
```

Example output:

```json
{
  "total_answerable_questions": 95,
  "correct_retrievals": 85,
  "skipped_lines_or_unanswerable_questions": 15,
  "recall@8": 0.8947,
  "mrr": 0.6662,
  "avg_retrieval_latency_ms": 5.4,
  "json_errors": []
}
```

## Running Retrieval Tuning

The tuning script tests different chunk sizes, chunk overlaps, and top-k values.

Place the local evaluation documents in:

```text
data/uploads/
```

Then run:

```bash
python evaluation/tune_retrieval.py
```

The script writes results to:

```text
evaluation/tuning_results.csv
```

## Included Tuning Result Summary

The best recorded configuration in the included tuning results is:

| Chunk size | Chunk overlap | Top-k | Total chunks | Answerable questions | Correct retrievals | Recall | MRR | Avg retrieval latency |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 600 | 100 | 8 | 552 | 95 | 85 | 0.8947 | 0.6662 | 5.40 ms |

The top two configurations by recall were:

| Chunk size | Chunk overlap | Top-k | Recall | MRR | Avg retrieval latency |
|---:|---:|---:|---:|---:|---:|
| 600 | 100 | 8 | 0.8947 | 0.6662 | 5.40 ms |
| 600 | 100 | 10 | 0.8947 | 0.6662 | 5.70 ms |

The `top_k=8` setting was preferred because it achieved the same recall and MRR as `top_k=10` with slightly lower retrieval latency and less context passed into the LLM.

## Manual Faithfulness Review

Run the faithfulness review script after documents have been indexed and the FastAPI server is running:

```bash
python evaluation/run_faithfulness_eval.py
```

The script sends each question in `eval_questions.jsonl` to the `/query` endpoint and writes:

```text
evaluation/faithfulness_review.csv
```

Reviewers then manually fill in:

| Column | Label guide |
|---|---|
| `answer_correct` | `1` if the generated answer is correct, otherwise `0` |
| `faithful` | `1` if the answer is supported by retrieved context, otherwise `0` |
| `notes` | Brief reason for failure or any useful observation |

## Suggested Review Rules

Use `answer_correct = 1` when:

- The generated answer matches the expected answer.
- The answer is phrased differently but preserves the key meaning.
- Minor wording differences do not affect correctness.

Use `answer_correct = 0` when:

- The answer misses an important point.
- The answer contradicts the expected answer.
- The answer gives a vague response when the expected answer is specific.

Use `faithful = 1` when:

- The generated answer is clearly supported by the retrieved context.
- The model refuses to answer because the retrieved context is insufficient.

Use `faithful = 0` when:

- The answer introduces unsupported claims.
- The answer uses outside knowledge not found in the retrieved context.
- The answer contradicts the retrieved context.

## Interpreting Correctness vs Faithfulness

Correctness and faithfulness are related but not identical:

| Case | Meaning |
|---|---|
| Correct and faithful | Ideal output: the answer is right and supported by context |
| Incorrect but faithful | Retrieval likely failed or context was insufficient, but the model stayed grounded |
| Correct but unfaithful | The model guessed correctly or used outside knowledge |
| Incorrect and unfaithful | Both retrieval/generation quality and grounding failed |

## Privacy Warning

Evaluation files may contain lecture-note text, generated answers, or retrieved context. Do not publish these files publicly unless you have permission to share the underlying documents.

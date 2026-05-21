# API Reference

Base URL:

```text
http://localhost:8000
```

Interactive documentation is available at:

```text
http://localhost:8000/docs
```

## GET `/health`

Checks whether the FastAPI backend is running.

### Example

```bash
curl http://localhost:8000/health
```

### Response

```json
{
  "status": "ok"
}
```

## POST `/documents/upload`

Uploads a PDF or TXT document, extracts its text, chunks it, embeds the chunks, and stores them in Qdrant.

### Request

Content type: `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---:|---|
| `file` | file | Yes | PDF or TXT file to index |

### Example

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@data/uploads/example.pdf"
```

### Response

```json
{
  "message": "Document uploaded and indexed successfully.",
  "doc_id": "4bb7e52e-2d5e-4b42-bbcb-42fb42e62563",
  "filename": "example.pdf",
  "chunks_indexed": 42
}
```

## POST `/retrieve`

Retrieves top-k relevant chunks for a query without calling the LLM. This is useful for debugging retrieval quality.

### Request Body

```json
{
  "query": "What are the core components of an AI agent?",
  "top_k": 5,
  "doc_id": "optional-document-id"
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `query` | string | Yes | User question or search query |
| `top_k` | integer | No | Number of chunks to retrieve |
| `doc_id` | string/null | No | Restrict retrieval to one uploaded document |

### Example

```bash
curl -X POST "http://localhost:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the core components of an AI agent?","top_k":5}'
```

### Response

```json
{
  "query": "What are the core components of an AI agent?",
  "results": [
    {
      "score": 0.8123,
      "text": "...retrieved chunk text...",
      "filename": "example.pdf",
      "page": 10,
      "source": "example.pdf#page=10",
      "doc_id": "4bb7e52e-2d5e-4b42-bbcb-42fb42e62563",
      "chunk_index": 0
    }
  ]
}
```

## POST `/query`

Runs the full RAG pipeline: embeds the user query, retrieves relevant chunks from Qdrant, sends the context to Ollama, and returns a grounded answer with sources.

### Request Body

```json
{
  "query": "What are the core components of an AI agent?",
  "top_k": 8
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `query` | string | Yes | User question |
| `top_k` | integer | No | Number of retrieved chunks used as context |

### Example

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the core components of an AI agent?","top_k":8}'
```

### Response

```json
{
  "question": "What are the core components of an AI agent?",
  "answer": "The core components include the LLM, reasoning and policy, tools, memory, planning, and reflection.",
  "sources": [
    {
      "filename": "example.pdf",
      "page": 10,
      "source": "example.pdf#page=10",
      "score": 0.8123
    }
  ],
  "retrieved_context": [
    {
      "text": "...retrieved context used by the LLM...",
      "source": "example.pdf#page=10",
      "score": 0.8123
    }
  ],
  "latency_ms": 1532.44
}
```

## POST `/evaluate/retrieval`

Evaluates retrieval quality against `evaluation/eval_questions.jsonl` using the currently indexed Qdrant collection.

### Example

```bash
curl -X POST "http://localhost:8000/evaluate/retrieval"
```

### Response

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

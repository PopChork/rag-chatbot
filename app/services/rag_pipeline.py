import time
import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL


def answer_question(question: str, embedder, vector_store, top_k: int = 8):
    start_time = time.time()

    query_vector = embedder.embed_query(question)

    retrieved_chunks = vector_store.search(
        query_vector=query_vector,
        top_k=top_k
    )

    context = "\n\n".join(
        [
            f"[Source: {chunk['source']}]\n{chunk['text']}"
            for chunk in retrieved_chunks
        ]
    )

    answer = generate_answer_from_context(question, context)

    total_latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "question": question,
        "answer": answer,
        "sources": [
            {
                "filename": chunk["filename"],
                "page": chunk["page"],
                "source": chunk["source"],
                "score": chunk["score"]
            }
            for chunk in retrieved_chunks
        ],
        "retrieved_context": [
            {
                "text": chunk["text"],
                "source": chunk["source"],
                "score": chunk["score"]
            }
            for chunk in retrieved_chunks
        ],
        "latency_ms": total_latency_ms
    }


def generate_answer_from_context(question: str, context: str):
    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using only the provided context.

Rules:
- Use only the context below.
- Do not use outside knowledge.
- If the context does not contain the answer, say: "The document does not provide enough information."
- Be concise.
- Include source references when possible.

Context:
{context}

Question:
{question}

Answer:
""".strip()

    url = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You answer questions only using the provided document context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 512
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama request failed: {e}")

    data = response.json()

    return data["message"]["content"]
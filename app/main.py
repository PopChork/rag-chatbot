from fastapi import FastAPI, UploadFile, File, HTTPException
from app.services.document_loader import extract_document_text
from app.services.chunker import chunk_pages
from app.services.embedder import Embedder
from app.services.vector_store import VectorStore
from app.services.rag_pipeline import answer_question
from app.schemas import QueryRequest, RetrieveRequest
from app.services.evaluator import evaluate_retrieval
from app.config import TOP_K

app = FastAPI(title="RAG Chatbot API")

embedder = Embedder()
vector_store = VectorStore(vector_size=embedder.embedding_dim)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")

    content = await file.read()

    pages = extract_document_text(content, file.filename)
    chunks = chunk_pages(pages, file.filename)

    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)

    doc_id = vector_store.upsert_chunks(chunks, embeddings)

    return {
        "message": "Document uploaded and indexed successfully.",
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks_indexed": len(chunks)
    }


@app.post("/retrieve")
def retrieve(request: RetrieveRequest):
    query_vector = embedder.embed_query(request.query)

    results = vector_store.search(
        query_vector=query_vector,
        top_k=request.top_k,
        doc_id=request.doc_id
    )

    return {
        "query": request.query,
        "results": results
    }


@app.post("/query")
def query(request: QueryRequest):
    result = answer_question(
        question=request.query,
        embedder=embedder,
        vector_store=vector_store,
        top_k=request.top_k
    )

    return result


@app.post("/evaluate/retrieval")
def evaluate_retrieval_endpoint():
    return evaluate_retrieval(
        eval_file="evaluation/eval_questions.jsonl",
        embedder=embedder,
        vector_store=vector_store,
        top_k=TOP_K
    )
# RAG Chatbot for Lecture Notes

A FastAPI-based Retrieval-Augmented Generation (RAG) chatbot that allows users to upload PDF or TXT documents, index them into a vector database, retrieve relevant chunks, and generate answers using a local LLM through Ollama.

The project was designed for querying lecture notes and evaluating retrieval quality using manually prepared question-answer pairs with expected source pages.

## Features

- Upload and index PDF or TXT documents
- Extract page-level text from PDFs
- Split documents into overlapping text chunks
- Generate embeddings using SentenceTransformers
- Store and search document chunks using Qdrant
- Retrieve top-k relevant chunks for a query
- Generate grounded answers using Ollama
- Return source metadata such as filename, page number, similarity score, and retrieved context
- Evaluate retrieval performance using Recall@k, MRR, and average retrieval latency
- Support manual faithfulness review of generated answers

## Tech Stack

- **Backend:** FastAPI
- **Vector Database:** Qdrant
- **Embeddings:** SentenceTransformers
- **LLM Runtime:** Ollama
- **PDF Parsing:** pypdf
- **Containerization:** Docker, Docker Compose
- **Evaluation:** Custom Python scripts for retrieval tuning and faithfulness review

## Project Structure

RAG-CHATBOT/
├── app/
│   ├── main.py                 # FastAPI routes
│   ├── config.py               # Environment-based configuration
│   ├── schemas.py              # Request schemas
│   └── services/
│       ├── document_loader.py  # PDF/TXT text extraction
│       ├── chunker.py          # Text chunking
│       ├── embedder.py         # SentenceTransformer embeddings
│       ├── vector_store.py     # Qdrant collection and search logic
│       ├── rag_pipeline.py     # Retrieval + Ollama answer generation
│       └── evaluator.py        # Retrieval evaluation metrics
├── data/
│   └── uploads/                # Local documents used for tuning/evaluation
├── evaluation/
│   ├── eval_questions.jsonl    # Evaluation questions and expected source pages
│   ├── tune_retrieval.py       # Retrieval tuning script
│   ├── tuning_results.csv      # Retrieval tuning output
│   ├── run_faithfulness_eval.py
│   ├── faithfulness_review.csv
│   └── faithfulness_review_filled.csv
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
>>>>>>> 7bedf8c (Initial RAG chatbot implementation)

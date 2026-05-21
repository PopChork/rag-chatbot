"use client";

import { FormEvent, useEffect, useState } from "react";

type IndexedDocument = {
  doc_id: string;
  filename: string;
  chunk_count: number;
  page_count: number;
  pages: number[];
};

type Source = {
  filename: string;
  page: number;
  source: string;
  score: number;
};

type RetrievedContext = {
  text: string;
  source: string;
  score: number;
};

type QueryResponse = {
  question: string;
  answer: string;
  sources: Source[];
  retrieved_context?: RetrievedContext[];
  latency_ms: number;
};

export default function Home() {
  const [documents, setDocuments] = useState<IndexedDocument[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(8);
  const [querying, setQuerying] = useState(false);
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);

  const [error, setError] = useState<string | null>(null);

  async function loadDocuments() {
    try {
      const response = await fetch("/api/documents");
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail ?? "Failed to load documents");
      }

      setDocuments(data.documents ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleUpload(event: FormEvent) {
    event.preventDefault();

    if (!selectedFile) {
      setError("Please choose a PDF or TXT file first.");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail ?? "Upload failed");
      }

      setSelectedFile(null);
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(event: FormEvent) {
    event.preventDefault();

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setQuerying(true);
    setError(null);
    setQueryResult(null);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: question,
          top_k: topK,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail ?? "Query failed");
      }

      setQueryResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setQuerying(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl px-6 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">
            RAG Document Chatbot
          </h1>
          <p className="mt-2 text-slate-400">
            Upload PDFs, index documents, ask questions, and inspect retrieved
            source chunks.
          </p>
        </header>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/40 bg-red-950/40 p-4 text-red-200">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
          <section className="space-y-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg">
              <h2 className="text-xl font-semibold">Upload PDF/TXT</h2>

              <form onSubmit={handleUpload} className="mt-4 space-y-4">
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={(event) =>
                    setSelectedFile(event.target.files?.[0] ?? null)
                  }
                  className="block w-full cursor-pointer rounded-lg border border-slate-700 bg-slate-950 p-2 text-sm text-slate-300 file:mr-4 file:rounded-md file:border-0 file:bg-slate-700 file:px-3 file:py-2 file:text-slate-100 hover:file:bg-slate-600"
                />

                <button
                  type="submit"
                  disabled={uploading}
                  className="w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {uploading ? "Uploading and indexing..." : "Upload Document"}
                </button>
              </form>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xl font-semibold">Indexed Documents</h2>

                <button
                  onClick={loadDocuments}
                  className="rounded-lg border border-slate-700 px-3 py-1 text-sm text-slate-300 hover:bg-slate-800"
                >
                  Refresh
                </button>
              </div>

              <div className="mt-4 space-y-3">
                {documents.length === 0 ? (
                  <p className="text-sm text-slate-400">
                    No indexed documents yet.
                  </p>
                ) : (
                  documents.map((doc) => (
                    <div
                      key={doc.doc_id}
                      className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                    >
                      <p className="break-words font-medium">{doc.filename}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        {doc.chunk_count} chunks · {doc.page_count} pages
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        ID: {doc.doc_id}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>

          <section className="space-y-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg">
              <h2 className="text-xl font-semibold">Ask a Question</h2>

              <form onSubmit={handleAsk} className="mt-4 space-y-4">
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Example: What is a Nash equilibrium?"
                  rows={4}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-slate-100 outline-none focus:border-blue-500"
                />

                <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <label className="flex items-center gap-2 text-sm text-slate-300">
                    Top-K:
                    <input
                      type="number"
                      min={1}
                      max={20}
                      value={topK}
                      onChange={(event) =>
                        setTopK(Number(event.target.value))
                      }
                      className="w-20 rounded-lg border border-slate-700 bg-slate-950 p-2 text-slate-100"
                    />
                  </label>

                  <button
                    type="submit"
                    disabled={querying}
                    className="rounded-lg bg-emerald-600 px-5 py-2 font-medium text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {querying ? "Generating answer..." : "Ask"}
                  </button>
                </div>
              </form>
            </div>

            {queryResult && (
              <div className="space-y-6">
                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg">
                  <div className="flex flex-col justify-between gap-2 sm:flex-row">
                    <h2 className="text-xl font-semibold">Answer</h2>
                    <p className="text-sm text-slate-400">
                      Latency: {queryResult.latency_ms} ms
                    </p>
                  </div>

                  <p className="mt-4 whitespace-pre-wrap leading-7 text-slate-100">
                    {queryResult.answer}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg">
                  <h2 className="text-xl font-semibold">Retrieved Sources</h2>

                  <div className="mt-4 space-y-3">
                    {queryResult.sources?.map((source, index) => (
                      <div
                        key={`${source.source}-${index}`}
                        className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                      >
                        <div className="flex flex-col justify-between gap-2 sm:flex-row">
                          <div>
                            <p className="font-medium">{source.filename}</p>
                            <p className="text-sm text-slate-400">
                              Page {source.page} · {source.source}
                            </p>
                          </div>

                          <p className="text-sm font-semibold text-blue-300">
                            Score: {source.score?.toFixed(4)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg">
                  <h2 className="text-xl font-semibold">Source Chunks</h2>

                  <div className="mt-4 space-y-4">
                    {queryResult.retrieved_context?.map((chunk, index) => (
                      <details
                        key={`${chunk.source}-${index}`}
                        className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                      >
                        <summary className="cursor-pointer font-medium text-slate-200">
                          {chunk.source} · Score {chunk.score?.toFixed(4)}
                        </summary>

                        <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-300">
                          {chunk.text}
                        </p>
                      </details>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
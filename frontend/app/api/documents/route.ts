export async function GET() {
  const backendUrl = process.env.RAG_API_BASE_URL ?? "http://localhost:8000";

  const response = await fetch(`${backendUrl}/documents`, {
    cache: "no-store",
  });

  const data = await response.json();

  return Response.json(data, {
    status: response.status,
  });
}
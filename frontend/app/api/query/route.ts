export async function POST(request: Request) {
  const backendUrl = process.env.RAG_API_BASE_URL ?? "http://localhost:8000";
  const body = await request.json();

  const response = await fetch(`${backendUrl}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();

  return Response.json(data, {
    status: response.status,
  });
}
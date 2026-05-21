export async function POST(request: Request) {
  const backendUrl = process.env.RAG_API_BASE_URL ?? "http://localhost:8000";
  const formData = await request.formData();

  const response = await fetch(`${backendUrl}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  return Response.json(data, {
    status: response.status,
  });
}
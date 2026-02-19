const API_BASE_URL = (
  process.env.API_BASE_URL || "http://localhost:8000"
).replace(/\/+$/, "");

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "无效的请求体" }, { status: 400 });
  }

  try {
    const upstream = await fetch(`${API_BASE_URL}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30_000),
    });

    if (!upstream.ok) {
      const text = await upstream.text().catch(() => "");
      return new Response(text || upstream.statusText, {
        status: upstream.status,
      });
    }

    const data = await upstream.json();
    return Response.json(data);
  } catch (err) {
    const message =
      err instanceof TypeError
        ? "无法连接到后端服务，请确保 FastAPI 服务正在运行"
        : "后端请求失败";
    return Response.json({ error: message }, { status: 502 });
  }
}

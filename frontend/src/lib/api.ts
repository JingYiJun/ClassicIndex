export interface SearchResult {
  book: string;
  page: number;
  content: string;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
}

export async function searchApi(
  query: string,
  topK: number
): Promise<SearchResponse> {
  const response = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(
      data?.error || `请求失败: ${response.status}`
    );
  }

  return response.json();
}

import { getToken } from "./auth";
import { API_BASE } from "./config";

// 사용자별 즐겨찾기/최근 (서버 동기화). 기기가 바뀌어도 계정 기준으로 유지.

function authHeaders(): Record<string, string> {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

export async function fetchFavorites(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/me/favorites`, { headers: authHeaders() });
  if (!res.ok) throw new Error("즐겨찾기 로드 실패");
  return ((await res.json()).data as string[]) || [];
}

export async function addFavoriteServer(id: string): Promise<void> {
  await fetch(`${API_BASE}/me/favorites`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ asset_id: id }),
  });
}

export async function removeFavoriteServer(id: string): Promise<void> {
  await fetch(`${API_BASE}/me/favorites/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
}

export async function fetchRecent(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/me/recent`, { headers: authHeaders() });
  if (!res.ok) throw new Error("최근 로드 실패");
  return ((await res.json()).data as string[]) || [];
}

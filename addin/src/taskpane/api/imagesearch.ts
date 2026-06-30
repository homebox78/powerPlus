import { getToken } from "./auth";
import { API_BASE } from "./config";

/** Openverse 이미지 검색 결과 1건 */
export interface ImageHit {
  id: string;
  title: string;
  thumb: string;
  url: string;
  source: string;
  creator: string;
  license: string;
  landing: string;
}

/** 무료 이미지(Openverse) 검색 — 서버 프록시 경유. */
export async function searchImages(
  q: string,
  page = 1,
  signal?: AbortSignal
): Promise<{ data: ImageHit[]; total: number }> {
  const token = getToken();
  const res = await fetch(`${API_BASE}/imagesearch?q=${encodeURIComponent(q)}&page=${page}`, {
    signal,
    cache: "no-store",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error(`이미지 검색 실패 (${res.status})`);
  const body = (await res.json()) as { data?: ImageHit[]; total?: number };
  return { data: body.data ?? [], total: body.total ?? 0 };
}

/** 외부 이미지를 동일 출처로 중계하는 프록시 URL(삽입 시 base64 변환용). */
export function imageProxyUrl(url: string): string {
  return `${API_BASE}/imageproxy?url=${encodeURIComponent(url)}`;
}

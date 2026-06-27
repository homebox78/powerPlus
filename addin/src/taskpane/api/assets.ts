import type { Asset } from "../data/mockAssets";
import { filterAssets } from "../data/mockAssets";

// 개발: webpack dev 서버가 /api 를 PHP 서버(http://localhost:8000)로 프록시.
// 운영: 같은 도메인에 배포하거나 환경에 맞게 절대 URL로 교체.
const API_BASE = "/api";

interface AssetsResponse {
  data: Asset[];
  total: number;
  page: number;
  limit: number;
}

export interface FetchResult {
  assets: Asset[];
  total: number;
  /** 서버 미연결로 로컬 mock을 사용했는지 여부 */
  offline: boolean;
}

/** 서버에서 자산 목록을 가져온다. 서버 미연결 시 로컬 mock으로 폴백. */
export async function fetchAssets(
  category: string,
  query: string,
  signal?: AbortSignal
): Promise<FetchResult> {
  const params = new URLSearchParams({
    category,
    q: query.trim(),
    page: "1",
    limit: "200",
  });

  try {
    const res = await fetch(`${API_BASE}/assets?${params.toString()}`, { signal });
    if (!res.ok) throw new Error(`서버 응답 ${res.status}`);
    const body = (await res.json()) as AssetsResponse;
    return { assets: body.data, total: body.total, offline: false };
  } catch (e) {
    // 요청이 취소된 경우는 상위에서 무시하도록 그대로 전파
    if (signal?.aborted) throw e;
    // 서버 미연결 → 로컬 mock 데이터로 폴백 (오프라인 데모)
    const assets = filterAssets(category, query);
    return { assets, total: assets.length, offline: true };
  }
}

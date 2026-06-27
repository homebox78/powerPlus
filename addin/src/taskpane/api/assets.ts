import type { Asset } from "../data/mockAssets";
import { filterAssets } from "../data/mockAssets";
import { getToken } from "./auth";
import { API_BASE } from "./config";

/** 로그인이 필요(401)함을 알리는 전용 에러 — 상위에서 로그인 화면으로 전환. */
export class AuthRequiredError extends Error {}

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

/** 서버에서 자산 목록을 가져온다(페이지 단위). 서버 미연결 시 로컬 mock으로 폴백. */
export async function fetchAssets(
  category: string,
  query: string,
  page = 1,
  limit = 60,
  signal?: AbortSignal,
  sort: string = "latest"
): Promise<FetchResult> {
  const params = new URLSearchParams({
    category,
    q: query.trim(),
    page: String(page),
    limit: String(limit),
    sort,
  });

  const token = getToken();

  try {
    const res = await fetch(`${API_BASE}/assets?${params.toString()}`, {
      signal,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (res.status === 401) throw new AuthRequiredError("로그인이 필요합니다.");
    if (!res.ok) throw new Error(`서버 응답 ${res.status}`);
    const body = (await res.json()) as AssetsResponse;
    return { assets: body.data, total: body.total, offline: false };
  } catch (e) {
    // 요청이 취소된 경우는 상위에서 무시하도록 그대로 전파
    if (signal?.aborted) throw e;
    // 인증 만료/누락은 mock 으로 가리지 말고 상위로 — 로그인 화면 전환
    if (e instanceof AuthRequiredError) throw e;
    // 서버 미연결 → 로컬 mock 데이터로 폴백 (오프라인 데모, mock은 소량이라 1페이지)
    const all = filterAssets(category, query);
    return { assets: page === 1 ? all : [], total: all.length, offline: true };
  }
}

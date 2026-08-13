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
  sort: string = "latest",
  kind: string = "",
  ptype: string = ""
): Promise<FetchResult> {
  const params = new URLSearchParams({
    category,
    q: query.trim(),
    page: String(page),
    limit: String(limit),
    sort,
  });
  if (kind) params.set("kind", kind);
  if (ptype) params.set("ptype", ptype);

  const token = getToken();

  try {
    const res = await fetch(`${API_BASE}/assets?${params.toString()}`, {
      signal,
      cache: "no-store",
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

/** 즐겨찾기·최근: id 목록으로 해당 자산만 조회(전체 과다 로드 회피). 서버 미연결 시 mock 폴백. */
export async function fetchByIds(ids: string[], signal?: AbortSignal): Promise<Asset[]> {
  if (!ids.length) return [];
  const token = getToken();
  try {
    const res = await fetch(`${API_BASE}/assets?ids=${encodeURIComponent(ids.join(","))}`, {
      signal,
      cache: "no-store",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (res.status === 401) throw new AuthRequiredError("로그인이 필요합니다.");
    if (!res.ok) throw new Error(`서버 응답 ${res.status}`);
    const body = (await res.json()) as { data: Asset[] };
    return body.data ?? [];
  } catch (e) {
    if (signal?.aborted || e instanceof AuthRequiredError) throw e;
    const set = new Set(ids);
    return filterAssets("all", "").filter((a) => set.has(a.id));
  }
}

/** 특정 자산과 유사한 자산 추천 목록(태그 중첩 기반). 실패 시 빈 배열. */
export async function fetchSimilar(
  id: string,
  limit = 12,
  signal?: AbortSignal
): Promise<Asset[]> {
  const token = getToken();
  try {
    const res = await fetch(
      `${API_BASE}/assets/${encodeURIComponent(id)}/similar?limit=${limit}`,
      {
        signal,
        cache: "no-store",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
    );
    if (res.status === 401) throw new AuthRequiredError("로그인이 필요합니다.");
    if (!res.ok) throw new Error(`서버 응답 ${res.status}`);
    const body = (await res.json()) as { data: Asset[] };
    return body.data ?? [];
  } catch (e) {
    if (signal?.aborted || e instanceof AuthRequiredError) throw e;
    return [];
  }
}

/** 같은 스타일 세트(같은 등록 배치) 자산 목록. 세트를 통째로 훑어보기 위한 용도. */
export async function fetchStyleSet(
  id: string,
  page = 1,
  limit = 60,
  signal?: AbortSignal
): Promise<{ data: Asset[]; total: number }> {
  const token = getToken();
  try {
    const res = await fetch(
      `${API_BASE}/assets/${encodeURIComponent(id)}/set?page=${page}&limit=${limit}`,
      {
        signal,
        cache: "no-store",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
    );
    if (res.status === 401) throw new AuthRequiredError("로그인이 필요합니다.");
    if (!res.ok) throw new Error(`서버 응답 ${res.status}`);
    const body = (await res.json()) as { data: Asset[]; total: number };
    return { data: body.data ?? [], total: body.total ?? 0 };
  } catch (e) {
    if (signal?.aborted || e instanceof AuthRequiredError) throw e;
    return { data: [], total: 0 };
  }
}

import { getToken } from "./auth";
import { API_BASE } from "./config";
import type { Category } from "../data/mockAssets";

interface CategoryRow {
  key: string;
  label: string;
}

/** 서버에서 카테고리 목록을 가져온다 (로그인 필요). 실패 시 상위에서 폴백 처리. */
export async function fetchCategories(): Promise<Category[]> {
  const token = getToken();
  const res = await fetch(`${API_BASE}/categories`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error("카테고리 로드 실패");
  const body = (await res.json()) as { data?: CategoryRow[] };
  return (body.data || []).map((c) => ({ key: c.key, label: c.label }));
}

import { getToken } from "./auth";
import { API_BASE } from "./config";

export interface Announcement {
  id: number;
  title: string;
  body: string | null;
  created_at: string;
}

/** 활성 공지 목록(최신순). 실패 시 빈 배열(알람은 부가기능이라 조용히 무시). */
export async function fetchAnnouncements(): Promise<Announcement[]> {
  const token = getToken();
  try {
    const res = await fetch(`${API_BASE}/announcements`, {
      cache: "no-store",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) return [];
    const body = (await res.json()) as { data?: Announcement[] };
    return body.data ?? [];
  } catch {
    return [];
  }
}

const SEEN_KEY = "pp_ann_seen";

/** 마지막으로 확인한 공지 id (이보다 큰 id = 미확인) */
export function getAnnSeen(): number {
  return Number(localStorage.getItem(SEEN_KEY) || "0") || 0;
}

export function setAnnSeen(id: number): void {
  localStorage.setItem(SEEN_KEY, String(id));
}

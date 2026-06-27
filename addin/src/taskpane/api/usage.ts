import { getToken } from "./auth";

// 자산 삽입 시 사용 기록을 서버에 남긴다 (통계용). 실패해도 삽입 흐름엔 영향 없음.
const API_BASE = "/api";

export async function recordUsage(assetId: string): Promise<void> {
  const token = getToken();
  if (!token) return;
  try {
    await fetch(`${API_BASE}/usage`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ asset_id: assetId }),
    });
  } catch {
    // 통계 기록 실패는 무시 (사용자 경험에 영향 없음)
  }
}

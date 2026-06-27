import { getToken } from "./auth";
import { API_BASE } from "./config";

export interface RequestPayload {
  type: string;
  title: string;
  description: string;
  link: string;
}

/** 콘텐츠 요청 전송. 성공하면 true. */
export async function submitRequest(payload: RequestPayload): Promise<boolean> {
  const token = getToken();
  try {
    const res = await fetch(`${API_BASE}/requests`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    });
    return res.ok;
  } catch {
    return false;
  }
}

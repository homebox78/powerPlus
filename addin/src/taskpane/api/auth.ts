// 이메일 OTP 인증 클라이언트.
// dev: webpack 프록시가 /api 를 PHP 서버로 전달. 토큰은 작업창 localStorage 에 보관.

const API_BASE = "/api";
const TOKEN_KEY = "pp_token";
const EMAIL_KEY = "pp_email";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getEmail(): string | null {
  return localStorage.getItem(EMAIL_KEY);
}

function setSession(token: string, email: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(EMAIL_KEY, email);
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(EMAIL_KEY);
}

export interface RequestCodeResult {
  /** auth_debug(개발) 일 때만 서버가 코드를 내려준다. */
  devCode?: string;
}

/** 인증코드 발송 요청. 실패 시 서버 메시지를 담은 Error 를 던진다. */
export async function requestCode(email: string): Promise<RequestCodeResult> {
  const res = await fetch(`${API_BASE}/auth/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.error || "인증코드 요청에 실패했습니다.");
  return { devCode: body.dev_code };
}

/** 코드 검증 → 성공 시 토큰 저장. 실패 시 Error. */
export async function verifyCode(email: string, code: string): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, code }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.error || "인증에 실패했습니다.");
  setSession(body.token, body.email);
}

/** 서버 세션 폐기 + 로컬 토큰 삭제. */
export async function logout(): Promise<void> {
  const token = getToken();
  clearSession();
  if (!token) return;
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch {
    // 네트워크 오류는 무시 — 로컬은 이미 정리됨
  }
}

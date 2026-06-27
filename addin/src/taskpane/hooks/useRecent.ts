import { useCallback, useState } from "react";

// 최근 사용(삽입)한 자산 ID 를 최신순으로 localStorage 에 보관 (기기별).
const KEY = "pp_recent";
const MAX = 20;

function load(): string[] {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || "[]");
    return Array.isArray(raw) ? (raw as string[]) : [];
  } catch {
    return [];
  }
}

export function useRecent() {
  const [recent, setRecent] = useState<string[]>(load);

  const pushRecent = useCallback((id: string) => {
    setRecent((prev) => {
      const next = [id, ...prev.filter((x) => x !== id)].slice(0, MAX);
      localStorage.setItem(KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  return { recent, pushRecent };
}

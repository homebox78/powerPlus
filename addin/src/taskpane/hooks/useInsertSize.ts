import { useCallback, useState } from "react";

// 삽입 크기 프리셋 (단위: pt — Office.js addImage 는 pt 사용).
export type InsertSizeKey = "small" | "medium" | "large";

export interface InsertSize {
  key: InsertSizeKey;
  label: string;
  pt: number;
}

export const INSERT_SIZES: InsertSize[] = [
  { key: "small", label: "작게", pt: 100 },
  { key: "medium", label: "보통", pt: 150 },
  { key: "large", label: "크게", pt: 250 },
];

const KEY = "pp_insert_size";
const DEFAULT: InsertSizeKey = "medium";

export function useInsertSize() {
  const [sizeKey, setSizeKey] = useState<InsertSizeKey>(() => {
    const v = localStorage.getItem(KEY) as InsertSizeKey | null;
    return v && INSERT_SIZES.some((s) => s.key === v) ? v : DEFAULT;
  });

  const setSize = useCallback((k: InsertSizeKey) => {
    setSizeKey(k);
    localStorage.setItem(KEY, k);
  }, []);

  const sizePt = (INSERT_SIZES.find((s) => s.key === sizeKey) ?? INSERT_SIZES[1]).pt;

  return { sizeKey, setSize, sizePt };
}

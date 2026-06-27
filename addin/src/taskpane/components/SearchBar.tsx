import * as React from "react";
import type { Category } from "../data/mockAssets";

interface Props {
  value: string;
  onChange: (q: string) => void;
  categories: Category[]; // 전체 + 분류
  category: string;
  onCategoryChange: (key: string) => void;
}

/** 분류 셀렉트 + 300ms 디바운스 검색. 분류를 고르면 그 분류 안에서 검색(전체면 통합검색). */
export default function SearchBar({ value, onChange, categories, category, onCategoryChange }: Props) {
  const [local, setLocal] = React.useState(value);
  const timer = React.useRef<number | undefined>(undefined);

  React.useEffect(() => setLocal(value), [value]);

  const handle = (v: string) => {
    setLocal(v);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => onChange(v), 300);
  };

  return (
    <div className="search">
      <select
        className="search__cat"
        value={category}
        onChange={(e) => onCategoryChange(e.target.value)}
        aria-label="분류 선택"
      >
        {categories.map((c) => (
          <option key={c.key} value={c.key}>
            {c.label}
          </option>
        ))}
      </select>
      <div className="search__field">
        <span className="search__icon" aria-hidden>🔍</span>
        <input
          className="search__input"
          type="search"
          aria-label="자산 검색"
          placeholder="태그로 검색"
          value={local}
          onChange={(e) => handle(e.target.value)}
        />
        {local && (
          <button className="search__clear" aria-label="검색어 지우기" onClick={() => handle("")}>
            ×
          </button>
        )}
      </div>
    </div>
  );
}

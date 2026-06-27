import * as React from "react";

interface Props {
  value: string;
  onChange: (q: string) => void;
}

/** 300ms 디바운스된 검색 입력. 부모에는 디바운스된 값을 전달. */
export default function SearchBar({ value, onChange }: Props) {
  const [local, setLocal] = React.useState(value);
  const timer = React.useRef<number | undefined>(undefined);

  // 외부에서 value가 리셋되면 동기화
  React.useEffect(() => setLocal(value), [value]);

  const handle = (v: string) => {
    setLocal(v);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => onChange(v), 300);
  };

  return (
    <div className="search">
      <span className="search__icon" aria-hidden>🔍</span>
      <input
        className="search__input"
        type="search"
        aria-label="자산 검색"
        placeholder="이름·태그로 검색 (예: 화살표)"
        value={local}
        onChange={(e) => handle(e.target.value)}
      />
      {local && (
        <button
          className="search__clear"
          aria-label="검색어 지우기"
          onClick={() => handle("")}
        >
          ×
        </button>
      )}
    </div>
  );
}

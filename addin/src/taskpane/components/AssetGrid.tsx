import * as React from "react";
import type { Asset } from "../data/mockAssets";

interface Props {
  assets: Asset[];
  insertingId: string | null;
  onInsert: (asset: Asset) => void;
}

export default function AssetGrid({ assets, insertingId, onInsert }: Props) {
  if (assets.length === 0) {
    return <div className="empty">결과가 없습니다.</div>;
  }

  return (
    <div className="grid">
      {assets.map((a) => (
        <button
          key={a.id}
          className="card"
          title={`${a.name} — 클릭하면 슬라이드에 삽입`}
          disabled={insertingId === a.id}
          onClick={() => onInsert(a)}
        >
          <div
            className="card__thumb"
            // SVG 문자열을 그대로 렌더 (mock 데이터). 신뢰된 내부 자산만 사용.
            dangerouslySetInnerHTML={{ __html: a.svg }}
          />
          <div className="card__name">
            {insertingId === a.id ? "삽입 중…" : a.name}
          </div>
        </button>
      ))}
    </div>
  );
}

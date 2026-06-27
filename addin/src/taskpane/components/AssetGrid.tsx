import * as React from "react";
import type { Asset } from "../data/mockAssets";

interface Props {
  assets: Asset[];
  insertingId: string | null;
  onInsert: (asset: Asset) => void;
  isFavorite: (id: string) => boolean;
  onToggleFavorite: (id: string) => void;
  emptyMessage?: string;
}

export default function AssetGrid({
  assets,
  insertingId,
  onInsert,
  isFavorite,
  onToggleFavorite,
  emptyMessage = "결과가 없습니다.",
}: Props) {
  if (assets.length === 0) {
    return <div className="empty">{emptyMessage}</div>;
  }

  return (
    <div className="grid">
      {assets.map((a) => {
        const fav = isFavorite(a.id);
        const label = a.name || a.tags?.[0] || a.id;
        return (
          <div key={a.id} className="card">
            <button
              className="card__btn"
              title={`${label} — 클릭하면 슬라이드에 삽입`}
              disabled={insertingId === a.id}
              onClick={() => onInsert(a)}
            >
              {a.image_url ? (
                <div className="card__thumb">
                  <img src={a.image_url} alt={label} loading="lazy" decoding="async" />
                </div>
              ) : (
                <div
                  className="card__thumb"
                  // 구 mock: SVG 문자열 렌더 (신뢰된 내부 자산만)
                  dangerouslySetInnerHTML={{ __html: a.svg || "" }}
                />
              )}
              <div className="card__name">
                {insertingId === a.id ? "삽입 중…" : label}
              </div>
            </button>
            <button
              className={"card__fav" + (fav ? " card__fav--on" : "")}
              title={fav ? "즐겨찾기 해제" : "즐겨찾기 추가"}
              aria-pressed={fav}
              onClick={() => onToggleFavorite(a.id)}
            >
              ★
            </button>
          </div>
        );
      })}
    </div>
  );
}

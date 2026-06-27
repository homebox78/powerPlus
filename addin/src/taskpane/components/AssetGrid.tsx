import * as React from "react";
import type { Asset } from "../data/mockAssets";

interface Props {
  assets: Asset[];
  insertingId: string | null;
  onInsert: (asset: Asset) => void;
  isFavorite: (id: string) => boolean;
  onToggleFavorite: (id: string) => void;
  emptyMessage?: string;
  loading?: boolean;
}

export default function AssetGrid({
  assets,
  insertingId,
  onInsert,
  isFavorite,
  onToggleFavorite,
  emptyMessage = "결과가 없습니다.",
  loading = false,
}: Props) {
  // 첫 로딩(표시할 게 아직 없음) → 스켈레톤
  if (loading && assets.length === 0) {
    return (
      <div className="grid" aria-busy="true" aria-label="불러오는 중">
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} className="card card--skeleton">
            <div className="skel skel--thumb" />
            <div className="skel skel--text" />
          </div>
        ))}
      </div>
    );
  }

  if (assets.length === 0) {
    return (
      <div className="empty">
        <div className="empty__icon" aria-hidden>🔍</div>
        <div>{emptyMessage}</div>
      </div>
    );
  }

  return (
    <div className="grid">
      {assets.map((a) => {
        const fav = isFavorite(a.id);
        const label = a.name || a.tags?.[0] || a.id;
        const inserting = insertingId === a.id;
        return (
          <div key={a.id} className="card">
            <button
              className="card__btn"
              title={`${label} — 클릭하면 슬라이드에 삽입`}
              disabled={inserting}
              onClick={() => onInsert(a)}
            >
              <div className="card__thumb">
                {a.image_url ? (
                  <img src={a.image_url} alt={label} loading="lazy" decoding="async" />
                ) : (
                  // 구 mock: SVG 문자열 렌더 (신뢰된 내부 자산만)
                  <span
                    className="card__svg"
                    dangerouslySetInnerHTML={{ __html: a.svg || "" }}
                  />
                )}
                {inserting && (
                  <span className="card__inserting" aria-hidden>
                    <span className="spinner" />
                  </span>
                )}
              </div>
              {a.name ? <div className="card__name">{a.name}</div> : null}
            </button>
            <button
              className={"card__fav" + (fav ? " card__fav--on" : "")}
              title={fav ? "즐겨찾기 해제" : "즐겨찾기 추가"}
              aria-pressed={fav}
              aria-label={fav ? "즐겨찾기 해제" : "즐겨찾기 추가"}
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

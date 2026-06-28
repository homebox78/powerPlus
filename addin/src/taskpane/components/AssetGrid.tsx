import * as React from "react";
import type { Asset } from "../data/mockAssets";

interface Props {
  assets: Asset[];
  insertingId: string | null;
  onInsert: (asset: Asset) => void;
  isFavorite: (id: string) => boolean;
  onToggleFavorite: (id: string) => void;
  emptyTitle?: string;
  emptySub?: string;
  loading?: boolean;
}

// 카테고리별 썸네일 배경 틴트 (디자인 시스템)
const TINTS: Record<string, string> = {
  icon: "#fbeee4",
  photo: "#edf0f4",
  illust: "#fdebee",
  diagram: "#f0ebfb",
  ppt: "#fef4e2",
};
const tintOf = (cat: string) => TINTS[cat] || "#f4f6f9";

const StarIcon = ({ on }: { on: boolean }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill={on ? "#f0566a" : "none"} stroke={on ? "#f0566a" : "#aeb7c4"} strokeWidth={on ? 1.2 : 1.5}>
    <path
      d="M12 3.5l2.5 5.6 6.1.6-4.6 4.1 1.3 6L12 16.9 6.2 19.8l1.3-6-4.6-4.1 6.1-.6z"
      strokeLinejoin="round"
    />
  </svg>
);

export default function AssetGrid({
  assets,
  insertingId,
  onInsert,
  isFavorite,
  onToggleFavorite,
  emptyTitle = "자료가 없어요",
  emptySub = "다른 카테고리를 선택해 보세요.",
  loading = false,
}: Props) {
  // 첫 로딩 → 스켈레톤
  if (loading && assets.length === 0) {
    return (
      <div className="grid" aria-busy="true" aria-label="불러오는 중">
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} className="card card--skeleton">
            <div className="skel skel--thumb" />
          </div>
        ))}
      </div>
    );
  }

  if (assets.length === 0) {
    return (
      <div className="empty">
        <div className="empty__icon" aria-hidden>
          ⭐
        </div>
        <div className="empty__title">{emptyTitle}</div>
        <div className="empty__sub">{emptySub}</div>
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
              <div className="card__thumb" style={{ background: tintOf(a.category) }}>
                {a.image_url || a.thumb_url ? (
                  // 목록은 썸네일(빠른 로딩), 삽입은 원본(useInsert가 image_url 사용)
                  <img src={a.thumb_url || a.image_url} alt={label} loading="lazy" decoding="async" />
                ) : (
                  <span className="card__svg" dangerouslySetInnerHTML={{ __html: a.svg || "" }} />
                )}
                {inserting && (
                  <span className="card__inserting" aria-hidden>
                    <span className="spinner" />
                  </span>
                )}
              </div>
            </button>
            <button
              className={"card__fav" + (fav ? " card__fav--on" : "")}
              title={fav ? "즐겨찾기 해제" : "즐겨찾기 추가"}
              aria-pressed={fav}
              aria-label={fav ? "즐겨찾기 해제" : "즐겨찾기 추가"}
              onClick={() => onToggleFavorite(a.id)}
            >
              <StarIcon on={fav} />
            </button>
          </div>
        );
      })}
    </div>
  );
}

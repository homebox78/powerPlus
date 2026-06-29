import * as React from "react";
import type { Asset } from "../data/mockAssets";

interface Props {
  assets: Asset[];
  insertingId: string | null;
  onInsert: (asset: Asset) => void;
  isFavorite: (id: string) => boolean;
  onToggleFavorite: (id: string) => void;
  /** 전달 시 카드에 "유사" 버튼 노출 → 비슷한 자산 추천 */
  onShowSimilar?: (asset: Asset) => void;
  emptyTitle?: string;
  emptySub?: string;
  loading?: boolean;
  /** 한 줄에 몇 개(아이콘/일러스트=3, 그 외=2) */
  cols?: number;
}

// 카드 썸네일 배경: 약간의 미색 — 흰색 로고도 묻히지 않고 보이도록 (사용자 요청)
const CARD_BG = "#f3f2ee";

// 장표(ppt) 유형 배지 라벨
const PPT_PAGE_LABEL: Record<string, string> = {
  cover: "표지", toc: "목차", divider: "간지", content: "콘텐츠",
  greeting: "인사말", qa: "Q&A", etc: "기타",
};
function pptBadge(a: Asset): string | null {
  if (a.slide_kind === "package") return "패키지";
  if (a.slide_kind === "single" && a.slide_page) return PPT_PAGE_LABEL[a.slide_page] || "기타";
  return null;
}

// 즐겨찾기 = 북마크(스크랩) 아이콘
const StarIcon = ({ on }: { on: boolean }) => (
  <svg width="14" height="15" viewBox="0 0 24 24" fill={on ? "#f0566a" : "none"} stroke={on ? "#f0566a" : "#aeb7c4"} strokeWidth={on ? 1.2 : 1.6}>
    <path
      d="M18 21l-6-4.2L6 21V5.2A2.2 2.2 0 0 1 8.2 3h7.6A2.2 2.2 0 0 1 18 5.2z"
      strokeLinejoin="round"
      strokeLinecap="round"
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
  cols = 2,
}: Props) {
  const gridStyle = { gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` } as React.CSSProperties;
  // 첫 로딩 → 스켈레톤
  if (loading && assets.length === 0) {
    return (
      <div className="grid" style={gridStyle} aria-busy="true" aria-label="불러오는 중">
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
        <img src="assets/state-empty.png" alt="" style={{ width: 150, height: "auto", marginBottom: 6 }} />
        <div className="empty__title">{emptyTitle}</div>
        <div className="empty__sub" style={{ whiteSpace: "pre-line" }}>{emptySub}</div>
      </div>
    );
  }

  return (
    <div className="grid" style={gridStyle}>
      {assets.map((a) => {
        const fav = isFavorite(a.id);
        const label = a.name || a.tags?.[0] || a.id;
        const inserting = insertingId === a.id;
        return (
          <div key={a.id} className="card">
            <button
              className="card__btn"
              title={a.tags?.length ? a.tags.slice(0, 4).join(" · ") : label}
              disabled={inserting}
              onClick={() => onInsert(a)}
            >
              <div className="card__thumb" style={{ background: CARD_BG }}>
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
                {/* 호버 시 등록된 태그 미리보기(이미지만으론 모를 때) */}
                {a.tags?.length ? (
                  <span className="card__tags" aria-hidden>
                    {a.tags.slice(0, 4).map((t, i) => (
                      <span key={i} className="card__tag">
                        {t}
                      </span>
                    ))}
                  </span>
                ) : null}
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
            {(() => {
              const badge = pptBadge(a);
              if (!badge) return null;
              const isPkg = a.slide_kind === "package";
              return (
                <span
                  className="card__type"
                  style={{
                    position: "absolute",
                    left: 6,
                    top: 6,
                    padding: "2px 8px",
                    borderRadius: 6,
                    fontSize: 11,
                    fontWeight: 700,
                    lineHeight: "16px",
                    color: "#fff",
                    background: isPkg ? "#E0701F" : "#3A6EA5",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.18)",
                    pointerEvents: "none",
                  }}
                >
                  {badge}
                </span>
              );
            })()}
          </div>
        );
      })}
    </div>
  );
}

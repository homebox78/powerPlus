import * as React from "react";
import CategoryTabs from "./components/CategoryTabs";
import SearchBar from "./components/SearchBar";
import AssetGrid from "./components/AssetGrid";
import Login from "./components/Login";
import { CATEGORIES } from "./data/mockAssets";
import type { Asset, Category } from "./data/mockAssets";
import { fetchAssets, AuthRequiredError } from "./api/assets";
import { getToken, getEmail, clearSession, logout } from "./api/auth";
import { recordUsage } from "./api/usage";
import { fetchCategories } from "./api/categories";
import { useInsert } from "./hooks/useInsert";
import { useFavorites } from "./hooks/useFavorites";
import { useRecent } from "./hooks/useRecent";
import { fetchAnnouncements, getAnnSeen, setAnnSeen } from "./api/announcements";
import type { Announcement } from "./api/announcements";

// 정렬 옵션
const SORTS = [
  { key: "latest", label: "기본" },
  { key: "popular", label: "인기순" },
  { key: "favorites", label: "즐겨찾기순" },
];

// 특수 탭(즐겨찾기/최근) — 클라이언트에서 필터링.
const SPECIAL_TABS: Category[] = [
  { key: "favorites", label: "⭐ 즐겨찾기" },
  { key: "recent", label: "🕒 최근" },
];

export default function App() {
  // 토큰이 있으면 로그인 상태로 시작 (만료 시 첫 fetch 의 401 로 로그아웃 처리).
  const [email, setUserEmail] = React.useState<string | null>(() =>
    getToken() ? getEmail() : null
  );

  const [category, setCategory] = React.useState("all");
  const [query, setQuery] = React.useState("");
  const [sort, setSort] = React.useState("latest");
  const [cats, setCats] = React.useState<Category[]>(CATEGORIES); // 폴백: 하드코딩

  // 전체 컨텐츠 수(필터 무관) — 로그인 시 1회 조회
  const [grandTotal, setGrandTotal] = React.useState<number | null>(null);

  // 공지(알람)
  const [announcements, setAnnouncements] = React.useState<Announcement[]>([]);
  const [annSeen, setAnnSeenState] = React.useState<number>(() => getAnnSeen());
  const [annOpen, setAnnOpen] = React.useState(false);
  const [annExpanded, setAnnExpanded] = React.useState<number | null>(null); // 펼친 공지 id
  const unreadAnn = announcements.filter((a) => a.id > annSeen).length;

  // 로그인 후 서버에서 카테고리 목록 로드 (실패 시 폴백 유지)
  React.useEffect(() => {
    if (!email) return;
    fetchCategories()
      .then((list) => setCats([{ key: "all", label: "전체" }, ...list]))
      .catch(() => {
        /* 서버 미연결 → 하드코딩 카테고리 유지 */
      });
  }, [email]);

  // 로그인 후 전체 컨텐츠 수 + 공지 로드
  React.useEffect(() => {
    if (!email) return;
    fetchAssets("all", "", 1, 1)
      .then((r) => setGrandTotal(r.total))
      .catch(() => undefined);
    fetchAnnouncements()
      .then(setAnnouncements)
      .catch(() => undefined);
  }, [email]);

  const [rawAssets, setRawAssets] = React.useState<Asset[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [offline, setOffline] = React.useState(false);

  const { insertingId, message, error, insert, clearMessage } = useInsert();
  const { favorites, toggleFavorite, isFavorite } = useFavorites(email);
  const { recent, pushRecent } = useRecent(email);

  const [total, setTotal] = React.useState(0);
  const [loadingMore, setLoadingMore] = React.useState(false);
  const pageRef = React.useRef(1);

  const PAGE_SIZE = 60;
  // 특수 탭(즐겨찾기/최근)은 클라이언트 필터라 전체를 한 번에, 일반 탭은 페이지 단위.
  const isSpecial = category === "favorites" || category === "recent";
  const serverCategory = isSpecial ? "all" : category;

  // 카테고리/검색어 변경 → 1페이지부터 새로 로드 (이전 요청 취소).
  React.useEffect(() => {
    if (!email) return; // 로그인 전에는 조회하지 않음
    const ctrl = new AbortController();
    pageRef.current = 1;
    setLoading(true);
    fetchAssets(serverCategory, query, 1, isSpecial ? 500 : PAGE_SIZE, ctrl.signal, sort)
      .then((r) => {
        setRawAssets(r.assets);
        setTotal(r.total);
        setOffline(r.offline);
      })
      .catch((e) => {
        // 세션 만료 → 로그인 화면으로
        if (e instanceof AuthRequiredError) {
          clearSession();
          setUserEmail(null);
        }
        // 그 외(취소 등)는 무시
      })
      .finally(() => {
        if (!ctrl.signal.aborted) setLoading(false);
      });
    return () => ctrl.abort();
  }, [category, query, email, sort]);

  // 다음 페이지 추가 로드 (일반 탭에서만)
  async function loadMore() {
    setLoadingMore(true);
    try {
      pageRef.current += 1;
      const r = await fetchAssets(serverCategory, query, pageRef.current, PAGE_SIZE, undefined, sort);
      setRawAssets((prev) => [...prev, ...r.assets]);
      setTotal(r.total);
    } catch (e) {
      if (e instanceof AuthRequiredError) {
        clearSession();
        setUserEmail(null);
      }
    } finally {
      setLoadingMore(false);
    }
  }

  const hasMore = !isSpecial && rawAssets.length < total;

  // 무한 스크롤: 하단 센티넬이 보이면 다음 페이지 자동 로드
  const bodyRef = React.useRef<HTMLElement>(null);
  const sentinelRef = React.useRef<HTMLDivElement>(null);
  React.useEffect(() => {
    const sentinel = sentinelRef.current;
    const root = bodyRef.current;
    if (!sentinel || !root || !hasMore) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loadingMore) loadMore();
      },
      { root, rootMargin: "300px" }
    );
    io.observe(sentinel);
    return () => io.disconnect();
  }, [hasMore, loadingMore, serverCategory, query, sort]);

  // 표시할 자산: 특수 탭이면 즐겨찾기/최근으로 필터·정렬.
  const displayed = React.useMemo(() => {
    if (category === "favorites") {
      return rawAssets.filter((a) => favorites.has(a.id));
    }
    if (category === "recent") {
      const order = new Map(recent.map((id, i) => [id, i] as const));
      return rawAssets
        .filter((a) => order.has(a.id))
        .sort((a, b) => (order.get(a.id) ?? 0) - (order.get(b.id) ?? 0));
    }
    return rawAssets;
  }, [rawAssets, category, favorites, recent]);

  async function handleInsert(asset: Asset) {
    const ok = await insert(asset);
    if (ok) {
      pushRecent(asset.id); // 실제 삽입 성공 시에만 최근 기록
      recordUsage(asset.id); // 사용 통계 기록 (실패해도 무시)
    }
  }

  async function handleLogout() {
    await logout();
    setUserEmail(null);
    setRawAssets([]);
  }

  // 공지 패널 열기 → 모두 읽음 처리(벨 숨김)
  function openAnnouncements() {
    setAnnOpen(true);
    const maxId = announcements.reduce((m, a) => Math.max(m, a.id), 0);
    if (maxId > annSeen) {
      setAnnSeen(maxId);
      setAnnSeenState(maxId);
    }
  }

  // 토스트 메시지 자동 사라짐
  React.useEffect(() => {
    if (!message) return;
    const t = window.setTimeout(clearMessage, 3000);
    return () => window.clearTimeout(t);
  }, [message, clearMessage]);

  if (!email) {
    return <Login onSuccess={setUserEmail} />;
  }

  const emptyMessage =
    category === "favorites"
      ? "즐겨찾기한 자산이 없습니다. 카드의 ★를 눌러 추가하세요."
      : category === "recent"
        ? "최근 사용한 자산이 없습니다. 자산을 삽입하면 여기에 모입니다."
        : "결과가 없습니다.";

  // 카운트: 검색된 수(total) + 전체 컨텐츠 수(grandTotal)
  const filtered = category !== "all" || query.trim() !== "";
  const gt = grandTotal ?? total;
  const countText = isSpecial
    ? `${displayed.length}개`
    : filtered
      ? `검색 ${total}개 · 전체 ${gt}개`
      : `전체 ${gt}개`;

  return (
    <div className="app">
      <header className="app__header app__header--row">
        <div className="brand">
          <span className="brand__mark" aria-hidden>
            <svg viewBox="0 0 24 24" width="15" height="15" fill="#fff">
              <rect x="3" y="3" width="7" height="7" rx="1.6" />
              <rect x="14" y="3" width="7" height="7" rx="1.6" />
              <rect x="3" y="14" width="7" height="7" rx="1.6" />
              <rect x="14" y="14" width="7" height="7" rx="1.6" />
            </svg>
          </span>
          <h1 className="app__title">powerPlus</h1>
        </div>
        <div className="app__actions">
          {unreadAnn > 0 && (
            <button
              className="bell"
              onClick={openAnnouncements}
              aria-label={`새 공지 ${unreadAnn}건`}
              title={`새 공지 ${unreadAnn}건`}
            >
              🔔<span className="bell__badge">{unreadAnn}</span>
            </button>
          )}
          <button className="app__logout" onClick={handleLogout} title={email}>
            로그아웃
          </button>
        </div>
      </header>

      <CategoryTabs categories={SPECIAL_TABS} active={category} onChange={setCategory} />

      <div className="app__count">
        <span className="app__count-text">
          {loading ? "불러오는 중…" : countText}
          {offline && !loading && " · 오프라인"}
        </span>
        {!isSpecial && (
          <select
            className="app__sort"
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            aria-label="정렬"
          >
            {SORTS.map((s) => (
              <option key={s.key} value={s.key}>
                {s.label}
              </option>
            ))}
          </select>
        )}
      </div>

      <main className="app__body" ref={bodyRef}>
        <AssetGrid
          assets={displayed}
          insertingId={insertingId}
          onInsert={handleInsert}
          isFavorite={isFavorite}
          onToggleFavorite={toggleFavorite}
          emptyMessage={emptyMessage}
          loading={loading}
        />
        {/* 무한 스크롤 센티넬 + 추가 로딩 표시 */}
        <div ref={sentinelRef} className="scroll-sentinel" aria-hidden />
        {loadingMore && (
          <div className="loadmore-spin" aria-label="더 불러오는 중">
            <span className="spinner" />
          </div>
        )}
      </main>

      {/* 하단 고정 검색 (채팅 입력창 스타일) */}
      <SearchBar
        value={query}
        onChange={setQuery}
        categories={cats}
        category={category}
        onCategoryChange={setCategory}
      />

      {message && (
        <div className={"toast" + (error ? " toast--error" : "")} role="status">
          {message}
        </div>
      )}

      {annOpen && (
        <div className="ann-overlay" onClick={() => setAnnOpen(false)}>
          <div className="ann-panel" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="공지">
            <div className="ann-panel__head">
              <span>📢 공지</span>
              <button className="ann-panel__close" onClick={() => setAnnOpen(false)} aria-label="닫기">
                ×
              </button>
            </div>
            <div className="ann-panel__body">
              {announcements.length === 0 ? (
                <div className="ann-empty">등록된 공지가 없습니다.</div>
              ) : (
                announcements.map((a) => {
                  const open = annExpanded === a.id;
                  return (
                    <div className={"ann-item" + (open ? " ann-item--open" : "")} key={a.id}>
                      <button
                        className="ann-item__title"
                        onClick={() => setAnnExpanded(open ? null : a.id)}
                        aria-expanded={open}
                      >
                        <span className="ann-item__title-text">{a.title}</span>
                        <span className="ann-item__chev" aria-hidden>
                          {open ? "▴" : "▾"}
                        </span>
                      </button>
                      {open && (
                        <div className="ann-item__detail">
                          {a.body && <div className="ann-item__body">{a.body}</div>}
                          <div className="ann-item__date">{a.created_at?.slice(0, 10)}</div>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

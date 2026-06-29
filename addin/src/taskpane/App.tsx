import * as React from "react";
import AssetGrid from "./components/AssetGrid";
import Login from "./components/Login";
import { CATEGORIES } from "./data/mockAssets";
import type { Asset, Category } from "./data/mockAssets";
import { fetchAssets, fetchSimilar, AuthRequiredError } from "./api/assets";
import { getToken, getEmail, clearSession, logout } from "./api/auth";
import { recordUsage } from "./api/usage";
import { fetchCategories } from "./api/categories";
import { useInsert } from "./hooks/useInsert";
import { useFavorites } from "./hooks/useFavorites";
import { useRecent } from "./hooks/useRecent";
import { fetchAnnouncements, getAnnSeen, setAnnSeen } from "./api/announcements";
import type { Announcement } from "./api/announcements";
import { submitRequest } from "./api/requests";

const SORTS = [
  { key: "popular", label: "인기순" },
  { key: "latest", label: "최신순" },
  { key: "favorites", label: "즐겨찾기순" },
];
const sortLabel = (k: string) => SORTS.find((s) => s.key === k)?.label || "인기순";

const VIEWS = [
  { key: "all", label: "추천" },
  { key: "favorites", label: "즐겨찾기" },
  { key: "recent", label: "최근" },
];

const REQ_TYPES = ["아이콘", "사진", "일러스트", "다이어그램", "장표"];

// ---- 인라인 아이콘 ----
const Ic = {
  bell: (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#5a6573" strokeWidth="1.7">
      <path d="M18 8a6 6 0 10-12 0c0 7-3 9-3 9h18s-3-2-3-9" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M13.7 21a2 2 0 01-3.4 0" strokeLinecap="round" />
    </svg>
  ),
  send: (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2">
      <path d="M12 19V6M6 12l6-6 6 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  chev: (
    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4">
      <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  check: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4">
      <path d="M5 12l5 5L20 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  logo: (
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <rect x="8.5" y="3.5" width="12" height="12" rx="2.5" opacity=".5" />
      <rect x="3.5" y="8.5" width="12" height="12" rx="2.5" />
      <path d="M9.5 12.6v3.8M7.6 14.5h3.8" />
    </svg>
  ),
  request: (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 4h10l4 4v12H5z" />
      <path d="M12 11v5M9.5 13.5h5" />
    </svg>
  ),
  logout: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M15 4h3a1 1 0 011 1v14a1 1 0 01-1 1h-3" strokeLinecap="round" />
      <path d="M10 8l-4 4 4 4M6 12h10" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  close: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#5a6573" strokeWidth="2" strokeLinecap="round">
      <path d="M6 6l12 12M18 6L6 18" />
    </svg>
  ),
};

export default function App() {
  const [email, setUserEmail] = React.useState<string | null>(() =>
    getToken() ? getEmail() : null
  );

  const [view, setView] = React.useState<string>("all"); // 추천/즐겨찾기/최근
  const [cat, setCat] = React.useState("all"); // 컴포저 카테고리 pill
  const [query, setQuery] = React.useState(""); // 컴포저 입력값
  const [activeQuery, setActiveQuery] = React.useState(""); // 전송된 검색어
  const [sort, setSort] = React.useState("popular");
  const [cats, setCats] = React.useState<Category[]>(CATEGORIES);
  const [grandTotal, setGrandTotal] = React.useState<number | null>(null);

  // 메뉴 상태
  const [notifOpen, setNotifOpen] = React.useState(false);
  const [profileOpen, setProfileOpen] = React.useState(false);
  const [catOpen, setCatOpen] = React.useState(false);
  const [sortOpen, setSortOpen] = React.useState(false);
  const closeMenus = () => {
    setNotifOpen(false);
    setProfileOpen(false);
    setCatOpen(false);
    setSortOpen(false);
  };

  // 공지(알림)
  const [announcements, setAnnouncements] = React.useState<Announcement[]>([]);
  const [annSeen, setAnnSeenState] = React.useState<number>(() => getAnnSeen());
  const [annExpanded, setAnnExpanded] = React.useState<number | null>(null); // 알림 아코디언
  const unreadAnn = announcements.filter((a) => a.id > annSeen).length;

  // 콘텐츠 요청 시트
  const [requestOpen, setRequestOpen] = React.useState(false);
  const [reqType, setReqType] = React.useState("아이콘");
  const [reqTitle, setReqTitle] = React.useState("");
  const [reqDesc, setReqDesc] = React.useState("");
  const [reqLink, setReqLink] = React.useState("");
  const [reqSubmitted, setReqSubmitted] = React.useState(false);

  const [rawAssets, setRawAssets] = React.useState<Asset[]>([]);
  // 유사 자산 추천 모드
  const [similarOf, setSimilarOf] = React.useState<Asset | null>(null);
  const [similarList, setSimilarList] = React.useState<Asset[]>([]);
  const [similarLoading, setSimilarLoading] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [offline, setOffline] = React.useState(false);
  const [total, setTotal] = React.useState(0);
  const [loadingMore, setLoadingMore] = React.useState(false);
  const pageRef = React.useRef(1);

  const { insertingId, message, error, insert, clearMessage } = useInsert();
  const { favorites, toggleFavorite, isFavorite } = useFavorites(email);
  const { recent, pushRecent } = useRecent(email);

  const PAGE_SIZE = 60;
  const isSpecial = view === "favorites" || view === "recent";
  const serverCategory = isSpecial ? "all" : cat;

  // 카테고리 + 전체 수 + 공지 로드
  React.useEffect(() => {
    if (!email) return;
    fetchCategories()
      .then((list) => setCats([{ key: "all", label: "전체" }, ...list]))
      .catch(() => undefined);
    fetchAssets("all", "", 1, 1)
      .then((r) => setGrandTotal(r.total))
      .catch(() => undefined);
    fetchAnnouncements().then(setAnnouncements).catch(() => undefined);
  }, [email]);

  // 목록 로드 (뷰/카테고리/검색/정렬 변경 시 1페이지부터)
  React.useEffect(() => {
    if (!email) return;
    const ctrl = new AbortController();
    pageRef.current = 1;
    setLoading(true);
    fetchAssets(serverCategory, activeQuery, 1, isSpecial ? 500 : PAGE_SIZE, ctrl.signal, sort)
      .then((r) => {
        setRawAssets(r.assets);
        setTotal(r.total);
        setOffline(r.offline);
      })
      .catch((e) => {
        if (e instanceof AuthRequiredError) {
          clearSession();
          setUserEmail(null);
        }
      })
      .finally(() => {
        if (!ctrl.signal.aborted) setLoading(false);
      });
    return () => ctrl.abort();
  }, [view, cat, activeQuery, email, sort]);

  async function loadMore() {
    setLoadingMore(true);
    try {
      pageRef.current += 1;
      const r = await fetchAssets(serverCategory, activeQuery, pageRef.current, PAGE_SIZE, undefined, sort);
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

  const bodyRef = React.useRef<HTMLDivElement>(null);
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
  }, [hasMore, loadingMore, serverCategory, activeQuery, sort]);

  const displayed = React.useMemo(() => {
    if (view === "favorites") return rawAssets.filter((a) => favorites.has(a.id));
    if (view === "recent") {
      const order = new Map(recent.map((id, i) => [id, i] as const));
      return rawAssets.filter((a) => order.has(a.id)).sort((a, b) => (order.get(a.id) ?? 0) - (order.get(b.id) ?? 0));
    }
    return rawAssets;
  }, [rawAssets, view, favorites, recent]);

  async function handleInsert(asset: Asset) {
    const ok = await insert(asset);
    if (ok) {
      pushRecent(asset.id);
      recordUsage(asset.id);
    }
  }

  // 비슷한 자산 보기
  async function handleShowSimilar(asset: Asset) {
    setSimilarOf(asset);
    setSimilarLoading(true);
    try {
      setSimilarList(await fetchSimilar(asset.id, 24));
    } finally {
      setSimilarLoading(false);
    }
    if (bodyRef.current) bodyRef.current.scrollTop = 0;
  }
  function clearSimilar() {
    setSimilarOf(null);
    setSimilarList([]);
  }
  // 카테고리/검색/세그먼트가 바뀌면 유사 모드 해제
  React.useEffect(() => {
    setSimilarOf(null);
    setSimilarList([]);
  }, [cat, activeQuery, view]);

  async function handleLogout() {
    await logout();
    setUserEmail(null);
    setRawAssets([]);
    closeMenus();
  }

  function openNotif() {
    setNotifOpen((v) => !v);
    setProfileOpen(false);
  }
  // "모두 읽음" — 미확인 표시(코랄 점/벨 배지) 해제
  function markAllNotifRead() {
    const maxId = announcements.reduce((m, a) => Math.max(m, a.id), 0);
    if (maxId > annSeen) {
      setAnnSeen(maxId);
      setAnnSeenState(maxId);
    }
  }

  function send() {
    setActiveQuery(query.trim());
    setView("all");
    closeMenus();
  }
  function clearQuery() {
    setQuery("");
    setActiveQuery("");
  }

  function openRequest() {
    setRequestOpen(true);
    setReqSubmitted(false);
    closeMenus();
  }
  function closeRequest() {
    setRequestOpen(false);
    setReqSubmitted(false);
    setReqType("아이콘");
    setReqTitle("");
    setReqDesc("");
    setReqLink("");
  }
  async function doSubmitRequest() {
    if (!reqTitle.trim()) return;
    await submitRequest({ type: reqType, title: reqTitle.trim(), description: reqDesc, link: reqLink });
    setReqSubmitted(true); // 서버 실패해도 UX상 접수 안내(요청은 best-effort)
  }

  // 토스트 자동 사라짐
  React.useEffect(() => {
    if (!message) return;
    const t = window.setTimeout(clearMessage, 2600);
    return () => window.clearTimeout(t);
  }, [message, clearMessage]);

  if (!email) {
    return <Login onSuccess={setUserEmail} />;
  }

  const local = email.split("@")[0] || email;
  const avatarChar = local.charAt(0).toUpperCase();
  const gt = grandTotal ?? total;
  const count = isSpecial ? displayed.length : total;
  const catLabel = cats.find((c) => c.key === cat)?.label || "전체";

  const emptyTitle = activeQuery
    ? "검색 결과가 없어요"
    : view === "favorites"
      ? "즐겨찾기가 비어 있어요"
      : view === "recent"
        ? "최근 본 자료가 없어요"
        : "자료가 없어요";
  const emptySub = activeQuery
    ? `‘${activeQuery}’와 일치하는 자료를 찾지 못했어요. 다른 키워드로 검색해 보세요.`
    : view === "favorites"
      ? "카드의 별을 눌러 자주 쓰는 자료를 모아보세요."
      : view === "recent"
        ? "자료를 클릭해 슬라이드에 추가하면 여기에 쌓여요."
        : "다른 카테고리를 선택해 보세요.";

  const anyMenu = notifOpen || profileOpen;

  return (
    <div className="app">
      {/* 헤더 */}
      <header className="app__header--row">
        <div className="brand">
          <span className="brand__mark" aria-hidden>
            {Ic.logo}
          </span>
          <span className="brand__text">
            <span className="app__title">powerPlus</span>
            <span className="brand__sub">에셋 라이브러리</span>
          </span>
        </div>
        <div className="app__actions">
          <button className="bell" onClick={openNotif} aria-label="알림" title="알림">
            {Ic.bell}
            {unreadAnn > 0 && <span className="bell__badge">{unreadAnn}</span>}
          </button>
          <button
            className="avatar"
            onClick={() => {
              setProfileOpen((v) => !v);
              setNotifOpen(false);
            }}
            aria-label="내 계정"
            title={email}
          >
            {avatarChar}
          </button>
        </div>
      </header>

      {/* 알림 / 프로필 드롭다운 */}
      {anyMenu && <div className="menu-scrim" onClick={closeMenus} />}
      {notifOpen && (
        <div className="dropdown notif" role="dialog" aria-label="알림">
          <div className="notif__head">
            <span className="notif__title">알림</span>
            {unreadAnn > 0 && (
              <button className="notif__readall" onClick={markAllNotifRead}>모두 읽음</button>
            )}
          </div>
          <div className="notif__list">
            {announcements.length === 0 ? (
              <div className="notif__empty">새 알림이 없습니다.</div>
            ) : (
              announcements.slice(0, 2).map((a) => {
                const open = annExpanded === a.id;
                const unread = a.id > annSeen;
                return (
                  <div key={a.id} className={"notif__item" + (open ? " notif__item--open" : "")}>
                    <button
                      className="notif__row"
                      onClick={() => setAnnExpanded(open ? null : a.id)}
                      aria-expanded={open}
                    >
                      <span className="notif__item-title">{a.title}</span>
                      {unread && <span className="notif__dot" aria-hidden />}
                      <svg
                        className={"notif__chev" + (open ? " notif__chev--open" : "")}
                        width="13" height="13" viewBox="0 0 24 24" fill="none"
                        stroke="#aeb7c4" strokeWidth="2.4" aria-hidden
                      >
                        <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </button>
                    {open && a.body && <div className="notif__item-text">{a.body}</div>}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
      {profileOpen && (
        <div className="dropdown profile" role="dialog" aria-label="내 계정">
          <div className="profile__head">
            <span className="profile__av" aria-hidden>
              {avatarChar}
            </span>
            <span style={{ minWidth: 0 }}>
              <span className="profile__email">{email}</span>
            </span>
          </div>
          <div className="profile__divider" />
          <div className="profile__section">
            <button className="profile__item" onClick={openRequest}>
              <span className="profile__item-ic" aria-hidden>
                {Ic.request}
              </span>
              <span style={{ minWidth: 0 }}>
                <span className="profile__item-title">콘텐츠 요청하기</span>
                <span className="profile__item-sub">원하는 자료를 관리자에게 요청</span>
              </span>
            </button>
          </div>
          <div className="profile__divider" />
          <div className="profile__section">
            <button className="profile__logout" onClick={handleLogout}>
              로그아웃
              <span className="profile__logout-ic" aria-hidden>
                {Ic.logout}
              </span>
            </button>
          </div>
        </div>
      )}

      {/* 홈 (인사말/검색바 + 세그먼트 + 카운트/정렬) */}
      <div className="home">
        {similarOf ? (
          <div className="querybar">
            <span className="querybar__text">
              ‘<b>{similarOf.name || similarOf.tags?.[0] || similarOf.id}</b>’와 비슷한 자산 {similarList.length}개
            </span>
            <button className="querybar__clear" onClick={clearSimilar}>
              닫기
            </button>
          </div>
        ) : activeQuery ? (
          <div className="querybar">
            <span className="querybar__text">
              ‘<b>{activeQuery}</b>’ 검색 결과 {count}개
            </span>
            <button className="querybar__clear" onClick={clearQuery}>
              전체 보기
            </button>
          </div>
        ) : (
          <div className="greeting">
            무엇을 찾아드릴까요? <span style={{ fontSize: 16 }}>👋</span>
          </div>
        )}

        <div className="segmented">
          {VIEWS.map((v) => (
            <button
              key={v.key}
              className={"seg" + (view === v.key ? " seg--active" : "")}
              onClick={() => {
                setView(v.key);
                closeMenus();
              }}
            >
              {v.label}
            </button>
          ))}
        </div>

        <div className="countrow">
          <span className="countrow__count">
            {loading ? "불러오는 중…" : count}개 <span>· 전체 {gt}</span>
            {offline && !loading && <span> · 오프라인</span>}
          </span>
          {!isSpecial && (
            <button
              className="sortbtn"
              onClick={() => {
                setSortOpen((v) => !v);
                setCatOpen(false);
              }}
            >
              {sortLabel(sort)}
              {Ic.chev}
            </button>
          )}
          {sortOpen && (
            <>
              <div className="menu-scrim" onClick={closeMenus} />
              <div className="sortmenu">
                {SORTS.map((s) => (
                  <button
                    key={s.key}
                    className={"menu-item" + (sort === s.key ? " menu-item--active" : "")}
                    onClick={() => {
                      setSort(s.key);
                      closeMenus();
                    }}
                  >
                    {s.label}
                    {sort === s.key && Ic.check}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* 그리드 */}
      <div className="app__body" ref={bodyRef}>
        <AssetGrid
          assets={similarOf ? similarList : displayed}
          insertingId={insertingId}
          onInsert={handleInsert}
          isFavorite={isFavorite}
          onToggleFavorite={toggleFavorite}
          onShowSimilar={handleShowSimilar}
          emptyTitle={similarOf ? "비슷한 자산이 없어요" : emptyTitle}
          emptySub={similarOf ? "다른 자산에서 다시 시도해 보세요." : emptySub}
          loading={similarOf ? similarLoading : loading}
        />
        <div ref={sentinelRef} className="scroll-sentinel" aria-hidden />
        {loadingMore && (
          <div className="loadmore-spin" aria-label="더 불러오는 중">
            <span className="spinner" />
          </div>
        )}
      </div>

      {/* 하단 컴포저 (검색) */}
      <div className="composer">
        {catOpen && (
          <>
            <div className="menu-scrim" onClick={closeMenus} />
            <div className="catmenu">
              {cats.map((c) => (
                <button
                  key={c.key}
                  className={"menu-item" + (cat === c.key ? " menu-item--active" : "")}
                  onClick={() => {
                    setCat(c.key);
                    setView("all");
                    closeMenus();
                  }}
                >
                  {c.label}
                  {cat === c.key && Ic.check}
                </button>
              ))}
            </div>
          </>
        )}
        <div className="composer__box">
          <input
            className="composer__input"
            type="search"
            value={query}
            placeholder="필요한 자료를 설명해 보세요…"
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                send();
              }
            }}
            aria-label="자산 검색"
          />
          <div className="composer__actions">
            <button
              className="composer__cat"
              onClick={() => {
                setCatOpen((v) => !v);
                setSortOpen(false);
              }}
            >
              {catLabel}
              {Ic.chev}
            </button>
            <button className="composer__send" onClick={send} aria-label="검색">
              {Ic.send}
            </button>
          </div>
        </div>
      </div>

      {/* 토스트 */}
      {message && (
        <div className={"toast" + (error ? " toast--error" : "")} role="status">
          <span className="toast__check" aria-hidden>
            {Ic.check}
          </span>
          {message}
        </div>
      )}

      {/* 콘텐츠 요청 시트 */}
      {requestOpen && (
        <div className="sheet-scrim" onClick={closeRequest}>
          <div className="sheet" onClick={(e) => e.stopPropagation()}>
            {!reqSubmitted ? (
              <>
                <div className="sheet__grip" />
                <div className="sheet__head">
                  <div>
                    <div className="sheet__title">콘텐츠 요청</div>
                    <div className="sheet__desc">
                      필요한 아이콘·자료를 요청하면
                      <br />
                      관리자가 검토 후 라이브러리에 추가해 드려요.
                    </div>
                  </div>
                  <button className="sheet__close" onClick={closeRequest} aria-label="닫기">
                    {Ic.close}
                  </button>
                </div>
                <div className="sheet__body">
                  <div className="sheet__flabel">유형</div>
                  <div className="sheet__types">
                    {REQ_TYPES.map((t) => (
                      <button
                        key={t}
                        className={"chip-btn" + (reqType === t ? " chip-btn--active" : "")}
                        onClick={() => setReqType(t)}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                  <div className="sheet__flabel">
                    제목 · 키워드 <span className="sheet__req">*</span>
                  </div>
                  <input
                    className="sheet__input"
                    value={reqTitle}
                    placeholder="예) 친환경·ESG 관련 3D 아이콘"
                    onChange={(e) => setReqTitle(e.target.value)}
                  />
                  <div className="sheet__flabel">상세 설명</div>
                  <textarea
                    className="sheet__textarea"
                    rows={3}
                    value={reqDesc}
                    placeholder="원하는 스타일, 색감, 용도 등을 적어주세요."
                    onChange={(e) => setReqDesc(e.target.value)}
                  />
                  <div className="sheet__flabel">참고 링크 (선택)</div>
                  <input
                    className="sheet__input"
                    value={reqLink}
                    placeholder="https://"
                    onChange={(e) => setReqLink(e.target.value)}
                  />
                </div>
                <div className="sheet__foot">
                  <button className="sheet__submit" disabled={!reqTitle.trim()} onClick={doSubmitRequest}>
                    요청 보내기
                  </button>
                </div>
              </>
            ) : (
              <div className="sheet__done">
                <div className="sheet__done-ic" aria-hidden>
                  ✓
                </div>
                <div className="sheet__done-title">요청이 접수되었습니다</div>
                <div className="sheet__done-sub">
                  관리자가 검토 후 라이브러리에 반영해 드려요.
                  <br />
                  결과는 알림으로 안내됩니다.
                </div>
                <button
                  className="sheet__submit"
                  style={{ marginTop: 20 }}
                  onClick={closeRequest}
                >
                  확인
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

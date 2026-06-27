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
import { useInsert } from "./hooks/useInsert";
import { useFavorites } from "./hooks/useFavorites";
import { useRecent } from "./hooks/useRecent";
import { INSERT_SIZES, useInsertSize } from "./hooks/useInsertSize";

// 일반 카테고리 + 특수 탭(즐겨찾기/최근). 특수 탭은 클라이언트에서 필터링한다.
const TABS: Category[] = [
  ...CATEGORIES,
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

  const [rawAssets, setRawAssets] = React.useState<Asset[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [offline, setOffline] = React.useState(false);

  const { insertingId, message, error, insert, clearMessage } = useInsert();
  const { favorites, toggleFavorite, isFavorite } = useFavorites();
  const { recent, pushRecent } = useRecent();
  const { sizeKey, setSize, sizePt } = useInsertSize();

  // 특수 탭(즐겨찾기/최근)은 서버엔 'all' 로 요청하고 클라이언트에서 거른다.
  const serverCategory =
    category === "favorites" || category === "recent" ? "all" : category;

  // 카테고리/검색어 변경 시 서버에서 자산을 가져온다 (이전 요청은 취소).
  React.useEffect(() => {
    if (!email) return; // 로그인 전에는 조회하지 않음
    const ctrl = new AbortController();
    setLoading(true);
    fetchAssets(serverCategory, query, ctrl.signal)
      .then((r) => {
        setRawAssets(r.assets);
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
  }, [serverCategory, query, email]);

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
    const ok = await insert(asset, sizePt);
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

  return (
    <div className="app">
      <header className="app__header app__header--row">
        <h1 className="app__title">powerPlus 자산 라이브러리</h1>
        <button className="app__logout" onClick={handleLogout} title={email}>
          로그아웃
        </button>
      </header>

      <SearchBar value={query} onChange={setQuery} />
      <CategoryTabs categories={TABS} active={category} onChange={setCategory} />

      <div className="toolbar">
        <div className="app__count">
          {loading ? "불러오는 중…" : `${displayed.length}개 자산`}
          {offline && !loading && " · 오프라인(로컬 데이터)"}
        </div>
        <div className="sizebar" role="group" aria-label="삽입 크기">
          <span className="sizebar__label">삽입 크기</span>
          {INSERT_SIZES.map((s) => (
            <button
              key={s.key}
              className={"sizebar__btn" + (sizeKey === s.key ? " sizebar__btn--on" : "")}
              aria-pressed={sizeKey === s.key}
              title={`${s.pt}pt`}
              onClick={() => setSize(s.key)}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <main className="app__body">
        <AssetGrid
          assets={displayed}
          insertingId={insertingId}
          onInsert={handleInsert}
          isFavorite={isFavorite}
          onToggleFavorite={toggleFavorite}
          emptyMessage={emptyMessage}
        />
      </main>

      {message && (
        <div className={"toast" + (error ? " toast--error" : "")} role="status">
          {message}
        </div>
      )}
    </div>
  );
}

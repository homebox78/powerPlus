import * as React from "react";
import CategoryTabs from "./components/CategoryTabs";
import SearchBar from "./components/SearchBar";
import AssetGrid from "./components/AssetGrid";
import Login from "./components/Login";
import { CATEGORIES } from "./data/mockAssets";
import type { Asset } from "./data/mockAssets";
import { fetchAssets, AuthRequiredError } from "./api/assets";
import { getToken, getEmail, clearSession, logout } from "./api/auth";
import { useInsert } from "./hooks/useInsert";

export default function App() {
  // 토큰이 있으면 로그인 상태로 시작 (만료 시 첫 fetch 의 401 로 로그아웃 처리).
  const [email, setUserEmail] = React.useState<string | null>(() =>
    getToken() ? getEmail() : null
  );

  const [category, setCategory] = React.useState("all");
  const [query, setQuery] = React.useState("");

  const [assets, setAssets] = React.useState<Asset[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [offline, setOffline] = React.useState(false);

  const { insertingId, message, error, insert, clearMessage } = useInsert();

  // 카테고리/검색어 변경 시 서버에서 자산을 가져온다 (이전 요청은 취소).
  React.useEffect(() => {
    if (!email) return; // 로그인 전에는 조회하지 않음
    const ctrl = new AbortController();
    setLoading(true);
    fetchAssets(category, query, ctrl.signal)
      .then((r) => {
        setAssets(r.assets);
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
  }, [category, query, email]);

  async function handleLogout() {
    await logout();
    setUserEmail(null);
    setAssets([]);
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

  return (
    <div className="app">
      <header className="app__header app__header--row">
        <h1 className="app__title">powerPlus 자산 라이브러리</h1>
        <button className="app__logout" onClick={handleLogout} title={email}>
          로그아웃
        </button>
      </header>

      <SearchBar value={query} onChange={setQuery} />
      <CategoryTabs categories={CATEGORIES} active={category} onChange={setCategory} />

      <div className="app__count">
        {loading ? "불러오는 중…" : `${assets.length}개 자산`}
        {offline && !loading && " · 오프라인(로컬 데이터)"}
      </div>

      <main className="app__body">
        <AssetGrid assets={assets} insertingId={insertingId} onInsert={insert} />
      </main>

      {message && (
        <div className={"toast" + (error ? " toast--error" : "")} role="status">
          {message}
        </div>
      )}
    </div>
  );
}

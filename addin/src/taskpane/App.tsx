import * as React from "react";
import CategoryTabs from "./components/CategoryTabs";
import SearchBar from "./components/SearchBar";
import AssetGrid from "./components/AssetGrid";
import { CATEGORIES } from "./data/mockAssets";
import type { Asset } from "./data/mockAssets";
import { fetchAssets } from "./api/assets";
import { useInsert } from "./hooks/useInsert";

export default function App() {
  const [category, setCategory] = React.useState("all");
  const [query, setQuery] = React.useState("");

  const [assets, setAssets] = React.useState<Asset[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [offline, setOffline] = React.useState(false);

  const { insertingId, message, error, insert, clearMessage } = useInsert();

  // 카테고리/검색어 변경 시 서버에서 자산을 가져온다 (이전 요청은 취소).
  React.useEffect(() => {
    const ctrl = new AbortController();
    setLoading(true);
    fetchAssets(category, query, ctrl.signal)
      .then((r) => {
        setAssets(r.assets);
        setOffline(r.offline);
      })
      .catch(() => {
        // 취소된 요청 — 무시
      })
      .finally(() => {
        if (!ctrl.signal.aborted) setLoading(false);
      });
    return () => ctrl.abort();
  }, [category, query]);

  // 토스트 메시지 자동 사라짐
  React.useEffect(() => {
    if (!message) return;
    const t = window.setTimeout(clearMessage, 3000);
    return () => window.clearTimeout(t);
  }, [message, clearMessage]);

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">powerPlus 자산 라이브러리</h1>
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

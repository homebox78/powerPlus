import * as React from "react";
import CategoryTabs from "./components/CategoryTabs";
import SearchBar from "./components/SearchBar";
import AssetGrid from "./components/AssetGrid";
import { CATEGORIES, filterAssets } from "./data/mockAssets";
import { useInsert } from "./hooks/useInsert";

export default function App() {
  const [category, setCategory] = React.useState("all");
  const [query, setQuery] = React.useState("");
  const { insertingId, message, error, insert, clearMessage } = useInsert();

  // 현재 카테고리 + 검색어 기준 결과 (mock). 추후 서버 fetch로 교체.
  const assets = React.useMemo(
    () => filterAssets(category, query),
    [category, query]
  );

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

      <div className="app__count">{assets.length}개 자산</div>

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

import * as React from "react";
import type { Category } from "../data/mockAssets";

interface Props {
  categories: Category[];
  active: string;
  onChange: (key: string) => void;
}

export default function CategoryTabs({ categories, active, onChange }: Props) {
  return (
    <div className="tabs" role="tablist">
      {categories.map((c) => (
        <button
          key={c.key}
          role="tab"
          aria-selected={active === c.key}
          className={"tab" + (active === c.key ? " tab--active" : "")}
          onClick={() => onChange(c.key)}
        >
          {c.label}
        </button>
      ))}
    </div>
  );
}

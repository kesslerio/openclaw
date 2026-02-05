import { Search, X, ChevronDown } from "lucide-react";
import React from "react";

const CATEGORIES = ["all", "Work", "Personal", "CopperAI", "General"];

export default function FilterBar({ filters, onFilterChange, tags = [] }) {
  const { priority, category, tag, search } = filters;

  const updateFilter = (key, value) => {
    onFilterChange({ ...filters, [key]: value === "all" ? null : value });
  };

  const clearFilters = () => {
    onFilterChange({ priority: null, category: null, tag: null, search: "" });
  };

  const hasActiveFilters = priority || category || tag || search;

  return (
    <div className="flex items-center gap-2 flex-1 min-w-0">
      {/* Search */}
      <div className="relative flex-1 min-w-[140px] max-w-[240px]">
        <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500 pointer-events-none" />
        <input
          type="text"
          placeholder="Search..."
          value={search || ""}
          onChange={(e) => updateFilter("search", e.target.value || null)}
          className="w-full bg-gray-800 border border-gray-700 rounded pl-7 pr-2 py-1 text-xs
                   focus:outline-none focus:border-blue-500 transition-colors"
        />
      </div>

      {/* Priority Filter */}
      <div className="relative">
        <select
          value={priority || "all"}
          onChange={(e) => updateFilter("priority", e.target.value)}
          className="appearance-none bg-gray-800 border border-gray-700 rounded px-2 py-1 pr-6 text-xs
                   focus:outline-none focus:border-blue-500 transition-colors cursor-pointer"
        >
          <option value="all">Priority</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <ChevronDown className="absolute right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-500 pointer-events-none" />
      </div>

      {/* Category Filter */}
      <div className="relative">
        <select
          value={category || "all"}
          onChange={(e) => updateFilter("category", e.target.value)}
          className="appearance-none bg-gray-800 border border-gray-700 rounded px-2 py-1 pr-6 text-xs
                   focus:outline-none focus:border-blue-500 transition-colors cursor-pointer"
        >
          <option value="all">Category</option>
          {CATEGORIES.filter((c) => c !== "all").map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-500 pointer-events-none" />
      </div>

      {/* Tag Filter */}
      {tags.length > 0 && (
        <div className="relative">
          <select
            value={tag || "all"}
            onChange={(e) => updateFilter("tag", e.target.value)}
            className="appearance-none bg-gray-800 border border-gray-700 rounded px-2 py-1 pr-6 text-xs
                     focus:outline-none focus:border-blue-500 transition-colors cursor-pointer"
          >
            <option value="all">Tag</option>
            {tags.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-500 pointer-events-none" />
        </div>
      )}

      {/* Clear Filters */}
      {hasActiveFilters && (
        <button
          onClick={clearFilters}
          className="flex items-center gap-1 px-1.5 py-1 text-xs text-gray-500 hover:text-white
                   hover:bg-gray-800 rounded transition-colors"
        >
          <X className="w-3 h-3" />
          Clear
        </button>
      )}
    </div>
  );
}

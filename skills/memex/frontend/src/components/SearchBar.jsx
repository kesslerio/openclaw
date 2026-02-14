import { format } from "date-fns";
import { Search, Loader2, Calendar, FileText } from "lucide-react";
import { useState } from "react";
import useMemexStore from "../store/useMemexStore";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const { searchResults, isSearching, performSearch } = useMemexStore();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    await performSearch(query);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Search Input */}
      <div className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search across all transcripts..."
              className="input pl-12"
              disabled={isSearching}
            />
          </div>
          <button
            type="submit"
            disabled={!query.trim() || isSearching}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSearching ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                Searching...
              </>
            ) : (
              <>
                <Search size={18} />
                Search
              </>
            )}
          </button>
        </form>

        <p className="text-sm text-slate-400 mt-2">
          Semantic search powered by AI. Find transcripts by meaning, not just keywords.
        </p>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto">
        {isSearching ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Loader2 className="inline-block animate-spin h-8 w-8 text-memex-primary mb-4" />
              <p className="text-slate-400">Searching through your memories...</p>
            </div>
          </div>
        ) : searchResults.length === 0 && query ? (
          <div className="flex items-center justify-center h-64 text-center">
            <div>
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold mb-2">No results found</h3>
              <p className="text-slate-400">Try different keywords or check your spelling.</p>
            </div>
          </div>
        ) : searchResults.length > 0 ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {searchResults.length} result{searchResults.length !== 1 ? "s" : ""} found
              </h3>
              <p className="text-sm text-slate-400">Sorted by relevance and recency</p>
            </div>

            {searchResults.map((result, i) => (
              <SearchResult key={i} result={result} index={i + 1} />
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 text-center">
            <div>
              <div className="text-6xl mb-4">🔎</div>
              <h3 className="text-xl font-semibold mb-2">Search Your Memory</h3>
              <p className="text-slate-400 max-w-md mx-auto">
                Enter a query above to search through all your transcripts. AI-powered semantic
                search finds relevant conversations even if they don't match your exact words.
              </p>

              <div className="mt-8 space-y-2 max-w-md mx-auto">
                <p className="text-sm text-slate-500 font-medium mb-3">Example searches:</p>
                {[
                  "project updates",
                  "meetings with Mark",
                  "discussions about pricing",
                  "action items from last week",
                ].map((example, i) => (
                  <button
                    key={i}
                    onClick={() => setQuery(example)}
                    className="w-full text-left px-4 py-2 bg-memex-surface border border-slate-700/50 rounded-lg hover:border-memex-primary/50 transition-all text-sm text-slate-300"
                  >
                    "{example}"
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SearchResult({ result, index }) {
  const { text, metadata, score, final_score } = result;
  const displayScore = final_score || score;

  const scoreColor =
    displayScore >= 0.8
      ? "bg-green-500/20 text-green-400 border-green-500/50"
      : displayScore >= 0.6
        ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/50"
        : "bg-slate-500/20 text-slate-400 border-slate-500/50";

  return (
    <div className="card hover:border-memex-primary/30 transition-all cursor-pointer">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl font-bold text-memex-primary">#{index}</span>
          <div>
            {metadata?.date && (
              <div className="flex items-center gap-2 text-sm text-slate-400 mb-1">
                <Calendar size={14} />
                {format(new Date(metadata.date), "EEEE, MMM d, yyyy")}
              </div>
            )}
            {metadata?.speaker && (
              <div className="text-xs text-slate-500">Speaker: {metadata.speaker}</div>
            )}
          </div>
        </div>

        <div className={`px-3 py-1 rounded-full border text-xs font-medium ${scoreColor}`}>
          {Math.round(displayScore * 100)}% match
        </div>
      </div>

      <p className="text-slate-300 leading-relaxed mb-3">
        {text.length > 400 ? text.slice(0, 400) + "..." : text}
      </p>

      <div className="flex items-center gap-4 text-xs text-slate-500">
        {metadata?.source_file && (
          <button className="flex items-center gap-1 hover:text-memex-secondary transition-colors">
            <FileText size={12} />
            View full transcript
          </button>
        )}

        {metadata?.topics && (
          <div className="flex gap-1">
            {metadata.topics.slice(0, 3).map((topic, i) => (
              <span key={i} className="px-2 py-0.5 bg-slate-800 rounded-full">
                {topic}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

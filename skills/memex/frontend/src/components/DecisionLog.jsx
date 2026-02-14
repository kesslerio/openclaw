import { GitBranch, Search, Filter, X, ExternalLink, Clock } from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import useMemexStore from "../store/useMemexStore";

export default function DecisionLog() {
  const [decisions, setDecisions] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { setActiveView, setSelectedTranscriptId } = useMemexStore();

  const loadDecisions = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (keyword) params.append("keyword", keyword);
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);

      const res = await fetch(`/api/decisions?${params}`);
      if (!res.ok) throw new Error("Failed to load");
      const data = await res.json();
      setDecisions(data.decisions || []);
      setCount(data.count || 0);
    } catch (err) {
      console.error("Failed to load decisions:", err);
    } finally {
      setLoading(false);
    }
  }, [keyword, startDate, endDate]);

  useEffect(() => {
    loadDecisions();
  }, [loadDecisions]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadDecisions();
  };

  const clearFilters = () => {
    setKeyword("");
    setStartDate("");
    setEndDate("");
  };

  const openSource = (fileId) => {
    if (!fileId) return;
    setSelectedTranscriptId(fileId);
    setActiveView("transcript-detail");
  };

  const hasFilters = keyword || startDate || endDate;

  // Group by date
  const grouped = {};
  decisions.forEach((dec) => {
    const key = dec.meeting_date || "Unknown";
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(dec);
  });
  const sortedDates = Object.keys(grouped).sort().reverse();

  return (
    <div className="h-full flex flex-col bg-memex-bg">
      {/* Header & Filters */}
      <div className="border-b border-slate-700/50 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <GitBranch className="text-cyan-400" size={22} />
            Decision Log
            <span className="text-sm font-normal text-slate-400">({count})</span>
          </h2>
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="text-sm text-slate-400 hover:text-white flex items-center gap-1"
            >
              <X size={14} /> Clear filters
            </button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3 text-sm">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                size={14}
              />
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Search decisions..."
                className="input pl-9 py-1.5 text-sm w-64"
              />
            </div>
            <button type="submit" className="btn-primary px-3 py-1.5 text-sm">
              Search
            </button>
          </form>

          <div className="flex items-center gap-2">
            <Filter size={14} className="text-slate-400" />
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="input px-3 py-1.5 text-sm"
            />
            <span className="text-slate-500">to</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="input px-3 py-1.5 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-memex-primary"></div>
              <p className="mt-4 text-slate-400">Loading decisions...</p>
            </div>
          </div>
        ) : decisions.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-center">
            <div>
              <div className="text-5xl mb-4">📋</div>
              <h3 className="text-lg font-semibold mb-2">No decisions found</h3>
              <p className="text-slate-400">Try adjusting your search or date range.</p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-8">
            {sortedDates.map((date) => (
              <div key={date}>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Clock size={14} />
                  {date}
                  <span className="text-xs font-normal">({grouped[date].length} decisions)</span>
                </h3>
                <div className="space-y-3">
                  {grouped[date].map((dec, i) => (
                    <div
                      key={i}
                      className="p-4 bg-slate-800/50 rounded-lg border border-cyan-900/20"
                    >
                      <p className="text-white font-medium">{dec.description}</p>
                      {dec.rationale && (
                        <p className="text-sm text-slate-400 mt-2">
                          <span className="text-slate-500 font-medium">Rationale: </span>
                          {dec.rationale}
                        </p>
                      )}
                      {dec.source_meeting && (
                        <button
                          onClick={() => openSource(dec.source_file_id)}
                          className="flex items-center gap-1 mt-3 text-xs text-slate-400 hover:text-memex-primary transition-colors"
                        >
                          <ExternalLink size={11} />
                          {dec.source_meeting.length > 60
                            ? dec.source_meeting.slice(0, 60) + "..."
                            : dec.source_meeting}
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

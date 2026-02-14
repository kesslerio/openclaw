import { CheckSquare, Filter, X, ExternalLink, User, Clock } from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import useMemexStore from "../store/useMemexStore";

export default function ActionItemsDashboard() {
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [ownerFilter, setOwnerFilter] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { setActiveView, setSelectedTranscriptId } = useMemexStore();

  const loadItems = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append("status", statusFilter);
      if (ownerFilter) params.append("owner", ownerFilter);
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);

      const res = await fetch(`/api/action-items?${params}`);
      if (!res.ok) throw new Error("Failed to load");
      const data = await res.json();
      setItems(data.action_items || []);
      setCount(data.count || 0);
    } catch (err) {
      console.error("Failed to load action items:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, ownerFilter, startDate, endDate]);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  const clearFilters = () => {
    setStatusFilter("");
    setOwnerFilter("");
    setStartDate("");
    setEndDate("");
  };

  const openSource = (fileId) => {
    if (!fileId) return;
    setSelectedTranscriptId(fileId);
    setActiveView("transcript-detail");
  };

  // Collect unique owners for filter
  const owners = [...new Set(items.map((i) => i.owner).filter((o) => o && o !== "Unassigned"))];
  const hasFilters = statusFilter || ownerFilter || startDate || endDate;

  // Group by meeting date
  const grouped = {};
  items.forEach((item) => {
    const key = item.meeting_date || "Unknown";
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(item);
  });
  const sortedDates = Object.keys(grouped).sort().reverse();

  return (
    <div className="h-full flex flex-col bg-memex-bg">
      {/* Header & Filters */}
      <div className="border-b border-slate-700/50 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <CheckSquare className="text-memex-primary" size={22} />
            Action Items
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
          <Filter size={16} className="text-slate-400" />

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input px-3 py-1.5 text-sm"
          >
            <option value="">All Status</option>
            <option value="open">Open</option>
            <option value="completed">Completed</option>
          </select>

          <select
            value={ownerFilter}
            onChange={(e) => setOwnerFilter(e.target.value)}
            className="input px-3 py-1.5 text-sm"
          >
            <option value="">All Owners</option>
            {owners.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>

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

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-memex-primary"></div>
              <p className="mt-4 text-slate-400">Loading action items...</p>
            </div>
          </div>
        ) : items.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-center">
            <div>
              <div className="text-5xl mb-4">✅</div>
              <h3 className="text-lg font-semibold mb-2">No action items found</h3>
              <p className="text-slate-400">Try adjusting your filters or date range.</p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-8">
            {sortedDates.map((date) => (
              <div key={date}>
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Clock size={14} />
                  {date}
                  <span className="text-xs font-normal">({grouped[date].length} items)</span>
                </h3>
                <div className="space-y-2">
                  {grouped[date].map((item, i) => (
                    <div
                      key={i}
                      className={`p-4 rounded-lg border flex items-start gap-3 ${
                        item.status === "completed"
                          ? "bg-green-900/10 border-green-800/30"
                          : "bg-slate-800/50 border-slate-700/30"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={item.status === "completed"}
                        readOnly
                        className="mt-1 rounded border-slate-600"
                      />
                      <div className="flex-1 min-w-0">
                        <p
                          className={`${item.status === "completed" ? "line-through text-slate-500" : "text-white"}`}
                        >
                          {item.description}
                        </p>
                        <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-400">
                          {item.owner !== "Unassigned" && (
                            <span className="flex items-center gap-1 px-2 py-0.5 bg-slate-700 rounded-full">
                              <User size={11} /> {item.owner}
                            </span>
                          )}
                          {item.source_meeting && (
                            <button
                              onClick={() => openSource(item.source_file_id)}
                              className="flex items-center gap-1 hover:text-memex-primary transition-colors"
                            >
                              <ExternalLink size={11} />
                              {item.source_meeting.length > 50
                                ? item.source_meeting.slice(0, 50) + "..."
                                : item.source_meeting}
                            </button>
                          )}
                          {item.due_date && <span className="text-amber-400">{item.due_date}</span>}
                        </div>
                      </div>
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

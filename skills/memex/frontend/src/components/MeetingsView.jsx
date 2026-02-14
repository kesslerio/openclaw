import { Search, Clock, FileText, ChevronRight, Filter, X } from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import useMemexStore from "../store/useMemexStore";

export default function MeetingsView() {
  const [meetings, setMeetings] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 30;

  const { setActiveView, setSelectedTranscriptId } = useMemexStore();

  const loadMeetings = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append("limit", limit);
      params.append("offset", offset);
      if (searchQuery) params.append("search", searchQuery);
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);

      const res = await fetch(`/api/transcripts?${params}`);
      if (!res.ok) throw new Error("Failed to load");
      const data = await res.json();
      setMeetings(data.transcripts || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error("Failed to load meetings:", err);
    } finally {
      setLoading(false);
    }
  }, [offset, searchQuery, startDate, endDate]);

  useEffect(() => {
    loadMeetings();
  }, [loadMeetings]);

  const handleSearch = (e) => {
    e.preventDefault();
    setOffset(0);
    loadMeetings();
  };

  const clearFilters = () => {
    setSearchQuery("");
    setStartDate("");
    setEndDate("");
    setOffset(0);
  };

  const openTranscript = (fileId) => {
    setSelectedTranscriptId(fileId);
    setActiveView("transcript-detail");
  };

  const formatDuration = (ms) => {
    if (!ms) return "";
    const mins = Math.round(ms / 60000);
    if (mins < 60) return `${mins}m`;
    const hrs = Math.floor(mins / 60);
    const rem = mins % 60;
    return `${hrs}h ${rem}m`;
  };

  const hasFilters = searchQuery || startDate || endDate;

  return (
    <div className="h-full flex flex-col bg-memex-bg">
      {/* Search & Filters */}
      <div className="border-b border-slate-700/50 p-4 space-y-3">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search meetings by title..."
              className="input pl-10 w-full"
            />
          </div>
          <button type="submit" className="btn-primary px-4">
            Search
          </button>
        </form>

        <div className="flex items-center gap-3 text-sm">
          <Filter size={16} className="text-slate-400" />
          <input
            type="date"
            value={startDate}
            onChange={(e) => {
              setStartDate(e.target.value);
              setOffset(0);
            }}
            className="input px-3 py-1.5 text-sm"
          />
          <span className="text-slate-500">to</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => {
              setEndDate(e.target.value);
              setOffset(0);
            }}
            className="input px-3 py-1.5 text-sm"
          />
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="text-slate-400 hover:text-white flex items-center gap-1"
            >
              <X size={14} /> Clear
            </button>
          )}
          <span className="ml-auto text-slate-400">{total} meetings</span>
        </div>
      </div>

      {/* Meeting List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-memex-primary"></div>
              <p className="mt-4 text-slate-400">Loading meetings...</p>
            </div>
          </div>
        ) : meetings.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-center">
            <div>
              <div className="text-5xl mb-4">📋</div>
              <h3 className="text-lg font-semibold mb-2">No meetings found</h3>
              <p className="text-slate-400">Try adjusting your search or date filters.</p>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-slate-700/30">
            {meetings.map((meeting) => (
              <button
                key={meeting.file_id}
                onClick={() => openTranscript(meeting.file_id)}
                className="w-full text-left px-6 py-4 hover:bg-slate-800/50 transition-colors flex items-center gap-4 group"
              >
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center">
                  <FileText className="text-memex-primary" size={22} />
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-white truncate group-hover:text-memex-primary transition-colors">
                    {meeting.title}
                  </h3>
                  <div className="flex items-center gap-4 mt-1 text-sm text-slate-400">
                    <span>{meeting.date}</span>
                    {meeting.duration_ms > 0 && (
                      <span className="flex items-center gap-1">
                        <Clock size={13} />
                        {formatDuration(meeting.duration_ms)}
                      </span>
                    )}
                    {meeting.has_notes && (
                      <span className="text-xs px-2 py-0.5 bg-memex-primary/20 text-memex-primary rounded-full">
                        Notes
                      </span>
                    )}
                  </div>
                </div>

                <ChevronRight
                  className="text-slate-600 group-hover:text-slate-400 flex-shrink-0"
                  size={18}
                />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {total > limit && (
        <div className="border-t border-slate-700/50 p-3 flex items-center justify-center gap-4">
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="text-sm text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-slate-500">
            {offset + 1}-{Math.min(offset + limit, total)} of {total}
          </span>
          <button
            onClick={() => setOffset(offset + limit)}
            disabled={offset + limit >= total}
            className="text-sm text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

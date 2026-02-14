import {
  ArrowLeft,
  FileText,
  CheckSquare,
  GitBranch,
  MessageSquare,
  Clock,
  Users,
} from "lucide-react";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import useMemexStore from "../store/useMemexStore";

export default function TranscriptDetail() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("summary");
  const { selectedTranscriptId, setActiveView } = useMemexStore();

  useEffect(() => {
    if (!selectedTranscriptId) return;
    loadTranscript();
  }, [selectedTranscriptId]);

  const loadTranscript = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/transcripts/${selectedTranscriptId}`);
      if (!res.ok) throw new Error("Failed to load");
      const d = await res.json();
      setData(d);
    } catch (err) {
      console.error("Failed to load transcript:", err);
    } finally {
      setLoading(false);
    }
  };

  const goBack = () => {
    setActiveView("meetings");
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-memex-bg">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-memex-primary"></div>
          <p className="mt-4 text-slate-400">Loading transcript...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="h-full flex items-center justify-center bg-memex-bg">
        <p className="text-slate-400">Transcript not found.</p>
      </div>
    );
  }

  const meta = data.metadata || {};
  const parsed = data.parsed_notes || {};
  const segments = data.segments || [];
  const startTime = meta.start_time;
  const dateStr = startTime
    ? new Date(startTime).toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "";
  const durationMin = meta.duration_ms ? Math.round(meta.duration_ms / 60000) : 0;

  const tabs = [
    { id: "summary", label: "Summary", icon: FileText },
    {
      id: "notes",
      label: "Notes",
      icon: CheckSquare,
      badge: (parsed.action_items?.length || 0) + (parsed.decisions?.length || 0),
    },
    { id: "transcript", label: "Transcript", icon: MessageSquare, badge: segments.length },
  ];

  return (
    <div className="h-full flex flex-col bg-memex-bg">
      {/* Header */}
      <div className="border-b border-slate-700/50 p-4">
        <div className="flex items-center gap-3 mb-3">
          <button onClick={goBack} className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
            <ArrowLeft size={20} />
          </button>
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold truncate">{meta.filename || "Untitled"}</h2>
            <div className="flex items-center gap-4 text-sm text-slate-400 mt-1">
              {dateStr && <span>{dateStr}</span>}
              {durationMin > 0 && (
                <span className="flex items-center gap-1">
                  <Clock size={13} /> {durationMin} min
                </span>
              )}
              {parsed.participants?.length > 0 && (
                <span className="flex items-center gap-1">
                  <Users size={13} /> {parsed.participants.length} participants
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Keywords */}
        {parsed.keywords?.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {parsed.keywords.map((kw, i) => (
              <span key={i} className="text-xs px-2 py-1 bg-slate-800 text-slate-300 rounded-full">
                {kw}
              </span>
            ))}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                  ${
                    activeTab === tab.id
                      ? "bg-memex-primary text-white"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }
                `}
              >
                <Icon size={16} />
                {tab.label}
                {tab.badge > 0 && (
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded-full ${
                      activeTab === tab.id ? "bg-white/20" : "bg-slate-700"
                    }`}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {activeTab === "summary" && <SummaryTab parsed={parsed} notes={data.notes} />}
          {activeTab === "notes" && <NotesTab parsed={parsed} />}
          {activeTab === "transcript" && <TranscriptTab segments={segments} text={data.text} />}
        </div>
      </div>
    </div>
  );
}

function SummaryTab({ parsed, notes }) {
  if (parsed.summary) {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-3">Overview</h3>
          <div className="prose prose-invert prose-sm">
            <ReactMarkdown>{parsed.summary}</ReactMarkdown>
          </div>
        </div>

        {parsed.key_points?.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Key Discussion Points</h3>
            <div className="space-y-3">
              {parsed.key_points.map((point, i) => (
                <div key={i} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/30">
                  <div className="prose prose-invert prose-sm">
                    <ReactMarkdown>{point}</ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {parsed.follow_ups?.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Follow-ups</h3>
            <ul className="space-y-2">
              {parsed.follow_ups.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-slate-300">
                  <span className="text-memex-primary mt-0.5">-</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  // Fallback: render raw notes
  if (notes) {
    return (
      <div className="prose prose-invert prose-sm">
        <ReactMarkdown>{notes}</ReactMarkdown>
      </div>
    );
  }

  return (
    <div className="text-center text-slate-400 py-12">
      <p>No summary available for this meeting.</p>
    </div>
  );
}

function NotesTab({ parsed }) {
  const actionItems = parsed.action_items || [];
  const decisions = parsed.decisions || [];

  if (actionItems.length === 0 && decisions.length === 0) {
    return (
      <div className="text-center text-slate-400 py-12">
        <p>No structured notes extracted from this meeting.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Action Items */}
      {actionItems.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <CheckSquare size={20} className="text-memex-primary" />
            Action Items ({actionItems.length})
          </h3>
          <div className="space-y-2">
            {actionItems.map((item, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg border flex items-start gap-3 ${
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
                <div className="flex-1">
                  <p
                    className={
                      item.status === "completed" ? "line-through text-slate-500" : "text-white"
                    }
                  >
                    {item.description}
                  </p>
                  <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
                    {item.owner !== "Unassigned" && (
                      <span className="px-2 py-0.5 bg-slate-700 rounded-full">@{item.owner}</span>
                    )}
                    {item.due_date && <span>{item.due_date}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decisions */}
      {decisions.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <GitBranch size={20} className="text-cyan-400" />
            Decisions ({decisions.length})
          </h3>
          <div className="space-y-3">
            {decisions.map((dec, i) => (
              <div key={i} className="p-4 bg-slate-800/50 rounded-lg border border-cyan-900/30">
                <p className="text-white font-medium">{dec.description}</p>
                {dec.rationale && (
                  <p className="text-sm text-slate-400 mt-2">
                    <span className="text-slate-500 font-medium">Rationale:</span> {dec.rationale}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TranscriptTab({ segments, text }) {
  if (segments && segments.length > 0) {
    return (
      <div className="space-y-4">
        {segments.map((seg, i) => {
          const startSec = seg.start_time != null ? Math.round(seg.start_time / 1000) : null;
          const mins = startSec != null ? Math.floor(startSec / 60) : null;
          const secs = startSec != null ? startSec % 60 : null;
          const timestamp =
            mins != null ? `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}` : "";

          return (
            <div key={i} className="flex gap-3">
              {timestamp && (
                <span className="text-xs text-slate-500 font-mono w-12 flex-shrink-0 pt-1 text-right">
                  {timestamp}
                </span>
              )}
              <div className="flex-1">
                {seg.speaker && (
                  <span className="text-xs font-semibold text-memex-primary">{seg.speaker}</span>
                )}
                <p className="text-slate-300 text-sm leading-relaxed">{seg.content}</p>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  if (text) {
    return <div className="prose prose-invert prose-sm whitespace-pre-wrap">{text}</div>;
  }

  return (
    <div className="text-center text-slate-400 py-12">
      <p>No transcript available for this meeting.</p>
    </div>
  );
}

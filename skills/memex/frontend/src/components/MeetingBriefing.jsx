import {
  ArrowLeft,
  FileText,
  Mail,
  CalendarDays,
  Video,
  Users,
  Clock,
  Send,
  CheckSquare,
  GitBranch,
  ExternalLink,
  HardDrive,
  Loader2,
  PenSquare,
} from "lucide-react";
import { useState, useRef, useEffect } from "react";
import useMemexStore from "../store/useMemexStore";

export default function MeetingBriefing() {
  const {
    selectedEvent,
    briefingData,
    briefingLoading,
    setActiveView,
    setSelectedTranscriptId,
    openEmailCompose,
    sendMessage,
    messages,
    isTyping,
    addMessage,
  } = useMemexStore();

  const [activeTab, setActiveTab] = useState("briefing");

  if (!selectedEvent) {
    return (
      <div className="h-full flex items-center justify-center bg-memex-bg">
        <p className="text-slate-400">No event selected.</p>
      </div>
    );
  }

  const ev = selectedEvent;
  const meetLink = ev.meet_link || ev.hangout_link;
  const attendees = ev.attendees || [];
  const attendeeEmails = attendees.map((a) => a.email).filter(Boolean);

  const formatTime = (isoStr) => {
    if (!isoStr) return "";
    return new Date(isoStr).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  const goBack = () => setActiveView("today");

  const handleComposeEmail = () => {
    openEmailCompose(attendeeEmails, `Re: ${ev.summary}`);
  };

  const briefing = briefingData?.briefing || {};
  const emails = briefingData?.emails || [];
  const synthesizedContext = briefingData?.synthesized_context || null;

  const tabs = [
    { id: "briefing", label: "Briefing", icon: FileText },
    { id: "emails", label: "Emails", icon: Mail, badge: emails.length },
    {
      id: "past-meetings",
      label: "Past Meetings",
      icon: CalendarDays,
      badge: briefing.total_past_meetings || 0,
    },
  ];

  return (
    <div className="h-full flex flex-col bg-memex-bg">
      {/* Header */}
      <div className="border-b border-slate-700/50 p-4">
        <div className="flex items-center gap-3 mb-2">
          <button onClick={goBack} className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
            <ArrowLeft size={20} />
          </button>
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold truncate">{ev.summary}</h2>
            <div className="flex items-center gap-4 text-sm text-slate-400 mt-0.5">
              <span className="flex items-center gap-1">
                <Clock size={13} /> {formatTime(ev.start)} - {formatTime(ev.end)}
              </span>
              {attendees.length > 0 && (
                <span className="flex items-center gap-1">
                  <Users size={13} /> {attendees.length} attendees
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {meetLink && (
              <a
                href={meetLink}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-900/30 text-cyan-400 rounded-lg text-sm hover:bg-cyan-900/50 transition-colors"
              >
                <Video size={14} /> Join Meet
              </a>
            )}
            <button
              onClick={handleComposeEmail}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-memex-primary/20 text-memex-primary rounded-lg text-sm hover:bg-memex-primary/30 transition-colors"
            >
              <PenSquare size={14} /> Compose Email
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mt-2">
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

      {/* Two-Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column - Tab Content (60%) */}
        <div className="w-3/5 border-r border-slate-700/50 overflow-y-auto p-6">
          {briefingLoading ? (
            <div className="text-center py-16">
              <Loader2 size={32} className="mx-auto text-memex-primary animate-spin" />
              <p className="mt-4 text-slate-400">Loading briefing...</p>
            </div>
          ) : (
            <>
              {activeTab === "briefing" && (
                <BriefingTab
                  briefing={briefing}
                  synthesizedContext={synthesizedContext}
                  setActiveView={setActiveView}
                  setSelectedTranscriptId={setSelectedTranscriptId}
                />
              )}
              {activeTab === "emails" && <EmailsTab emails={emails} />}
              {activeTab === "past-meetings" && (
                <PastMeetingsTab
                  briefing={briefing}
                  setActiveView={setActiveView}
                  setSelectedTranscriptId={setSelectedTranscriptId}
                />
              )}
            </>
          )}
        </div>

        {/* Right Column - AI Chat (40%) */}
        <div className="w-2/5 flex flex-col">
          <BriefingChat
            eventTitle={ev.summary}
            attendeeNames={attendees.map((a) => a.name || a.email).filter(Boolean)}
          />
        </div>
      </div>
    </div>
  );
}

function BriefingTab({ briefing, synthesizedContext, setActiveView, setSelectedTranscriptId }) {
  const actionItems = briefing.unresolved_action_items || [];
  const decisions = briefing.key_decisions || [];
  const meetings = briefing.matching_meetings || [];

  return (
    <div className="space-y-8">
      {/* Synthesized Context or Fallback Summary */}
      {synthesizedContext ? (
        <div className="p-4 bg-slate-800/30 rounded-lg border border-memex-primary/20">
          <h3 className="text-sm font-semibold text-memex-primary uppercase tracking-wider mb-2">
            Meeting Context
          </h3>
          <div className="text-sm text-slate-300 whitespace-pre-wrap">{synthesizedContext}</div>
        </div>
      ) : meetings.length > 0 ? (
        <div>
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Past Meeting Context
          </h3>
          <p className="text-slate-300 text-sm">
            Found {briefing.total_past_meetings || 0} past meetings with these attendees.
            {actionItems.length > 0 && ` ${actionItems.length} unresolved action items.`}
            {decisions.length > 0 && ` ${decisions.length} key decisions.`}
          </p>
        </div>
      ) : null}

      {meetings.length === 0 && (
        <div className="text-center py-8">
          <CalendarDays size={40} className="mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">No past meetings found with these attendees.</p>
        </div>
      )}

      {/* Action Items */}
      {actionItems.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <CheckSquare size={16} className="text-amber-400" />
            Unresolved Action Items ({actionItems.length})
          </h3>
          <div className="space-y-2">
            {actionItems.map((item, i) => (
              <div key={i} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/30">
                <p className="text-white text-sm">{item.description}</p>
                <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-400">
                  {item.owner !== "Unassigned" && (
                    <span className="px-2 py-0.5 bg-slate-700 rounded-full">@{item.owner}</span>
                  )}
                  {item.meeting_date && <span>{item.meeting_date}</span>}
                  {item.source_meeting && (
                    <button
                      onClick={() => {
                        if (item.source_file_id) {
                          setSelectedTranscriptId(item.source_file_id);
                          setActiveView("transcript-detail");
                        }
                      }}
                      className="text-memex-primary hover:underline"
                    >
                      {item.source_meeting}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decisions */}
      {decisions.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <GitBranch size={16} className="text-cyan-400" />
            Key Decisions ({decisions.length})
          </h3>
          <div className="space-y-2">
            {decisions.map((dec, i) => (
              <div key={i} className="p-3 bg-slate-800/50 rounded-lg border border-cyan-900/20">
                <p className="text-white text-sm">{dec.description}</p>
                {dec.rationale && (
                  <p className="text-xs text-slate-400 mt-1">Rationale: {dec.rationale}</p>
                )}
                <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-500">
                  {dec.meeting_date && <span>{dec.meeting_date}</span>}
                  {dec.source_meeting && <span>{dec.source_meeting}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function EmailsTab({ emails }) {
  const [expandedId, setExpandedId] = useState(null);

  if (emails.length === 0) {
    return (
      <div className="space-y-8">
        <div className="text-center py-8">
          <Mail size={40} className="mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400">No recent email threads found with these attendees.</p>
        </div>

        {/* Google Drive placeholder */}
        <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/30">
          <div className="flex items-center gap-2 text-slate-400">
            <HardDrive size={18} />
            <span className="font-medium">Google Drive</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Drive integration coming soon. Shared files with attendees will appear here.
          </p>
        </div>
      </div>
    );
  }

  const formatDate = (isoStr) => {
    const d = new Date(isoStr);
    const now = new Date();
    const diff = now - d;
    if (diff < 86400000)
      return d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
    if (diff < 604800000) return d.toLocaleDateString("en-US", { weekday: "short" });
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  const formatFullDate = (isoStr) => {
    return new Date(isoStr).toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const toggleExpand = (id) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        {emails.map((email, i) => {
          const id = email.message_id || i;
          const isExpanded = expandedId === id;
          return (
            <div
              key={id}
              onClick={() => toggleExpand(id)}
              className={`p-3 bg-slate-800/50 rounded-lg border cursor-pointer transition-colors ${
                isExpanded
                  ? "border-memex-primary/40"
                  : "border-slate-700/30 hover:border-slate-600/50"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p
                    className={`text-sm font-medium ${isExpanded ? "" : "truncate"} ${email.is_read ? "text-slate-300" : "text-white"}`}
                  >
                    {email.subject}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {email.from?.name || email.from?.email}
                    {isExpanded && email.to?.length > 0 && (
                      <span className="text-slate-500">
                        {" "}
                        → {email.to.map((t) => t.name || t.email).join(", ")}
                      </span>
                    )}
                  </p>
                  {!isExpanded && email.snippet && (
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">{email.snippet}</p>
                  )}
                </div>
                <span className="text-xs text-slate-500 flex-shrink-0">
                  {isExpanded ? formatFullDate(email.date) : formatDate(email.date)}
                </span>
              </div>

              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-slate-700/30">
                  <p className="text-sm text-slate-300 whitespace-pre-wrap">
                    {email.body || email.snippet || "No content available."}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Google Drive placeholder */}
      <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/30">
        <div className="flex items-center gap-2 text-slate-400">
          <HardDrive size={18} />
          <span className="font-medium">Google Drive</span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Drive integration coming soon. Shared files with attendees will appear here.
        </p>
      </div>
    </div>
  );
}

function PastMeetingsTab({ briefing, setActiveView, setSelectedTranscriptId }) {
  const meetings = briefing.matching_meetings || [];

  if (meetings.length === 0) {
    return (
      <div className="text-center py-8">
        <CalendarDays size={40} className="mx-auto text-slate-600 mb-3" />
        <p className="text-slate-400">No past meetings found with these attendees.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {meetings.map((meeting, i) => (
        <button
          key={meeting.file_id || i}
          onClick={() => {
            if (meeting.file_id) {
              setSelectedTranscriptId(meeting.file_id);
              setActiveView("transcript-detail");
            }
          }}
          className="w-full text-left p-3 bg-slate-800/50 rounded-lg border border-slate-700/30 hover:border-memex-primary/30 transition-colors group"
        >
          <div className="flex items-center justify-between">
            <div className="min-w-0">
              <p className="text-sm font-medium text-white truncate group-hover:text-memex-primary transition-colors">
                {meeting.title}
              </p>
              <p className="text-xs text-slate-400 mt-0.5">{meeting.date}</p>
            </div>
            <ExternalLink
              size={14}
              className="text-slate-600 group-hover:text-memex-primary transition-colors flex-shrink-0"
            />
          </div>
        </button>
      ))}
    </div>
  );
}

function BriefingChat({ eventTitle, attendeeNames }) {
  const [chatMessages, setChatMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");

    const userMsg = { role: "user", content: userText };
    setChatMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      // Prepend context about the meeting
      const contextPrefix =
        attendeeNames.length > 0 ? `About meetings with ${attendeeNames.join(", ")}: ` : "";
      const query = contextPrefix + userText;

      const response = await fetch("/api/chat/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error("Query failed");
      const data = await response.json();

      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-slate-700/50">
        <h3 className="text-sm font-semibold text-slate-300">AI Chat</h3>
        <p className="text-xs text-slate-500">Ask about meetings with these attendees</p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {chatMessages.length === 0 && (
          <div className="text-center py-8">
            <p className="text-xs text-slate-500">
              Ask questions about your history with these attendees, e.g.:
            </p>
            <div className="mt-3 space-y-2">
              {[
                "What did we decide last time?",
                "What action items are pending?",
                "Summarize our last meeting",
              ].map((q, i) => (
                <button
                  key={i}
                  onClick={() => setInput(q)}
                  className="block w-full text-xs text-left px-3 py-2 bg-slate-800/50 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {chatMessages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[90%] px-3 py-2 rounded-lg text-sm ${
                msg.role === "user" ? "bg-memex-primary text-white" : "bg-slate-800 text-slate-200"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="px-3 py-2 bg-slate-800 rounded-lg">
              <Loader2 size={16} className="animate-spin text-memex-primary" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-3 border-t border-slate-700/50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about this meeting..."
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-memex-primary"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="p-2 bg-memex-primary text-white rounded-lg hover:bg-memex-primary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

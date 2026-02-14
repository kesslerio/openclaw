import { Menu, X, Brain } from "lucide-react";

export default function Header({ sidebarOpen, onToggleSidebar, activeView }) {
  const viewTitles = {
    today: "Today's Schedule",
    calendar: "Calendar",
    "meeting-briefing": "Meeting Briefing",
    chat: "Chat with Your Memory",
    meetings: "Meetings",
    "transcript-detail": "Meeting Detail",
    "action-items": "Action Items",
    decisions: "Decision Log",
    journals: "Daily Journals",
    search: "Search Transcripts",
  };

  return (
    <header className="bg-memex-surface border-b border-slate-700/50 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>

        <div className="flex items-center gap-3">
          <Brain className="text-memex-primary" size={28} />
          <div>
            <h1 className="text-xl font-semibold">{viewTitles[activeView]}</h1>
            <p className="text-sm text-slate-400">Your AI Memory Partner</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-sm text-slate-400">
          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
          Connected
        </div>
      </div>
    </header>
  );
}

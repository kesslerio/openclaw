import {
  MessageSquare,
  BookOpen,
  Search,
  Settings,
  HelpCircle,
  FileText,
  CheckSquare,
  GitBranch,
  RefreshCw,
  Loader2,
  CheckCircle,
  AlertCircle,
  CalendarDays,
  Calendar,
} from "lucide-react";
import useMemexStore from "../store/useMemexStore";
import IntegrationStatus from "./IntegrationStatus";

export default function Sidebar({ activeView, onViewChange, onClose }) {
  const { messages, journals, syncStatus, syncResult, startPlaudSync } = useMemexStore();

  const navItems = [
    { id: "today", icon: CalendarDays, label: "Today", badge: null },
    { id: "calendar", icon: Calendar, label: "Calendar", badge: null },
    { id: "chat", icon: MessageSquare, label: "Chat", badge: messages.length },
    { id: "meetings", icon: FileText, label: "Meetings", badge: null },
    { id: "action-items", icon: CheckSquare, label: "Action Items", badge: null },
    { id: "decisions", icon: GitBranch, label: "Decisions", badge: null },
    { id: "journals", icon: BookOpen, label: "Journals", badge: journals.length },
    { id: "search", icon: Search, label: "Search", badge: null },
  ];

  return (
    <aside className="w-64 bg-memex-surface border-r border-slate-700/50 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700/50">
        <h2 className="text-2xl font-bold text-memex-primary flex items-center gap-2">
          <span className="text-3xl">🧠</span>
          Memex
        </h2>
        <p className="text-sm text-slate-400 mt-1">Personal Memory AI</p>
      </div>

      {/* Plaud Sync Button */}
      <div className="px-4 pt-4">
        <button
          onClick={startPlaudSync}
          disabled={syncStatus === "running"}
          className={`
            w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200
            ${
              syncStatus === "running"
                ? "bg-amber-900/30 text-amber-300 border border-amber-700/40 cursor-wait"
                : syncStatus === "done"
                  ? "bg-green-900/30 text-green-300 border border-green-700/40 hover:bg-green-900/40"
                  : syncStatus === "error"
                    ? "bg-red-900/30 text-red-300 border border-red-700/40 hover:bg-red-900/40"
                    : "bg-slate-800 text-slate-200 border border-slate-600/50 hover:bg-slate-700 hover:border-memex-primary/40"
            }
          `}
        >
          {syncStatus === "running" ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              <span>Syncing...</span>
            </>
          ) : syncStatus === "done" ? (
            <>
              <CheckCircle size={16} />
              <span>Pull from Plaud Now</span>
            </>
          ) : syncStatus === "error" ? (
            <>
              <AlertCircle size={16} />
              <span>Pull from Plaud Now</span>
            </>
          ) : (
            <>
              <RefreshCw size={16} />
              <span>Pull from Plaud Now</span>
            </>
          )}
        </button>

        {/* Sync result message */}
        {syncResult && syncStatus !== "running" && (
          <div
            className={`mt-2 text-xs px-3 py-2 rounded-lg ${
              syncStatus === "error"
                ? "bg-red-900/20 text-red-300"
                : "bg-green-900/20 text-green-300"
            }`}
          >
            {syncResult}
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                ${
                  isActive
                    ? "bg-memex-primary text-white shadow-lg"
                    : "text-slate-300 hover:bg-slate-700/50"
                }
              `}
            >
              <Icon size={20} />
              <span className="flex-1 text-left font-medium">{item.label}</span>
              {item.badge !== null && item.badge > 0 && (
                <span
                  className={`
                  text-xs px-2 py-0.5 rounded-full font-medium
                  ${isActive ? "bg-white/20" : "bg-slate-700 text-slate-300"}
                `}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700/50 space-y-2">
        {/* Integration Status */}
        <IntegrationStatus />

        <button className="w-full flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-slate-700/50 rounded-lg transition-colors">
          <Settings size={18} />
          <span className="text-sm">Settings</span>
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-slate-700/50 rounded-lg transition-colors">
          <HelpCircle size={18} />
          <span className="text-sm">Help</span>
        </button>

        <div className="mt-4 pt-4 border-t border-slate-700/50 text-xs text-slate-500 text-center">
          <p>Memex v0.1.0</p>
          <p className="mt-1">Built by Nike 🐾</p>
        </div>
      </div>
    </aside>
  );
}

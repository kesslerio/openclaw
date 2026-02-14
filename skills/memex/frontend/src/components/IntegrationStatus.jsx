import { CalendarDays, Mail } from "lucide-react";
import { useEffect } from "react";
import useMemexStore from "../store/useMemexStore";

export default function IntegrationStatus() {
  const { integrationStatus, loadIntegrationStatus } = useMemexStore();

  useEffect(() => {
    loadIntegrationStatus();
  }, []);

  if (!integrationStatus) return null;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2 px-4 py-1.5">
        <CalendarDays size={14} className="text-slate-400" />
        <span className="text-xs text-slate-400 flex-1">Calendar</span>
        <span
          className={`w-2 h-2 rounded-full ${
            integrationStatus.calendar_connected ? "bg-green-500" : "bg-red-500"
          }`}
        />
      </div>
      <div className="flex items-center gap-2 px-4 py-1.5">
        <Mail size={14} className="text-slate-400" />
        <span className="text-xs text-slate-400 flex-1">Gmail</span>
        <span
          className={`w-2 h-2 rounded-full ${
            integrationStatus.gmail_connected ? "bg-green-500" : "bg-red-500"
          }`}
        />
      </div>
    </div>
  );
}

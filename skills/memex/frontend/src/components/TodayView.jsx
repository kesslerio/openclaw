import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Clock,
  Users,
  Video,
  ExternalLink,
  FileText,
  AlertCircle,
  CheckSquare,
} from "lucide-react";
import { useState, useEffect } from "react";
import useMemexStore from "../store/useMemexStore";

export default function TodayView() {
  const { todayEvents, todayEventsLoading, todayDate, loadTodayEvents, openMeetingBriefing } =
    useMemexStore();

  useEffect(() => {
    loadTodayEvents(todayDate);
  }, []);

  const changeDate = (offset) => {
    const d = new Date(todayDate + "T12:00:00");
    d.setDate(d.getDate() + offset);
    const newDate = d.toISOString().split("T")[0];
    loadTodayEvents(newDate);
  };

  const goToday = () => {
    const today = new Date().toISOString().split("T")[0];
    loadTodayEvents(today);
  };

  const isToday = todayDate === new Date().toISOString().split("T")[0];

  const dateDisplay = new Date(todayDate + "T12:00:00").toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const formatTime = (isoStr) => {
    if (!isoStr) return "";
    const d = new Date(isoStr);
    return d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
  };

  const getDuration = (start, end) => {
    if (!start || !end) return "";
    const ms = new Date(end) - new Date(start);
    const min = Math.round(ms / 60000);
    if (min < 60) return `${min}m`;
    const h = Math.floor(min / 60);
    const m = min % 60;
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  };

  return (
    <div className="h-full flex flex-col bg-memex-bg">
      {/* Date Navigation */}
      <div className="border-b border-slate-700/50 p-4">
        <div className="flex items-center justify-between max-w-3xl mx-auto">
          <button
            onClick={() => changeDate(-1)}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <ChevronLeft size={20} />
          </button>

          <div className="text-center">
            <h2 className="text-lg font-semibold">{dateDisplay}</h2>
            {!isToday && (
              <button onClick={goToday} className="text-xs text-memex-primary hover:underline mt-1">
                Go to Today
              </button>
            )}
          </div>

          <button
            onClick={() => changeDate(1)}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Events List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto space-y-3">
          {todayEventsLoading ? (
            <div className="text-center py-16">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-memex-primary"></div>
              <p className="mt-4 text-slate-400">Loading calendar events...</p>
            </div>
          ) : todayEvents.length === 0 ? (
            <div className="text-center py-16">
              <CalendarDays size={48} className="mx-auto text-slate-600 mb-4" />
              <h3 className="text-lg font-medium text-slate-400">No events scheduled</h3>
              <p className="text-sm text-slate-500 mt-1">
                {isToday ? "You're free today!" : "No events on this day."}
              </p>
            </div>
          ) : (
            todayEvents.map((event, idx) => (
              <EventCard
                key={event.event_id || idx}
                event={event}
                formatTime={formatTime}
                getDuration={getDuration}
                onClick={() => openMeetingBriefing(event)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function EventCard({ event, formatTime, getDuration, onClick }) {
  const ctx = event.context || {};
  const attendeeCount = (event.attendees || []).length;
  const meetLink = event.meet_link || event.hangout_link;
  const isAllDay = event.all_day;

  return (
    <button
      onClick={onClick}
      className="w-full text-left p-4 bg-memex-surface rounded-xl border border-slate-700/50 hover:border-memex-primary/50 hover:bg-slate-800/80 transition-all duration-200 group"
    >
      <div className="flex items-start gap-4">
        {/* Time Column */}
        <div className="w-20 flex-shrink-0 pt-0.5">
          {isAllDay ? (
            <span className="text-sm font-medium text-amber-400">All Day</span>
          ) : (
            <>
              <p className="text-sm font-medium text-white">{formatTime(event.start)}</p>
              <p className="text-xs text-slate-500">{formatTime(event.end)}</p>
            </>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white group-hover:text-memex-primary transition-colors truncate">
            {event.summary}
          </h3>

          <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-400">
            {!isAllDay && (
              <span className="flex items-center gap-1">
                <Clock size={12} /> {getDuration(event.start, event.end)}
              </span>
            )}
            {attendeeCount > 0 && (
              <span className="flex items-center gap-1">
                <Users size={12} /> {attendeeCount}
              </span>
            )}
            {meetLink && (
              <span className="flex items-center gap-1 text-cyan-400">
                <Video size={12} /> Meet
              </span>
            )}
          </div>

          {/* Context Tags */}
          <div className="flex flex-wrap gap-1.5 mt-2">
            {ctx.has_transcript && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 bg-green-900/30 text-green-400 rounded-full border border-green-800/30">
                <FileText size={10} /> Has Transcript
              </span>
            )}
            {ctx.past_meeting_count > 0 && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 bg-blue-900/30 text-blue-400 rounded-full border border-blue-800/30">
                <CalendarDays size={10} /> {ctx.past_meeting_count} Past
              </span>
            )}
            {ctx.open_items_count > 0 && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 bg-amber-900/30 text-amber-400 rounded-full border border-amber-800/30">
                <CheckSquare size={10} /> {ctx.open_items_count} Open
              </span>
            )}
          </div>
        </div>

        {/* Arrow */}
        <div className="text-slate-600 group-hover:text-memex-primary transition-colors pt-1">
          <ExternalLink size={16} />
        </div>
      </div>
    </button>
  );
}

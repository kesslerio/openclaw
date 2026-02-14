import {
  format,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  addMonths,
  addWeeks,
  addDays,
  isSameDay,
  isSameMonth,
  isToday,
  parseISO,
} from "date-fns";
import {
  ChevronLeft,
  ChevronRight,
  CalendarDays,
  Clock,
  Users,
  Video,
  ExternalLink,
  FileText,
  CheckSquare,
  X,
} from "lucide-react";
import { useState, useEffect, useMemo } from "react";
import useMemexStore from "../store/useMemexStore";

export default function CalendarView() {
  const {
    calendarViewMode,
    setCalendarViewMode,
    calendarDate,
    setCalendarDate,
    calendarEvents,
    calendarEventsLoading,
    loadCalendarRange,
    calendarSelectedDay,
    selectCalendarDay,
    openMeetingBriefing,
    loadTodayEvents,
    todayEvents,
    todayEventsLoading,
  } = useMemexStore();

  const anchor = parseISO(calendarDate);

  // Load events for visible range on mount and when anchor/viewMode changes
  useEffect(() => {
    const { start, end } = getVisibleRange(anchor, calendarViewMode);
    loadCalendarRange(format(start, "yyyy-MM-dd"), format(end, "yyyy-MM-dd"));
  }, [calendarDate, calendarViewMode]);

  // For day view, load via single-day endpoint (reuses TodayView's enriched data)
  useEffect(() => {
    if (calendarViewMode === "day") {
      loadTodayEvents(calendarDate);
    }
  }, [calendarDate, calendarViewMode]);

  const navigate = (dir) => {
    let next;
    if (calendarViewMode === "month") next = addMonths(anchor, dir);
    else if (calendarViewMode === "week") next = addWeeks(anchor, dir);
    else next = addDays(anchor, dir);
    setCalendarDate(format(next, "yyyy-MM-dd"));
    selectCalendarDay(null);
  };

  const goToday = () => {
    setCalendarDate(format(new Date(), "yyyy-MM-dd"));
    selectCalendarDay(null);
  };

  const headerLabel = useMemo(() => {
    if (calendarViewMode === "month") return format(anchor, "MMMM yyyy");
    if (calendarViewMode === "week") {
      const ws = startOfWeek(anchor, { weekStartsOn: 0 });
      const we = endOfWeek(anchor, { weekStartsOn: 0 });
      return `${format(ws, "MMM d")} – ${format(we, "MMM d, yyyy")}`;
    }
    return format(anchor, "EEEE, MMMM d, yyyy");
  }, [anchor, calendarViewMode]);

  return (
    <div className="h-full flex flex-col bg-memex-bg">
      {/* Toolbar */}
      <div className="border-b border-slate-700/50 p-4">
        <div className="flex items-center justify-between max-w-5xl mx-auto">
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <ChevronLeft size={20} />
            </button>
            <button
              onClick={() => navigate(1)}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <ChevronRight size={20} />
            </button>
            <h2 className="text-lg font-semibold ml-2">{headerLabel}</h2>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={goToday}
              className="px-3 py-1.5 text-sm border border-slate-600 rounded-lg hover:bg-slate-700 transition-colors"
            >
              Today
            </button>
            <div className="flex bg-slate-800 rounded-lg p-0.5">
              {["day", "week", "month"].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setCalendarViewMode(mode)}
                  className={`px-3 py-1.5 text-sm rounded-md capitalize transition-colors ${
                    calendarViewMode === mode
                      ? "bg-memex-primary text-white"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {calendarEventsLoading && Object.keys(calendarEvents).length === 0 ? (
          <div className="text-center py-16">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-memex-primary" />
            <p className="mt-4 text-slate-400">Loading calendar...</p>
          </div>
        ) : (
          <>
            {calendarViewMode === "month" && (
              <MonthGrid
                anchor={anchor}
                events={calendarEvents}
                selectedDay={calendarSelectedDay}
                onSelectDay={(dateStr) => {
                  selectCalendarDay(calendarSelectedDay === dateStr ? null : dateStr);
                }}
                onDayDoubleClick={(dateStr) => {
                  setCalendarDate(dateStr);
                  setCalendarViewMode("day");
                }}
              />
            )}
            {calendarViewMode === "week" && (
              <WeekGrid
                anchor={anchor}
                events={calendarEvents}
                onEventClick={openMeetingBriefing}
                onDayHeaderClick={(dateStr) => {
                  setCalendarDate(dateStr);
                  setCalendarViewMode("day");
                }}
              />
            )}
            {calendarViewMode === "day" && (
              <DayView
                date={calendarDate}
                events={todayEvents}
                loading={todayEventsLoading}
                onEventClick={openMeetingBriefing}
              />
            )}

            {/* Analysis Panel (month view) */}
            {calendarViewMode === "month" && calendarSelectedDay && (
              <AnalysisPanel
                dateStr={calendarSelectedDay}
                events={calendarEvents[calendarSelectedDay] || []}
                onClose={() => selectCalendarDay(null)}
                onEventClick={openMeetingBriefing}
                onViewFullDay={() => {
                  setCalendarDate(calendarSelectedDay);
                  setCalendarViewMode("day");
                }}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ── Helpers ────────────────────────────────────────────────────────

function getVisibleRange(anchor, mode) {
  if (mode === "month") {
    const ms = startOfMonth(anchor);
    const me = endOfMonth(anchor);
    return { start: startOfWeek(ms, { weekStartsOn: 0 }), end: endOfWeek(me, { weekStartsOn: 0 }) };
  }
  if (mode === "week") {
    return {
      start: startOfWeek(anchor, { weekStartsOn: 0 }),
      end: endOfWeek(anchor, { weekStartsOn: 0 }),
    };
  }
  return { start: anchor, end: anchor };
}

function formatTime(isoStr) {
  if (!isoStr) return "";
  return new Date(isoStr).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function getDuration(start, end) {
  if (!start || !end) return "";
  const min = Math.round((new Date(end) - new Date(start)) / 60000);
  if (min < 60) return `${min}m`;
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

const DOT_COLORS = [
  "bg-memex-primary",
  "bg-cyan-400",
  "bg-amber-400",
  "bg-purple-400",
  "bg-green-400",
];

// ── Month Grid ─────────────────────────────────────────────────────

function MonthGrid({ anchor, events, selectedDay, onSelectDay, onDayDoubleClick }) {
  const monthStart = startOfMonth(anchor);
  const monthEnd = endOfMonth(anchor);
  const gridStart = startOfWeek(monthStart, { weekStartsOn: 0 });
  const gridEnd = endOfWeek(monthEnd, { weekStartsOn: 0 });
  const days = eachDayOfInterval({ start: gridStart, end: gridEnd });

  return (
    <div className="max-w-5xl mx-auto p-4">
      {/* Day headers */}
      <div className="grid grid-cols-7 mb-1">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
          <div key={d} className="text-xs font-medium text-slate-500 text-center py-2">
            {d}
          </div>
        ))}
      </div>

      {/* Day cells */}
      <div className="grid grid-cols-7 gap-px bg-slate-700/30 rounded-lg overflow-hidden">
        {days.map((day) => {
          const dateStr = format(day, "yyyy-MM-dd");
          const dayEvents = events[dateStr] || [];
          const inMonth = isSameMonth(day, anchor);
          const today = isToday(day);
          const selected = selectedDay === dateStr;

          return (
            <button
              key={dateStr}
              onClick={() => onSelectDay(dateStr)}
              onDoubleClick={() => onDayDoubleClick(dateStr)}
              className={`
                min-h-[80px] p-2 text-left transition-colors flex flex-col
                ${inMonth ? "bg-memex-surface" : "bg-slate-900/50"}
                ${selected ? "ring-2 ring-memex-primary ring-inset" : ""}
                hover:bg-slate-800/80
              `}
            >
              <span
                className={`
                text-sm font-medium inline-flex items-center justify-center w-7 h-7 rounded-full
                ${today ? "bg-memex-primary text-white" : inMonth ? "text-slate-200" : "text-slate-600"}
              `}
              >
                {format(day, "d")}
              </span>

              {/* Event dots / compact labels */}
              <div className="mt-1 space-y-0.5 flex-1">
                {dayEvents.slice(0, 3).map((ev, i) => (
                  <div
                    key={ev.event_id || i}
                    className={`flex items-center gap-1 text-[10px] leading-tight truncate px-1 py-0.5 rounded ${DOT_COLORS[i % DOT_COLORS.length].replace("bg-", "bg-").replace("400", "900/40")} text-slate-300`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${DOT_COLORS[i % DOT_COLORS.length]}`}
                    />
                    <span className="truncate">{ev.summary}</span>
                  </div>
                ))}
                {dayEvents.length > 3 && (
                  <div className="text-[10px] text-slate-500 px-1">
                    +{dayEvents.length - 3} more
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Week Grid ──────────────────────────────────────────────────────

function WeekGrid({ anchor, events, onEventClick, onDayHeaderClick }) {
  const ws = startOfWeek(anchor, { weekStartsOn: 0 });
  const we = endOfWeek(anchor, { weekStartsOn: 0 });
  const days = eachDayOfInterval({ start: ws, end: we });

  return (
    <div className="max-w-5xl mx-auto p-4">
      <div className="grid grid-cols-7 gap-2">
        {days.map((day) => {
          const dateStr = format(day, "yyyy-MM-dd");
          const dayEvents = events[dateStr] || [];
          const today = isToday(day);

          return (
            <div key={dateStr} className="flex flex-col">
              {/* Day header */}
              <button
                onClick={() => onDayHeaderClick(dateStr)}
                className={`
                  text-center py-2 rounded-lg mb-2 transition-colors
                  ${today ? "bg-memex-primary/20 text-memex-primary" : "hover:bg-slate-800 text-slate-400"}
                `}
              >
                <div className="text-xs font-medium uppercase">{format(day, "EEE")}</div>
                <div
                  className={`text-lg font-semibold ${today ? "text-memex-primary" : "text-white"}`}
                >
                  {format(day, "d")}
                </div>
              </button>

              {/* Events */}
              <div className="space-y-1.5 flex-1">
                {dayEvents.length === 0 && (
                  <div className="text-xs text-slate-600 text-center py-4">No events</div>
                )}
                {dayEvents.map((ev, i) => (
                  <button
                    key={ev.event_id || i}
                    onClick={() => onEventClick(ev)}
                    className="w-full text-left p-2 bg-memex-surface rounded-lg border border-slate-700/50 hover:border-memex-primary/50 transition-colors"
                  >
                    <div className="text-[11px] text-slate-500">
                      {ev.all_day ? "All Day" : formatTime(ev.start)}
                    </div>
                    <div className="text-xs font-medium text-white truncate">{ev.summary}</div>
                    {(ev.attendees || []).length > 0 && (
                      <div className="text-[10px] text-slate-500 mt-0.5 flex items-center gap-0.5">
                        <Users size={9} /> {ev.attendees.length}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Day View ───────────────────────────────────────────────────────

function DayView({ date, events, loading, onEventClick }) {
  const dateDisplay = new Date(date + "T12:00:00").toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-3">
      {loading ? (
        <div className="text-center py-16">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-memex-primary" />
          <p className="mt-4 text-slate-400">Loading events...</p>
        </div>
      ) : events.length === 0 ? (
        <div className="text-center py-16">
          <CalendarDays size={48} className="mx-auto text-slate-600 mb-4" />
          <h3 className="text-lg font-medium text-slate-400">No events scheduled</h3>
          <p className="text-sm text-slate-500 mt-1">No events on this day.</p>
        </div>
      ) : (
        events.map((event, idx) => (
          <EventCard
            key={event.event_id || idx}
            event={event}
            onClick={() => onEventClick(event)}
          />
        ))
      )}
    </div>
  );
}

// ── Event Card (reused from TodayView pattern) ────────────────────

function EventCard({ event, onClick }) {
  const ctx = event.context || {};
  const attendeeCount = (event.attendees || []).length;
  const meetLink = event.meet_link || event.hangout_link;

  return (
    <button
      onClick={onClick}
      className="w-full text-left p-4 bg-memex-surface rounded-xl border border-slate-700/50 hover:border-memex-primary/50 hover:bg-slate-800/80 transition-all duration-200 group"
    >
      <div className="flex items-start gap-4">
        {/* Time Column */}
        <div className="w-20 flex-shrink-0 pt-0.5">
          {event.all_day ? (
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
            {!event.all_day && (
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

// ── Analysis Panel (slides in under month grid) ───────────────────

function AnalysisPanel({ dateStr, events, onClose, onEventClick, onViewFullDay }) {
  const dateDisplay = new Date(dateStr + "T12:00:00").toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="border-t border-slate-700/50 bg-slate-900/50">
      <div className="max-w-5xl mx-auto p-4">
        {/* Panel Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <CalendarDays size={18} className="text-memex-primary" />
            <h3 className="font-semibold text-white">{dateDisplay}</h3>
            <span className="text-xs text-slate-500">
              {events.length} event{events.length !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={onViewFullDay} className="text-xs text-memex-primary hover:underline">
              View full day
            </button>
            <button onClick={onClose} className="p-1 hover:bg-slate-700 rounded transition-colors">
              <X size={16} className="text-slate-400" />
            </button>
          </div>
        </div>

        {/* Event list */}
        {events.length === 0 ? (
          <p className="text-sm text-slate-500 py-4 text-center">No events on this day.</p>
        ) : (
          <div className="space-y-2">
            {events.map((ev, i) => (
              <EventCard key={ev.event_id || i} event={ev} onClick={() => onEventClick(ev)} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

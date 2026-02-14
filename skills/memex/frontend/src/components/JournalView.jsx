import { format, subDays, addDays } from "date-fns";
import { ChevronLeft, ChevronRight, Calendar } from "lucide-react";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import useMemexStore from "../store/useMemexStore";

export default function JournalView() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedJournal, setSelectedJournal] = useState(null);
  const [loading, setLoading] = useState(false);

  const { journals, loadJournals } = useMemexStore();

  useEffect(() => {
    loadJournalsForMonth();
  }, [currentDate]);

  const loadJournalsForMonth = async () => {
    setLoading(true);
    const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

    await loadJournals(format(startOfMonth, "yyyy-MM-dd"), format(endOfMonth, "yyyy-MM-dd"));
    setLoading(false);
  };

  const goToPrevDay = () => {
    setCurrentDate(subDays(currentDate, 1));
    setSelectedJournal(null);
  };

  const goToNextDay = () => {
    setCurrentDate(addDays(currentDate, 1));
    setSelectedJournal(null);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedJournal(null);
  };

  // Find journal for current date
  useEffect(() => {
    const dateStr = format(currentDate, "yyyy-MM-dd");
    const journal = journals.find((j) => j.date === dateStr);
    setSelectedJournal(journal || null);
  }, [currentDate, journals]);

  return (
    <div className="h-full flex">
      {/* Calendar Sidebar */}
      <div className="w-80 border-r border-slate-700/50 flex flex-col">
        <div className="p-4 border-b border-slate-700/50">
          <h3 className="font-semibold text-lg mb-3">Journal Calendar</h3>

          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-medium text-slate-300">
              {format(currentDate, "MMMM yyyy")}
            </h4>
            <button
              onClick={goToToday}
              className="text-xs text-memex-secondary hover:text-cyan-400"
            >
              Today
            </button>
          </div>

          <MiniCalendar
            currentDate={currentDate}
            journals={journals}
            onDateSelect={setCurrentDate}
          />
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <h4 className="text-sm font-medium text-slate-400 mb-3">Recent Journals</h4>
          {journals.length === 0 ? (
            <p className="text-sm text-slate-500 italic">No journals yet</p>
          ) : (
            <div className="space-y-2">
              {journals.slice(0, 10).map((journal) => (
                <button
                  key={journal.date}
                  onClick={() => {
                    setCurrentDate(new Date(journal.date));
                    setSelectedJournal(journal);
                  }}
                  className={`
                    w-full text-left px-3 py-2 rounded-lg transition-colors
                    ${
                      selectedJournal?.date === journal.date
                        ? "bg-memex-primary text-white"
                        : "bg-slate-800/50 hover:bg-slate-700 text-slate-300"
                    }
                  `}
                >
                  <div className="text-sm font-medium">
                    {format(new Date(journal.date), "MMM d, yyyy")}
                  </div>
                  <div className="text-xs opacity-75 mt-1">
                    {journal.action_items?.length || 0} action items
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Journal Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-slate-700/50 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={goToPrevDay}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <ChevronLeft size={20} />
            </button>

            <div className="flex items-center gap-2">
              <Calendar className="text-memex-primary" size={20} />
              <h2 className="text-xl font-semibold">{format(currentDate, "EEEE, MMMM d, yyyy")}</h2>
            </div>

            <button
              onClick={goToNextDay}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              disabled={format(currentDate, "yyyy-MM-dd") === format(new Date(), "yyyy-MM-dd")}
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>

        {/* Journal Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-memex-primary"></div>
                <p className="mt-4 text-slate-400">Loading journals...</p>
              </div>
            </div>
          ) : selectedJournal ? (
            <div className="max-w-4xl mx-auto">
              <div className="prose prose-lg prose-invert">
                <ReactMarkdown>{selectedJournal.content}</ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-center">
              <div>
                <div className="text-6xl mb-4">📝</div>
                <h3 className="text-xl font-semibold mb-2">No journal for this day</h3>
                <p className="text-slate-400">
                  Journals are generated automatically from your transcripts.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MiniCalendar({ currentDate, journals, onDateSelect }) {
  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();

  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();

  const journalDates = new Set(journals.map((j) => j.date));

  return (
    <div className="grid grid-cols-7 gap-1">
      {["S", "M", "T", "W", "T", "F", "S"].map((day, i) => (
        <div key={i} className="text-xs font-medium text-slate-500 text-center py-1">
          {day}
        </div>
      ))}

      {Array.from({ length: firstDayOfMonth }).map((_, i) => (
        <div key={`empty-${i}`} />
      ))}

      {Array.from({ length: daysInMonth }).map((_, i) => {
        const day = i + 1;
        const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
        const dateStr = format(date, "yyyy-MM-dd");
        const hasJournal = journalDates.has(dateStr);
        const isSelected = format(currentDate, "yyyy-MM-dd") === dateStr;
        const isToday = format(new Date(), "yyyy-MM-dd") === dateStr;

        return (
          <button
            key={day}
            onClick={() => onDateSelect(date)}
            className={`
              aspect-square flex items-center justify-center text-sm rounded-lg transition-all
              ${
                isSelected
                  ? "bg-memex-primary text-white font-semibold"
                  : isToday
                    ? "border-2 border-memex-primary text-memex-primary"
                    : hasJournal
                      ? "bg-slate-700 text-white hover:bg-slate-600"
                      : "text-slate-500 hover:bg-slate-800"
              }
            `}
          >
            {day}
          </button>
        );
      })}
    </div>
  );
}

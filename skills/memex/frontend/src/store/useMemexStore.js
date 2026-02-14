import { create } from "zustand";

const useMemexStore = create((set, get) => ({
  // Chat state
  messages: [],
  isTyping: false,

  // Journal state
  journals: [],
  selectedDate: null,

  // Search state
  searchResults: [],
  searchQuery: "",
  isSearching: false,

  // Navigation
  activeView: "today",
  setActiveView: (view) => set({ activeView: view }),

  // Transcript detail
  selectedTranscriptId: null,
  setSelectedTranscriptId: (id) => set({ selectedTranscriptId: id }),

  // Plaud sync state
  syncStatus: "idle", // idle | running | done | error
  syncResult: null, // string message shown after sync

  // Today's Schedule state
  todayEvents: [],
  todayEventsLoading: false,
  todayDate: new Date().toISOString().split("T")[0],

  // Meeting Briefing state
  selectedEvent: null,
  briefingData: null,
  briefingLoading: false,

  // Integration status
  integrationStatus: null,

  // Calendar view state
  calendarViewMode: "month", // 'day' | 'week' | 'month'
  calendarDate: new Date().toISOString().split("T")[0], // anchor date YYYY-MM-DD
  calendarEvents: {}, // { 'YYYY-MM-DD': [events] }
  calendarEventsLoading: false,
  calendarSelectedDay: null, // YYYY-MM-DD for analysis panel

  setCalendarViewMode: (mode) => set({ calendarViewMode: mode }),
  setCalendarDate: (date) => set({ calendarDate: date }),
  selectCalendarDay: (date) => set({ calendarSelectedDay: date }),

  async loadCalendarRange(start, end) {
    set({ calendarEventsLoading: true });
    try {
      const params = new URLSearchParams({ start, end });
      const response = await fetch(`/api/today/events/range?${params}`);
      if (!response.ok) throw new Error("Failed to load calendar range");
      const data = await response.json();
      // Merge into existing cache so navigating back doesn't re-fetch
      set((state) => ({
        calendarEvents: { ...state.calendarEvents, ...(data.events_by_date || {}) },
        calendarEventsLoading: false,
      }));
    } catch (error) {
      console.error("Failed to load calendar range:", error);
      set({ calendarEventsLoading: false });
    }
  },

  // Email compose
  emailComposeOpen: false,
  emailComposeDefaults: null,

  async startPlaudSync() {
    if (get().syncStatus === "running") return;

    set({ syncStatus: "running", syncResult: null });

    try {
      // Kick off sync
      const res = await fetch("/api/sync", { method: "POST" });
      if (!res.ok) throw new Error("Failed to start sync");
      const data = await res.json();

      if (data.status === "already_running") {
        set({ syncResult: "Sync already in progress..." });
      }

      // Poll for completion
      let attempts = 0;
      const maxAttempts = 600; // 10 minutes max (1s intervals)
      while (attempts < maxAttempts) {
        await new Promise((r) => setTimeout(r, 2000));
        attempts++;

        const statusRes = await fetch("/api/sync/status");
        if (!statusRes.ok) continue;
        const status = await statusRes.json();

        if (!status.running) {
          const result = status.last_result || {};
          if (result.error) {
            set({
              syncStatus: "error",
              syncResult: `Error: ${result.error}`,
            });
          } else {
            const exported = result.export?.exported || 0;
            const indexed = result.index?.new || 0;
            const chunks = result.index?.chunks || 0;
            set({
              syncStatus: "done",
              syncResult:
                exported > 0 || indexed > 0
                  ? `${exported} new transcripts downloaded, ${indexed} indexed (${chunks} chunks)`
                  : "Already up to date",
            });
          }
          // Reset to idle after 15 seconds
          setTimeout(() => {
            if (get().syncStatus !== "running") {
              set({ syncStatus: "idle" });
            }
          }, 15000);
          return;
        }
      }

      // Timed out
      set({ syncStatus: "error", syncResult: "Sync timed out" });
    } catch (err) {
      set({ syncStatus: "error", syncResult: `Error: ${err.message}` });
      setTimeout(() => {
        if (get().syncStatus !== "running") {
          set({ syncStatus: "idle" });
        }
      }, 15000);
    }
  },

  // Actions
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, { ...message, id: Date.now() }],
    })),

  setTyping: (isTyping) => set({ isTyping }),

  setJournals: (journals) => set({ journals }),

  setSelectedDate: (date) => set({ selectedDate: date }),

  setSearchResults: (results) => set({ searchResults: results }),

  setSearchQuery: (query) => set({ searchQuery: query }),

  setSearching: (isSearching) => set({ isSearching }),

  clearChat: () => set({ messages: [] }),

  // Today's Schedule actions
  async loadTodayEvents(date) {
    set({ todayEventsLoading: true });
    if (date) set({ todayDate: date });

    try {
      const params = new URLSearchParams();
      if (date) params.append("date", date);
      const response = await fetch(`/api/today/events?${params}`);
      if (!response.ok) throw new Error("Failed to load events");
      const data = await response.json();
      set({ todayEvents: data.events || [], todayEventsLoading: false });
    } catch (error) {
      console.error("Failed to load today events:", error);
      set({ todayEvents: [], todayEventsLoading: false });
    }
  },

  openMeetingBriefing(event) {
    set({
      selectedEvent: event,
      briefingData: null,
      activeView: "meeting-briefing",
    });
    // Auto-load briefing data
    get().loadBriefingData(event);
  },

  async loadBriefingData(event) {
    const ev = event || get().selectedEvent;
    if (!ev) return;

    set({ briefingLoading: true });

    try {
      // Build attendees param: Name:email,...
      const attendees = (ev.attendees || [])
        .filter((a) => a.email)
        .map((a) => `${a.name || a.email.split("@")[0]}:${a.email}`)
        .join(",");

      if (!attendees) {
        set({
          briefingData: {
            briefing: {
              attendees: [],
              matching_meetings: [],
              total_past_meetings: 0,
              unresolved_action_items: [],
              key_decisions: [],
            },
            emails: [],
          },
          briefingLoading: false,
        });
        return;
      }

      const params = new URLSearchParams({ attendees });
      if (ev.summary) params.append("summary", ev.summary);
      const response = await fetch(`/api/today/briefing/${ev.event_id}?${params}`);
      if (!response.ok) throw new Error("Failed to load briefing");
      const data = await response.json();
      set({ briefingData: data, briefingLoading: false });
    } catch (error) {
      console.error("Failed to load briefing:", error);
      set({ briefingData: null, briefingLoading: false });
    }
  },

  async loadIntegrationStatus() {
    try {
      const response = await fetch("/api/integrations/status");
      if (!response.ok) throw new Error("Failed to load status");
      const data = await response.json();
      set({ integrationStatus: data });
    } catch (error) {
      console.error("Failed to load integration status:", error);
    }
  },

  openEmailCompose(to, subject) {
    set({
      emailComposeOpen: true,
      emailComposeDefaults: { to: to || [], subject: subject || "" },
    });
  },

  closeEmailCompose() {
    set({ emailComposeOpen: false, emailComposeDefaults: null });
  },

  // API helpers
  async sendMessage(text) {
    const userMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    get().addMessage(userMessage);
    set({ isTyping: true });

    try {
      const response = await fetch("/api/chat/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) throw new Error("Query failed");

      const data = await response.json();

      const assistantMessage = {
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        confidence: data.confidence,
        timestamp: new Date().toISOString(),
      };

      get().addMessage(assistantMessage);
    } catch (error) {
      const errorMessage = {
        role: "assistant",
        content: `Sorry, I encountered an error: ${error.message}`,
        error: true,
        timestamp: new Date().toISOString(),
      };

      get().addMessage(errorMessage);
    } finally {
      set({ isTyping: false });
    }
  },

  async loadJournals(startDate, endDate) {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);

      const response = await fetch(`/api/journals?${params}`);

      if (!response.ok) throw new Error("Failed to load journals");

      const data = await response.json();
      set({ journals: data.journals || [] });
    } catch (error) {
      console.error("Failed to load journals:", error);
    }
  },

  async performSearch(query) {
    if (!query.trim()) return;

    set({ isSearching: true, searchQuery: query });

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 10 }),
      });

      if (!response.ok) throw new Error("Search failed");

      const data = await response.json();
      set({ searchResults: data.results || [] });
    } catch (error) {
      console.error("Search failed:", error);
      set({ searchResults: [] });
    } finally {
      set({ isSearching: false });
    }
  },
}));

export default useMemexStore;

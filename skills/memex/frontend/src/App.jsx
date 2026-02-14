import { useState } from "react";
import ActionItemsDashboard from "./components/ActionItemsDashboard";
import CalendarView from "./components/CalendarView";
import ChatInterface from "./components/ChatInterface";
import DecisionLog from "./components/DecisionLog";
import EmailComposeModal from "./components/EmailComposeModal";
import Header from "./components/Header";
import JournalView from "./components/JournalView";
import MeetingBriefing from "./components/MeetingBriefing";
import MeetingsView from "./components/MeetingsView";
import SearchBar from "./components/SearchBar";
import Sidebar from "./components/Sidebar";
import TodayView from "./components/TodayView";
import TranscriptDetail from "./components/TranscriptDetail";
import useMemexStore from "./store/useMemexStore";

function App() {
  const { activeView, setActiveView } = useMemexStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      {sidebarOpen && (
        <Sidebar
          activeView={activeView}
          onViewChange={setActiveView}
          onClose={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          activeView={activeView}
        />

        {/* Content Area */}
        <main className="flex-1 overflow-hidden">
          {activeView === "today" && <TodayView />}
          {activeView === "calendar" && <CalendarView />}
          {activeView === "meeting-briefing" && <MeetingBriefing />}
          {activeView === "chat" && <ChatInterface />}
          {activeView === "journals" && <JournalView />}
          {activeView === "meetings" && <MeetingsView />}
          {activeView === "transcript-detail" && <TranscriptDetail />}
          {activeView === "action-items" && <ActionItemsDashboard />}
          {activeView === "decisions" && <DecisionLog />}
          {activeView === "search" && (
            <div className="h-full flex flex-col p-6">
              <SearchBar />
            </div>
          )}
        </main>
      </div>

      {/* Modals */}
      <EmailComposeModal />
    </div>
  );
}

export default App;

import { Plus, RefreshCw } from "lucide-react";
import React, { useState, useMemo } from "react";
import Board from "./components/Board";
import FilterBar from "./components/FilterBar";
import MissionControl from "./components/MissionControl";
import OpsPanel from "./components/OpsPanel";
import Sidebar from "./components/Sidebar";
import TaskModal from "./components/TaskModal";
import { useKanban } from "./hooks/useKanban";
import { useStatus } from "./hooks/useStatus";

export default function App() {
  const { data, loading, error, refresh, addTask, editTask, removeTask, changeStatus } =
    useKanban();

  const { status } = useStatus(30000);

  const [activeView, setActiveView] = useState("board");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const [filters, setFilters] = useState({
    priority: null,
    category: null,
    tag: null,
    search: "",
  });

  const [modalState, setModalState] = useState({
    open: false,
    task: null,
    defaultStatus: "backlog",
  });

  // Collect all unique tags from tasks
  const allTags = useMemo(() => {
    if (!data?.tasks) return [];
    const tags = new Set();
    data.tasks.forEach((t) => {
      if (t.tags) t.tags.forEach((tag) => tags.add(tag));
    });
    return Array.from(tags).sort();
  }, [data]);

  // Handle drag and drop
  const handleDragEnd = async (result) => {
    const { destination, source, draggableId } = result;
    if (!destination) return;
    if (destination.droppableId === source.droppableId && destination.index === source.index)
      return;
    await changeStatus(draggableId, destination.droppableId);
  };

  // Modal handlers
  const openAddModal = (status = "backlog") => {
    setModalState({ open: true, task: null, defaultStatus: status });
  };

  const openEditModal = (task) => {
    setModalState({ open: true, task, defaultStatus: task.status });
  };

  const closeModal = () => {
    setModalState({ open: false, task: null, defaultStatus: "backlog" });
  };

  const handleSaveTask = async (taskData) => {
    if (modalState.task) {
      await editTask(modalState.task.id, taskData);
    } else {
      await addTask({ ...taskData, status: modalState.defaultStatus });
    }
    closeModal();
  };

  const handleDeleteTask = async (taskId) => {
    if (confirm("Delete this task?")) {
      await removeTask(taskId);
    }
  };

  const handleMoveTask = async (taskId, newStatus) => {
    await changeStatus(taskId, newStatus);
  };

  if (loading && !data) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const gatewayAlive = status?.gateway?.alive;
  const taskCount = data?.tasks?.length || 0;

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onNavigate={setActiveView}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        taskCount={taskCount}
        gatewayAlive={gatewayAlive}
      />

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {activeView === "board" && (
          <>
            {/* Board header: filters + actions */}
            <div className="flex items-center gap-3 px-4 py-2.5 border-b border-gray-800 bg-gray-900 flex-shrink-0">
              <FilterBar filters={filters} onFilterChange={setFilters} tags={allTags} />
              <div className="flex items-center gap-2 flex-shrink-0 ml-auto">
                <button
                  onClick={refresh}
                  className="p-1.5 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
                  title="Refresh"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
                <button
                  onClick={() => openAddModal()}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Create
                </button>
              </div>
            </div>

            {/* Error display */}
            {error && (
              <div className="mx-4 mt-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm flex-shrink-0">
                Error: {error}
              </div>
            )}

            {/* Board */}
            <Board
              data={data}
              onDragEnd={handleDragEnd}
              onEdit={openEditModal}
              onDelete={handleDeleteTask}
              onMove={handleMoveTask}
              onAddTask={openAddModal}
              filters={filters}
            />
          </>
        )}

        {activeView === "mission" && (
          <div className="flex-1 overflow-y-auto p-6">
            <MissionControl />
          </div>
        )}

        {activeView === "ops" && (
          <div className="flex-1 overflow-y-auto p-6">
            <OpsPanel />
          </div>
        )}
      </main>

      {/* Task Modal */}
      {modalState.open && (
        <TaskModal
          task={modalState.task}
          defaultStatus={modalState.defaultStatus}
          onSave={handleSaveTask}
          onClose={closeModal}
        />
      )}
    </div>
  );
}

import { Calendar, MoreVertical, Edit, Trash2, AlertCircle } from "lucide-react";
import React from "react";

const priorityBorderColors = {
  high: "border-l-red-500",
  medium: "border-l-amber-500",
  low: "border-l-green-500",
};

const categoryConfig = {
  Work: "category-work",
  Personal: "category-personal",
  CopperAI: "category-copperai",
  General: "category-general",
};

export default function TaskCard({ task, onEdit, onDelete, onMove, provided, isDragging }) {
  const borderColor = priorityBorderColors[task.priority] || priorityBorderColors.medium;
  const categoryClass = categoryConfig[task.category] || categoryConfig.General;

  const getDueDateStatus = () => {
    if (!task.dueDate) return null;
    const due = new Date(task.dueDate);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const dueDay = new Date(due.getFullYear(), due.getMonth(), due.getDate());
    if (dueDay < today) return "overdue";
    if (dueDay.getTime() === today.getTime()) return "today";
    return "upcoming";
  };

  const dueDateStatus = getDueDateStatus();

  const formatDueDate = (dateStr) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  const [showMenu, setShowMenu] = React.useState(false);

  return (
    <div
      ref={provided?.innerRef}
      {...provided?.draggableProps}
      {...provided?.dragHandleProps}
      onClick={() => onEdit?.(task)}
      className={`
        group bg-gray-850 rounded border-l-2 ${borderColor} border border-gray-800
        px-2.5 py-2 mb-1.5 cursor-pointer
        hover:bg-gray-800 hover:border-gray-700 transition-all
        ${isDragging ? "task-card-dragging" : ""}
      `}
    >
      {/* Title + menu */}
      <div className="flex items-start justify-between gap-1">
        <h3 className="text-sm font-medium text-gray-200 line-clamp-2 flex-1">{task.title}</h3>

        {/* 3-dot menu, visible on hover */}
        <div className="relative flex-shrink-0">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            className="p-0.5 rounded transition-colors opacity-0 group-hover:opacity-100
                       hover:bg-gray-700 text-gray-500 hover:text-gray-300"
          >
            <MoreVertical className="w-3.5 h-3.5" />
          </button>

          {showMenu && (
            <div className="absolute right-0 top-6 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 py-1 min-w-[100px]">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit?.(task);
                  setShowMenu(false);
                }}
                className="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-gray-800 transition-colors"
              >
                <Edit className="w-3 h-3" />
                Edit
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete?.(task.id);
                  setShowMenu(false);
                }}
                className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-red-400 hover:bg-gray-800 transition-colors"
              >
                <Trash2 className="w-3 h-3" />
                Delete
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Metadata chips */}
      <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
        <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${categoryClass}`}>
          {task.category}
        </span>

        {task.dueDate && (
          <span
            className={`
            flex items-center gap-0.5 text-[10px]
            ${dueDateStatus === "overdue" ? "due-overdue" : ""}
            ${dueDateStatus === "today" ? "due-today" : ""}
            ${dueDateStatus === "upcoming" ? "due-upcoming" : ""}
          `}
          >
            {dueDateStatus === "overdue" && <AlertCircle className="w-2.5 h-2.5" />}
            <Calendar className="w-2.5 h-2.5" />
            {formatDueDate(task.dueDate)}
          </span>
        )}

        {task.tags && task.tags.length > 0 && (
          <>
            {task.tags.slice(0, 2).map((tag) => (
              <span key={tag} className="tag bg-gray-700/60 text-gray-400">
                {tag}
              </span>
            ))}
            {task.tags.length > 2 && (
              <span className="text-[10px] text-gray-600">+{task.tags.length - 2}</span>
            )}
          </>
        )}
      </div>
    </div>
  );
}

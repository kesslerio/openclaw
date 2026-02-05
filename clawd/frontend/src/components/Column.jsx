import { Droppable, Draggable } from "@hello-pangea/dnd";
import { Plus } from "lucide-react";
import React from "react";
import TaskCard from "./TaskCard";

const columnDotColors = {
  backlog: "bg-gray-500",
  todo: "bg-blue-500",
  doing: "bg-amber-500",
  done: "bg-green-500",
};

export default function Column({ column, tasks, onEdit, onDelete, onMove, onAddTask, isLast }) {
  const dotColor = columnDotColors[column.id] || columnDotColors.backlog;

  return (
    <div className={`flex flex-col flex-1 min-w-0 ${!isLast ? "border-r border-gray-800" : ""}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2.5 flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full ${dotColor}`} />
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            {column.title}
          </h2>
          <span className="text-xs text-gray-600 font-mono">{tasks.length}</span>
        </div>

        {column.id !== "done" && (
          <button
            onClick={() => onAddTask?.(column.id)}
            className="p-0.5 hover:bg-gray-800 rounded transition-colors text-gray-600 hover:text-gray-400"
            title="Add task"
          >
            <Plus className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Droppable Area */}
      <Droppable droppableId={column.id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`
              flex-1 overflow-y-auto px-2 pb-2 transition-colors
              ${snapshot.isDraggingOver ? "bg-blue-500/5" : ""}
            `}
          >
            {tasks.map((task, index) => (
              <Draggable key={task.id} draggableId={task.id} index={index}>
                {(provided, snapshot) => (
                  <TaskCard
                    task={task}
                    onEdit={onEdit}
                    onDelete={onDelete}
                    onMove={onMove}
                    provided={provided}
                    isDragging={snapshot.isDragging}
                  />
                )}
              </Draggable>
            ))}
            {provided.placeholder}

            {tasks.length === 0 && !snapshot.isDraggingOver && (
              <div className="text-center text-gray-700 py-8">
                <p className="text-xs">No tasks</p>
              </div>
            )}
          </div>
        )}
      </Droppable>
    </div>
  );
}

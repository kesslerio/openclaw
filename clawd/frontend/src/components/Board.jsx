import { DragDropContext } from "@hello-pangea/dnd";
import React from "react";
import Column from "./Column";

const COLUMN_ORDER = ["backlog", "todo", "doing", "done"];

export default function Board({ data, onDragEnd, onEdit, onDelete, onMove, onAddTask, filters }) {
  if (!data) return null;

  // Apply filters to tasks
  const filterTasks = (tasks) => {
    let filtered = [...tasks];

    if (filters.priority) {
      filtered = filtered.filter((t) => t.priority === filters.priority);
    }

    if (filters.category) {
      filtered = filtered.filter((t) => t.category === filters.category);
    }

    if (filters.tag) {
      filtered = filtered.filter((t) => t.tags && t.tags.includes(filters.tag));
    }

    if (filters.search) {
      const search = filters.search.toLowerCase();
      filtered = filtered.filter(
        (t) =>
          t.title.toLowerCase().includes(search) ||
          (t.description && t.description.toLowerCase().includes(search)),
      );
    }

    // Sort by priority then due date
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    filtered.sort((a, b) => {
      const pDiff = (priorityOrder[a.priority] || 1) - (priorityOrder[b.priority] || 1);
      if (pDiff !== 0) return pDiff;

      if (a.dueDate && b.dueDate) {
        return new Date(a.dueDate) - new Date(b.dueDate);
      }
      return a.dueDate ? -1 : 1;
    });

    return filtered;
  };

  const getColumnTasks = (columnId) => {
    const column = data.columns[columnId];
    if (!column) return [];

    const columnTasks = column.tasks
      .map((taskId) => data.tasks.find((t) => t.id === taskId))
      .filter(Boolean);

    return filterTasks(columnTasks);
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="flex flex-1 overflow-hidden">
        {COLUMN_ORDER.map((columnId, idx) => {
          const column = data.columns[columnId];
          if (!column) return null;

          return (
            <Column
              key={columnId}
              column={column}
              tasks={getColumnTasks(columnId)}
              onEdit={onEdit}
              onDelete={onDelete}
              onMove={onMove}
              onAddTask={onAddTask}
              isLast={idx === COLUMN_ORDER.length - 1}
            />
          );
        })}
      </div>
    </DragDropContext>
  );
}

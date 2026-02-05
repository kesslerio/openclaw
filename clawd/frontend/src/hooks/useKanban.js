import { useState, useEffect, useCallback } from "react";
import { fetchKanban, createTask, updateTask, deleteTask, moveTask } from "../utils/api";

export function useKanban() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const kanban = await fetchKanban();
      setData(kanban);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const addTask = async (task) => {
    try {
      const newTask = await createTask(task);
      await loadData();
      return newTask;
    } catch (e) {
      setError(e.message);
      throw e;
    }
  };

  const editTask = async (id, updates) => {
    try {
      const updated = await updateTask(id, updates);
      await loadData();
      return updated;
    } catch (e) {
      setError(e.message);
      throw e;
    }
  };

  const removeTask = async (id) => {
    try {
      await deleteTask(id);
      await loadData();
    } catch (e) {
      setError(e.message);
      throw e;
    }
  };

  const changeStatus = async (id, newStatus) => {
    try {
      await moveTask(id, newStatus);
      await loadData();
    } catch (e) {
      setError(e.message);
      throw e;
    }
  };

  // Get tasks for a specific column
  const getColumnTasks = (columnId) => {
    if (!data) return [];
    const column = data.columns[columnId];
    if (!column) return [];

    return column.tasks.map((taskId) => data.tasks.find((t) => t.id === taskId)).filter(Boolean);
  };

  return {
    data,
    loading,
    error,
    refresh: loadData,
    addTask,
    editTask,
    removeTask,
    changeStatus,
    getColumnTasks,
  };
}

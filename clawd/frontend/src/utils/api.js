/**
 * API Client for Kanban Backend
 *
 * Adapts the raw kanban.json format (status: ready/in_progress/done/blocked,
 * priority: HIGH/MEDIUM/LOW, columns: TODO/DOING/DONE/BLOCKED) to the
 * frontend's expected model (status: backlog/todo/doing/done, priority:
 * high/medium/low, columns keyed the same).
 */

const API_BASE = "/api";

// ── Status / priority mapping ──────────────────────────────────────

const STATUS_TO_FRONTEND = {
  ready: "todo",
  in_progress: "doing",
  done: "done",
  blocked: "backlog",
};

const STATUS_TO_BACKEND = {
  backlog: "blocked",
  todo: "ready",
  doing: "in_progress",
  done: "done",
};

const COLUMN_TO_FRONTEND = {
  TODO: "todo",
  DOING: "doing",
  DONE: "done",
  BLOCKED: "backlog",
};

const COLUMN_TITLES = {
  backlog: "Backlog",
  todo: "Todo",
  doing: "Doing",
  done: "Done",
};

function mapPriorityDown(p) {
  return (p || "MEDIUM").toLowerCase();
}

function mapPriorityUp(p) {
  return (p || "medium").toUpperCase();
}

function mapCategoryDown(c) {
  // Capitalize first letter for display
  if (!c) return "General";
  const map = { revenue: "Work", personal: "Personal", technical: "CopperAI", admin: "General" };
  return map[c.toLowerCase()] || c.charAt(0).toUpperCase() + c.slice(1);
}

function mapCategoryUp(c) {
  const map = { Work: "revenue", Personal: "personal", CopperAI: "technical", General: "admin" };
  return map[c] || c.toLowerCase();
}

// Transform a raw task from kanban.json into frontend shape
function transformTask(raw) {
  return {
    id: raw.id,
    title: raw.title || "",
    description: raw.description || "",
    status: STATUS_TO_FRONTEND[raw.status] || "backlog",
    priority: mapPriorityDown(raw.priority),
    dueDate: raw.dueDate || null,
    tags: raw.tags || [],
    category: mapCategoryDown(raw.category),
    analysis: raw.steps
      ? {
          automationType:
            raw.canNikeComplete === false ? "human" : raw.blockers ? "blocked" : "hybrid",
          automationReason:
            raw.blockers || (raw.canNikeComplete === false ? "Requires human action" : ""),
          isBlocked: !!raw.blockers,
          blockageReason: raw.blockers || null,
          steps: (raw.steps || []).map((s) => (typeof s === "string" ? s : s.text)),
          aiCapabilities: [],
          humanRequirements: [],
          estimatedMinutes: raw.estimatedMinutes || null,
        }
      : null,
  };
}

// ── Fetch kanban board ─────────────────────────────────────────────

export async function fetchKanban() {
  const res = await fetch("/kanban.json");
  if (!res.ok) throw new Error("Failed to fetch kanban data");
  const raw = await res.json();

  // Transform tasks
  const tasks = (raw.tasks || []).map(transformTask);

  // Build column map from raw.columns (TODO/DOING/DONE/BLOCKED → arrays of task IDs)
  const columns = {};
  const COLUMN_ORDER = ["backlog", "todo", "doing", "done"];

  // Initialize columns
  for (const col of COLUMN_ORDER) {
    columns[col] = { id: col, title: COLUMN_TITLES[col], tasks: [] };
  }

  // Map raw columns to frontend columns
  for (const [rawCol, taskIds] of Object.entries(raw.columns || {})) {
    const frontendCol = COLUMN_TO_FRONTEND[rawCol];
    if (frontendCol && columns[frontendCol]) {
      columns[frontendCol].tasks = taskIds || [];
    }
  }

  // Ensure any tasks not in a column get placed by their status
  const allColumnTaskIds = new Set(Object.values(columns).flatMap((c) => c.tasks));
  for (const task of tasks) {
    if (!allColumnTaskIds.has(task.id)) {
      const col = columns[task.status] || columns.backlog;
      col.tasks.push(task.id);
    }
  }

  return { tasks, columns };
}

// ── Fetch filtered tasks ───────────────────────────────────────────

export async function fetchTasks(filters = {}) {
  const data = await fetchKanban();
  return data.tasks;
}

// ── Create task ────────────────────────────────────────────────────

export async function createTask(task) {
  // Read current kanban.json, add task, write back
  const res = await fetch("/kanban.json");
  if (!res.ok) throw new Error("Failed to read kanban data");
  const raw = await res.json();

  const id = "task-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8);
  const backendStatus = STATUS_TO_BACKEND[task.status] || "ready";

  const newRawTask = {
    id,
    title: task.title,
    description: task.description || "",
    owner: "",
    priority: mapPriorityUp(task.priority),
    urgent: task.priority === "high",
    tags: task.tags || [],
    created: new Date().toISOString().split("T")[0],
    estimatedTokens: 0,
    canNikeComplete: true,
    blockers: null,
    status: backendStatus,
    category: mapCategoryUp(task.category),
    estimatedMinutes: 0,
    dueDate: task.dueDate || null,
    dependencies: [],
    steps: [],
  };

  raw.tasks.push(newRawTask);

  // Add to appropriate column
  const rawCol =
    Object.entries(COLUMN_TO_FRONTEND).find(([, v]) => v === task.status)?.[0] || "TODO";
  if (!raw.columns[rawCol]) raw.columns[rawCol] = [];
  raw.columns[rawCol].push(id);

  // Write back via /update endpoint (writes kanban-data.json)
  // Instead, write to kanban.json by POSTing the entire structure
  const writeRes = await fetch("/kanban.json", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(raw),
  });

  // Fallback: if the server doesn't accept POST to /kanban.json,
  // try the /api/tasks endpoint
  if (!writeRes.ok) {
    const fallbackRes = await fetch(`${API_BASE}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newRawTask),
    });
    if (!fallbackRes.ok) throw new Error("Failed to create task");
  }

  return transformTask(newRawTask);
}

// ── Update task ────────────────────────────────────────────────────

export async function updateTask(id, updates) {
  const res = await fetch("/kanban.json");
  if (!res.ok) throw new Error("Failed to read kanban data");
  const raw = await res.json();

  const idx = raw.tasks.findIndex((t) => t.id === id);
  if (idx === -1) throw new Error("Task not found");

  const task = raw.tasks[idx];

  // Apply updates
  if (updates.title !== undefined) task.title = updates.title;
  if (updates.description !== undefined) task.description = updates.description;
  if (updates.priority !== undefined) task.priority = mapPriorityUp(updates.priority);
  if (updates.category !== undefined) task.category = mapCategoryUp(updates.category);
  if (updates.dueDate !== undefined) task.dueDate = updates.dueDate;
  if (updates.tags !== undefined) task.tags = updates.tags;

  if (updates.status !== undefined) {
    const oldStatus = task.status;
    const newStatus = STATUS_TO_BACKEND[updates.status] || updates.status;
    task.status = newStatus;

    // Move between columns
    const oldCol = Object.entries(COLUMN_TO_FRONTEND).find(
      ([, v]) => v === (STATUS_TO_FRONTEND[oldStatus] || "backlog"),
    )?.[0];
    const newCol = Object.entries(COLUMN_TO_FRONTEND).find(([, v]) => v === updates.status)?.[0];

    if (oldCol && raw.columns[oldCol]) {
      raw.columns[oldCol] = raw.columns[oldCol].filter((tid) => tid !== id);
    }
    if (newCol) {
      if (!raw.columns[newCol]) raw.columns[newCol] = [];
      if (!raw.columns[newCol].includes(id)) {
        raw.columns[newCol].push(id);
      }
    }
  }

  raw.tasks[idx] = task;

  // Write back
  await writeKanbanJson(raw);

  return transformTask(task);
}

// ── Delete task ────────────────────────────────────────────────────

export async function deleteTask(id) {
  const res = await fetch("/kanban.json");
  if (!res.ok) throw new Error("Failed to read kanban data");
  const raw = await res.json();

  raw.tasks = raw.tasks.filter((t) => t.id !== id);

  // Remove from all columns
  for (const col of Object.keys(raw.columns)) {
    if (Array.isArray(raw.columns[col])) {
      raw.columns[col] = raw.columns[col].filter((tid) => tid !== id);
    }
  }

  await writeKanbanJson(raw);
  return { success: true };
}

// ── Move task ──────────────────────────────────────────────────────

export async function moveTask(id, frontendStatus) {
  return updateTask(id, { status: frontendStatus });
}

// ── Status endpoint ────────────────────────────────────────────────

export async function fetchStatus() {
  // The running server doesn't have /api/status — build a minimal
  // response from /kanban.json data so the sidebar gateway dot works.
  try {
    const data = await fetchKanban();
    const tasks = data.tasks || [];
    const doing = tasks.filter((t) => t.status === "doing").length;
    const todo = tasks.filter((t) => t.status === "todo").length;
    const overdue = tasks.filter((t) => {
      if (!t.dueDate) return false;
      return new Date(t.dueDate) < new Date();
    }).length;
    const topTask =
      tasks.find((t) => t.status === "doing" && t.priority === "high") ||
      tasks.find((t) => t.status === "doing");

    return {
      gateway: { alive: true, port: 8888 },
      tokens: { totalTokens: 0, estimatedCost: "0.00" },
      sprint: {
        doing,
        todo,
        overdue,
        topTask: topTask
          ? {
              id: topTask.id,
              title: topTask.title,
              priority: topTask.priority,
              dueDate: topTask.dueDate,
            }
          : null,
      },
    };
  } catch {
    return {
      gateway: { alive: false, port: 8888 },
      tokens: { totalTokens: 0, estimatedCost: "0.00" },
      sprint: { doing: 0, todo: 0, overdue: 0, topTask: null },
    };
  }
}

// ── Ops endpoint (works natively) ──────────────────────────────────

export async function fetchOps() {
  const res = await fetch(`${API_BASE}/ops`);
  if (!res.ok) throw new Error("Failed to fetch ops data");
  return res.json();
}

// ── Helper: write kanban.json back to server ───────────────────────

async function writeKanbanJson(data) {
  // Try POST to /kanban.json first
  let res = await fetch("/kanban.json", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    // Fallback: use /update endpoint
    res = await fetch("/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to save kanban data");
  }
}

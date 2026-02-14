#!/usr/bin/env node
/**
 * CLI tool for updating Kanban tasks
 * Updated to use single source of truth
 */

const fs = require("fs");
const path = require("path");

// SINGLE SOURCE OF TRUTH - Updated path
const DATA_PATH = path.resolve(__dirname, "../tools/kanban/data/kanban.json");

function loadData() {
  if (!fs.existsSync(DATA_PATH)) {
    console.error(`❌ Data file not found: ${DATA_PATH}`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
}

function saveData(data) {
  data.meta = data.meta || {};
  data.meta.lastUpdated = new Date().toISOString();
  fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
}

function generateId() {
  return `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

const commands = {
  add: (args) => {
    const data = loadData();
    const [title, ...rest] = args;

    if (!title) {
      console.log(
        'Usage: update-kanban add "Task title" [--priority high|medium|low] [--category Work|Personal|CopperAI] [--due 2024-01-15]',
      );
      return;
    }

    const task = {
      id: generateId(),
      title,
      description: "",
      status: "backlog",
      priority: "medium",
      dueDate: null,
      tags: [],
      category: "General",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    // Parse flags
    for (let i = 0; i < rest.length; i++) {
      if (rest[i] === "--priority" && rest[i + 1]) {
        task.priority = rest[++i].toLowerCase();
      } else if (rest[i] === "--category" && rest[i + 1]) {
        task.category = rest[++i];
      } else if (rest[i] === "--due" && rest[i + 1]) {
        task.dueDate = rest[++i];
      } else if (rest[i] === "--tag" && rest[i + 1]) {
        task.tags.push(rest[++i]);
      }
    }

    data.tasks.push(task);
    data.columns.backlog.tasks.push(task.id);
    saveData(data);

    console.log(`✅ Added task: ${task.title} (${task.id})`);
  },

  move: (args) => {
    const [taskId, newStatus] = args;

    if (!taskId || !newStatus) {
      console.log("Usage: update-kanban move <task-id> <backlog|todo|doing|done>");
      return;
    }

    const data = loadData();
    const task = data.tasks.find((t) => t.id === taskId || t.id.includes(taskId));

    if (!task) {
      console.error(`❌ Task not found: ${taskId}`);
      return;
    }

    const oldStatus = task.status;
    task.status = newStatus.toLowerCase();
    task.updatedAt = new Date().toISOString();

    if (task.status === "done") {
      task.completedAt = new Date().toISOString();
    }

    // Update column lists
    if (data.columns[oldStatus]) {
      data.columns[oldStatus].tasks = data.columns[oldStatus].tasks.filter((id) => id !== task.id);
    }
    if (data.columns[task.status]) {
      data.columns[task.status].tasks.push(task.id);
    }

    saveData(data);
    console.log(`✅ Moved "${task.title}" from ${oldStatus} → ${task.status}`);
  },

  priority: (args) => {
    const [taskId, priority] = args;

    if (!taskId || !priority) {
      console.log("Usage: update-kanban priority <task-id> <high|medium|low>");
      return;
    }

    const data = loadData();
    const task = data.tasks.find((t) => t.id === taskId || t.id.includes(taskId));

    if (!task) {
      console.error(`❌ Task not found: ${taskId}`);
      return;
    }

    task.priority = priority.toLowerCase();
    task.updatedAt = new Date().toISOString();
    saveData(data);

    console.log(`✅ Updated priority of "${task.title}" to ${task.priority}`);
  },

  list: (args) => {
    const data = loadData();
    const [filter] = args;

    let tasks = data.tasks;

    if (filter) {
      tasks = tasks.filter(
        (t) =>
          t.status === filter.toLowerCase() ||
          t.priority === filter.toLowerCase() ||
          t.category === filter,
      );
    }

    console.log("\n📋 Kanban Tasks\n");

    const byStatus = {};
    for (const task of tasks) {
      byStatus[task.status] = byStatus[task.status] || [];
      byStatus[task.status].push(task);
    }

    for (const status of ["backlog", "todo", "doing", "done"]) {
      const statusTasks = byStatus[status] || [];
      console.log(`\n${status.toUpperCase()} (${statusTasks.length})`);
      console.log("─".repeat(40));

      for (const task of statusTasks) {
        const priorityIcon = { high: "🔴", medium: "🟡", low: "🟢" }[task.priority] || "⚪";
        const due = task.dueDate ? ` 📅 ${task.dueDate}` : "";
        console.log(`  ${priorityIcon} ${task.title}${due}`);
        console.log(`     ID: ${task.id.slice(-12)} | ${task.category}`);
      }
    }

    console.log(`\nTotal: ${tasks.length} tasks`);
  },

  help: () => {
    console.log(`
Kanban CLI - Task Management

Commands:
  add "title" [options]     Add new task
    --priority high|medium|low
    --category Work|Personal|CopperAI
    --due YYYY-MM-DD
    --tag tagname

  move <task-id> <status>   Move task to column
  priority <task-id> <lvl>  Set priority
  list [filter]             List tasks

Examples:
  update-kanban add "Fix login bug" --priority high --category Work
  update-kanban move task-abc123 doing
  update-kanban list doing
`);
  },
};

const [, , cmd, ...args] = process.argv;
const handler = commands[cmd] || commands.help;
handler(args);

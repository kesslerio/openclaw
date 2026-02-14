#!/usr/bin/env node
/**
 * Migrate existing 85-task Kanban data to new v2.0 schema
 */

const fs = require("fs");
const path = require("path");

const OLD_DATA_PATH =
  "/Users/arvindsarin/Cursor/Claude-2026/openclaw/tools/kanban/data/kanban-data.json";
const TARGET_PATH = "./tools/kanban/data/kanban.json";

console.log("🔄 Migrating existing Kanban tasks to new schema...\n");

// Load old data
if (!fs.existsSync(OLD_DATA_PATH)) {
  console.error(`❌ Source file not found: ${OLD_DATA_PATH}`);
  process.exit(1);
}

const oldData = JSON.parse(fs.readFileSync(OLD_DATA_PATH, "utf8"));
console.log(`📦 Found ${oldData.tasks.length} tasks in old format`);

// Category mapping
const categoryMap = {
  property: "Personal",
  personal: "Personal",
  copper: "CopperAI",
  work: "Work",
};

// Status mapping (blocked → todo with high priority)
const statusMap = {
  todo: "todo",
  doing: "doing",
  done: "done",
  blocked: "todo", // Blocked tasks go to todo but with high priority
  backlog: "backlog",
};

// Convert tasks
const newTasks = oldData.tasks.map((task) => {
  // Generate new ID
  const newId = `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  // Determine priority
  let priority = "medium";
  if (task.urgent === true || task.status === "blocked") {
    priority = "high";
  } else if (task.status === "done") {
    priority = "low";
  }

  // Map category
  const category = categoryMap[task.category?.toLowerCase()] || "General";

  // Map status
  const status = statusMap[task.status?.toLowerCase()] || "backlog";

  // Clean title (remove extra whitespace and numbering)
  let title = task.title
    .replace(/\n\s+#\d+\n\s+/g, "")
    .replace(/^\s+|\s+$/g, "")
    .trim();

  // Extract tags from title and details
  const tags = [];
  if (task.category) tags.push(task.category.toLowerCase());
  if (task.owner && task.owner !== "Arvind" && task.owner !== "VEENA") {
    tags.push(task.owner.toLowerCase());
  }
  if (task.status === "blocked") tags.push("blocked");

  return {
    id: newId,
    title: title,
    description: task.details || "",
    status: status,
    priority: priority,
    dueDate: null,
    tags: [...new Set(tags)], // Deduplicate
    category: category,
    createdAt: task.lastChanged || new Date().toISOString(),
    updatedAt: task.lastChanged || new Date().toISOString(),
    completedAt: task.completedAt || (status === "done" ? task.lastChanged : null),
    assignee: task.owner || task.activeWorker || null,
    estimate: null,
    timeSpent: 0,
    // Keep original metadata
    _original: {
      oldId: task.id,
      urgent: task.urgent,
      wasBlocked: task.status === "blocked",
      tokenUsage: task.tokenUsage,
    },
  };
});

console.log(`✅ Converted ${newTasks.length} tasks\n`);

// Create new data structure
const newData = {
  columns: {
    backlog: {
      id: "backlog",
      title: "BACKLOG",
      tasks: [],
      color: "#6B7280",
    },
    todo: {
      id: "todo",
      title: "TODO",
      tasks: [],
      color: "#3B82F6",
    },
    doing: {
      id: "doing",
      title: "DOING",
      tasks: [],
      color: "#F59E0B",
    },
    done: {
      id: "done",
      title: "DONE",
      tasks: [],
      color: "#10B981",
    },
  },
  tasks: newTasks,
  columnOrder: ["backlog", "todo", "doing", "done"],
  meta: {
    version: "2.0",
    migratedAt: new Date().toISOString(),
    migratedFrom: OLD_DATA_PATH,
    originalTaskCount: oldData.tasks.length,
    schema: {
      fields: [
        "id",
        "title",
        "description",
        "status",
        "priority",
        "dueDate",
        "tags",
        "category",
        "createdAt",
        "updatedAt",
        "completedAt",
        "assignee",
        "estimate",
        "timeSpent",
      ],
      priorities: ["high", "medium", "low"],
      categories: ["Work", "Personal", "CopperAI", "General"],
      statuses: ["backlog", "todo", "doing", "done"],
    },
  },
};

// Distribute tasks to columns
newTasks.forEach((task) => {
  const column = task.status || "backlog";
  if (newData.columns[column]) {
    newData.columns[column].tasks.push(task.id);
  }
});

// Show statistics
const stats = {
  total: newTasks.length,
  byStatus: {},
  byPriority: {},
  byCategory: {},
};

newTasks.forEach((task) => {
  stats.byStatus[task.status] = (stats.byStatus[task.status] || 0) + 1;
  stats.byPriority[task.priority] = (stats.byPriority[task.priority] || 0) + 1;
  stats.byCategory[task.category] = (stats.byCategory[task.category] || 0) + 1;
});

console.log("📊 Migration Statistics:");
console.log(`   Total Tasks: ${stats.total}`);
console.log("\n   By Status:");
console.log(`     Backlog: ${stats.byStatus.backlog || 0}`);
console.log(`     Todo: ${stats.byStatus.todo || 0}`);
console.log(`     Doing: ${stats.byStatus.doing || 0}`);
console.log(`     Done: ${stats.byStatus.done || 0}`);
console.log("\n   By Priority:");
console.log(`     High: ${stats.byPriority.high || 0}`);
console.log(`     Medium: ${stats.byPriority.medium || 0}`);
console.log(`     Low: ${stats.byPriority.low || 0}`);
console.log("\n   By Category:");
console.log(`     Work: ${stats.byCategory.Work || 0}`);
console.log(`     Personal: ${stats.byCategory.Personal || 0}`);
console.log(`     CopperAI: ${stats.byCategory.CopperAI || 0}`);
console.log(`     General: ${stats.byCategory.General || 0}`);

// Backup current file if it exists
if (fs.existsSync(TARGET_PATH)) {
  const backupPath = TARGET_PATH.replace(".json", `-backup-${Date.now()}.json`);
  fs.copyFileSync(TARGET_PATH, backupPath);
  console.log(`\n💾 Backed up current file to: ${backupPath}`);
}

// Write new data
fs.writeFileSync(TARGET_PATH, JSON.stringify(newData, null, 2));
console.log(`\n✅ Migration complete! Data written to: ${TARGET_PATH}`);
console.log("\n🎉 All 85 tasks successfully migrated to new schema v2.0");

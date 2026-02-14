#!/usr/bin/env node
/**
 * Schema Migration Script
 * Adds priority, dueDate, tags, category fields to existing tasks
 */

const fs = require("fs");
const path = require("path");

const DATA_PATH = "./tools/kanban/data/kanban.json";

const PRIORITY_LEVELS = ["high", "medium", "low"];
const CATEGORIES = ["Work", "Personal", "CopperAI", "General"];

function migrate() {
  console.log("📦 Starting schema migration...\n");

  if (!fs.existsSync(DATA_PATH)) {
    console.error(`❌ Data file not found: ${DATA_PATH}`);
    console.log("   Run merge-kanban-files.js first");
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));

  let migratedCount = 0;

  // Migrate each task
  data.tasks = data.tasks.map((task) => {
    const migrated = {
      ...task,

      // Ensure ID exists
      id: task.id || `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,

      // Core fields
      title: task.title || "Untitled",
      description: task.description || "",
      status: (task.status || "backlog").toLowerCase(),

      // NEW: Priority (default: medium)
      priority:
        task.priority && PRIORITY_LEVELS.includes(task.priority.toLowerCase())
          ? task.priority.toLowerCase()
          : "medium",

      // NEW: Due Date (ISO string or null)
      dueDate: task.dueDate || task.due || null,

      // NEW: Tags (array)
      tags: Array.isArray(task.tags) ? task.tags : task.tag ? [task.tag] : [],

      // NEW: Category
      category:
        task.category && CATEGORIES.includes(task.category) ? task.category : inferCategory(task),

      // Timestamps
      createdAt: task.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),

      // NEW: Completion tracking
      completedAt: task.status === "done" ? task.completedAt || new Date().toISOString() : null,

      // NEW: Assignee (for future use)
      assignee: task.assignee || null,

      // NEW: Estimated hours
      estimate: task.estimate || null,

      // NEW: Actual hours spent
      timeSpent: task.timeSpent || 0,
    };

    // Check if migration was needed
    if (!task.priority || !task.hasOwnProperty("tags") || !task.category) {
      migratedCount++;
    }

    return migrated;
  });

  // Update schema version
  data.meta = {
    ...data.meta,
    version: "2.0",
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
      priorities: PRIORITY_LEVELS,
      categories: CATEGORIES,
      statuses: ["backlog", "todo", "doing", "done"],
    },
    lastMigration: new Date().toISOString(),
  };

  // Ensure columns have proper structure
  data.columns = data.columns || {};
  const defaultColumns = {
    backlog: { id: "backlog", title: "BACKLOG", tasks: [], color: "#6B7280" },
    todo: { id: "todo", title: "TODO", tasks: [], color: "#3B82F6" },
    doing: { id: "doing", title: "DOING", tasks: [], color: "#F59E0B" },
    done: { id: "done", title: "DONE", tasks: [], color: "#10B981" },
  };

  for (const [key, defaults] of Object.entries(defaultColumns)) {
    data.columns[key] = {
      ...defaults,
      ...data.columns[key],
      tasks: data.columns[key]?.tasks || [],
    };
  }

  // Rebuild column task lists
  for (const col of Object.values(data.columns)) {
    col.tasks = [];
  }

  for (const task of data.tasks) {
    const col = task.status || "backlog";
    if (data.columns[col]) {
      data.columns[col].tasks.push(task.id);
    }
  }

  // Write back
  fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));

  console.log(`✅ Migration complete!`);
  console.log(`   Total tasks: ${data.tasks.length}`);
  console.log(`   Migrated: ${migratedCount}`);
  console.log(`   Schema version: ${data.meta.version}`);
}

function inferCategory(task) {
  const text = `${task.title} ${task.description}`.toLowerCase();

  if (
    text.includes("copper") ||
    text.includes("ai") ||
    text.includes("agent") ||
    text.includes("oasis") ||
    text.includes("nicole") ||
    text.includes("ashley")
  ) {
    return "CopperAI";
  }

  if (
    text.includes("work") ||
    text.includes("client") ||
    text.includes("meeting") ||
    text.includes("sprint") ||
    text.includes("deploy") ||
    text.includes("feature")
  ) {
    return "Work";
  }

  if (text.includes("personal") || text.includes("home") || text.includes("family")) {
    return "Personal";
  }

  return "General";
}

migrate();

#!/usr/bin/env node
/**
 * Kanban File Consolidation Script
 * Merges multiple kanban.json files into single source of truth
 */

const fs = require("fs");
const path = require("path");

const POSSIBLE_LOCATIONS = [
  "./kanban.json",
  "./kanban/kanban.json",
  "./kanban/data/kanban.json",
  "./data/kanban.json",
  "./clawd/kanban.json",
];

const TARGET_PATH = "./tools/kanban/data/kanban.json";

function findKanbanFiles() {
  const found = [];

  for (const loc of POSSIBLE_LOCATIONS) {
    const fullPath = path.resolve(loc);
    if (fs.existsSync(fullPath)) {
      try {
        const content = JSON.parse(fs.readFileSync(fullPath, "utf8"));
        const stat = fs.statSync(fullPath);
        found.push({
          path: fullPath,
          content,
          modified: stat.mtime,
          taskCount: countTasks(content),
        });
        console.log(
          `✅ Found: ${fullPath} (${found[found.length - 1].taskCount} tasks, modified: ${stat.mtime.toISOString()})`,
        );
      } catch (e) {
        console.log(`⚠️  Invalid JSON at ${fullPath}: ${e.message}`);
      }
    }
  }

  return found;
}

function countTasks(data) {
  if (Array.isArray(data)) return data.length;
  if (data.tasks) return data.tasks.length;
  if (data.columns) {
    return Object.values(data.columns).reduce(
      (sum, col) => sum + (col.tasks?.length || col.items?.length || 0),
      0,
    );
  }
  return 0;
}

function normalizeData(data) {
  // Handle array format
  if (Array.isArray(data)) {
    return {
      columns: {
        backlog: { id: "backlog", title: "BACKLOG", tasks: [] },
        todo: { id: "todo", title: "TODO", tasks: [] },
        doing: { id: "doing", title: "DOING", tasks: [] },
        done: { id: "done", title: "DONE", tasks: [] },
      },
      tasks: data.map(normalizeTask),
      columnOrder: ["backlog", "todo", "doing", "done"],
    };
  }

  // Handle object with tasks array
  if (data.tasks && Array.isArray(data.tasks)) {
    const normalized = {
      columns: data.columns || {
        backlog: { id: "backlog", title: "BACKLOG", tasks: [] },
        todo: { id: "todo", title: "TODO", tasks: [] },
        doing: { id: "doing", title: "DOING", tasks: [] },
        done: { id: "done", title: "DONE", tasks: [] },
      },
      tasks: data.tasks.map(normalizeTask),
      columnOrder: data.columnOrder || ["backlog", "todo", "doing", "done"],
    };

    // Distribute tasks to columns based on status
    normalized.tasks.forEach((task) => {
      const column = task.status?.toLowerCase() || "backlog";
      if (normalized.columns[column]) {
        if (!normalized.columns[column].tasks.includes(task.id)) {
          normalized.columns[column].tasks.push(task.id);
        }
      }
    });

    return normalized;
  }

  // Already in correct format
  return {
    ...data,
    tasks: (data.tasks || []).map(normalizeTask),
    columnOrder: data.columnOrder || ["backlog", "todo", "doing", "done"],
  };
}

function normalizeTask(task, index) {
  return {
    id: task.id || `task-${Date.now()}-${index}`,
    title: task.title || task.name || "Untitled Task",
    description: task.description || task.desc || "",
    status: (task.status || task.column || "backlog").toLowerCase(),
    priority: task.priority || "medium",
    dueDate: task.dueDate || task.due || null,
    tags: task.tags || [],
    category: task.category || "General",
    createdAt: task.createdAt || task.created || new Date().toISOString(),
    updatedAt: task.updatedAt || new Date().toISOString(),
  };
}

function mergeKanbanFiles(files) {
  if (files.length === 0) {
    console.log("❌ No kanban.json files found. Creating fresh database.");
    return createFreshDatabase();
  }

  if (files.length === 1) {
    console.log(`📦 Single file found. Normalizing: ${files[0].path}`);
    return normalizeData(files[0].content);
  }

  // Multiple files - merge by most recent modification + dedup tasks
  console.log(`🔀 Merging ${files.length} files...`);

  // Sort by modification date (newest first)
  files.sort((a, b) => b.modified - a.modified);

  const taskMap = new Map();
  const merged = {
    columns: {
      backlog: { id: "backlog", title: "BACKLOG", tasks: [] },
      todo: { id: "todo", title: "TODO", tasks: [] },
      doing: { id: "doing", title: "DOING", tasks: [] },
      done: { id: "done", title: "DONE", tasks: [] },
    },
    tasks: [],
    columnOrder: ["backlog", "todo", "doing", "done"],
  };

  // Process each file, newer files take precedence
  for (const file of files) {
    const normalized = normalizeData(file.content);

    for (const task of normalized.tasks || []) {
      const key = task.id || `${task.title}-${task.createdAt}`;

      if (!taskMap.has(key)) {
        taskMap.set(key, task);
      }
    }
  }

  merged.tasks = Array.from(taskMap.values());

  // Rebuild column task lists
  merged.tasks.forEach((task) => {
    const column = task.status || "backlog";
    if (merged.columns[column]) {
      merged.columns[column].tasks.push(task.id);
    }
  });

  console.log(`✅ Merged ${merged.tasks.length} unique tasks`);
  return merged;
}

function createFreshDatabase() {
  return {
    columns: {
      backlog: { id: "backlog", title: "BACKLOG", tasks: [] },
      todo: { id: "todo", title: "TODO", tasks: [] },
      doing: { id: "doing", title: "DOING", tasks: [] },
      done: { id: "done", title: "DONE", tasks: [] },
    },
    tasks: [],
    columnOrder: ["backlog", "todo", "doing", "done"],
    meta: {
      version: "2.0",
      createdAt: new Date().toISOString(),
      migratedAt: new Date().toISOString(),
    },
  };
}

function backupAndCleanup(files, targetPath) {
  const backupDir = "./clawd/data/backups";

  if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true });
  }

  for (const file of files) {
    if (file.path !== path.resolve(targetPath)) {
      const backupName = `kanban-backup-${path.basename(path.dirname(file.path))}-${Date.now()}.json`;
      const backupPath = path.join(backupDir, backupName);

      fs.copyFileSync(file.path, backupPath);
      console.log(`📁 Backed up: ${file.path} → ${backupPath}`);

      // Remove old file
      fs.unlinkSync(file.path);
      console.log(`🗑️  Removed: ${file.path}`);
    }
  }
}

function main() {
  console.log("🔍 Scanning for kanban.json files...\n");

  const files = findKanbanFiles();

  console.log(`\n📊 Found ${files.length} kanban file(s)\n`);

  // Ensure target directory exists
  const targetDir = path.dirname(TARGET_PATH);
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  // Merge and normalize
  const merged = mergeKanbanFiles(files);

  // Add metadata
  merged.meta = {
    version: "2.0",
    migratedAt: new Date().toISOString(),
    sourceFiles: files.map((f) => f.path),
  };

  // Write to target
  fs.writeFileSync(TARGET_PATH, JSON.stringify(merged, null, 2));
  console.log(`\n✅ Consolidated data written to: ${TARGET_PATH}`);

  // Backup and cleanup old files
  if (files.length > 0) {
    console.log("\n🧹 Cleaning up old files...");
    backupAndCleanup(files, TARGET_PATH);
  }

  console.log("\n🎉 Migration complete!");
  console.log(`   Total tasks: ${merged.tasks.length}`);
  console.log(`   Target file: ${path.resolve(TARGET_PATH)}`);
}

main();

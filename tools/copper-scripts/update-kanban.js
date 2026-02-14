#!/usr/bin/env node

/**
 * Nike's Kanban Updater
 * Usage: node update-kanban.js <action> [options]
 *
 * Actions:
 *   add       Add a new task
 *   update    Update existing task
 *   move      Move task to different status
 *   delete    Delete a task
 *   list      List all tasks
 *
 * Examples:
 *   node update-kanban.js add --title "Call Alex" --owner Arvind --category property
 *   node update-kanban.js move --id 5 --status done
 *   node update-kanban.js update --id 3 --urgent true
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const DATA_FILE = path.join(__dirname, "../kanban-data.json");

// Read kanban data
function readKanban() {
  const data = fs.readFileSync(DATA_FILE, "utf8");
  return JSON.parse(data);
}

// Write kanban data
function writeKanban(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// Git commit and push
function publishToGitHub(message) {
  try {
    execSync("git add kanban-data.json", { cwd: path.dirname(DATA_FILE) });
    execSync(`git commit -m "${message}"`, { cwd: path.dirname(DATA_FILE) });
    execSync("git push origin master", { cwd: path.dirname(DATA_FILE) });
    console.log("✅ Published to GitHub!");
    return true;
  } catch (error) {
    console.error("❌ Git error:", error.message);
    return false;
  }
}

// Add new task
function addTask(options) {
  const data = readKanban();
  const newId = Math.max(...data.tasks.map((t) => t.id), 0) + 1;

  const task = {
    id: newId,
    title: options.title,
    details: options.details || "",
    owner: options.owner || "Arvind",
    category: options.category || "personal",
    status: options.status || "todo",
    urgent: options.urgent === "true" || options.urgent === true,
    lastChanged: new Date().toISOString(),
  };

  if (options.activeWorker) task.activeWorker = options.activeWorker;

  data.tasks.push(task);
  data.lastUpdated = new Date().toISOString();

  writeKanban(data);

  const urgentFlag = task.urgent ? " (urgent)" : "";
  const commitMsg = `🤖 Nike: Added '${task.title}' for ${task.owner} (${task.category})${urgentFlag}`;

  console.log(`➕ Added task #${newId}: ${task.title}`);
  publishToGitHub(commitMsg);
}

// Update existing task
function updateTask(options) {
  const data = readKanban();
  const task = data.tasks.find((t) => t.id === parseInt(options.id));

  if (!task) {
    console.error(`❌ Task #${options.id} not found`);
    return;
  }

  const changes = [];

  if (options.title) {
    task.title = options.title;
    changes.push("title");
  }
  if (options.details) {
    task.details = options.details;
    changes.push("details");
  }
  if (options.owner) {
    task.owner = options.owner;
    changes.push("owner");
  }
  if (options.category) {
    task.category = options.category;
    changes.push("category");
  }
  if (options.status) {
    task.status = options.status;
    changes.push("status");
    if (options.status === "done" && !task.completedAt) {
      task.completedAt = new Date().toISOString();
    }
  }
  if (options.activeWorker !== undefined) {
    task.activeWorker = options.activeWorker || null;
    changes.push("activeWorker");
  }
  if (options.urgent !== undefined) {
    task.urgent = options.urgent === "true" || options.urgent === true;
    changes.push("urgent");
  }

  task.lastChanged = new Date().toISOString();
  data.lastUpdated = new Date().toISOString();

  writeKanban(data);

  const commitMsg = `🤖 Nike: Updated '${task.title}' (${changes.join(", ")})`;

  console.log(`✏️  Updated task #${task.id}: ${changes.join(", ")}`);
  publishToGitHub(commitMsg);
}

// Move task to different status
function moveTask(options) {
  const data = readKanban();
  const task = data.tasks.find((t) => t.id === parseInt(options.id));

  if (!task) {
    console.error(`❌ Task #${options.id} not found`);
    return;
  }

  const oldStatus = task.status;
  task.status = options.status;
  task.lastChanged = new Date().toISOString();

  if (options.status === "done" && !task.completedAt) {
    task.completedAt = new Date().toISOString();
  }

  data.lastUpdated = new Date().toISOString();

  writeKanban(data);

  const commitMsg = `🤖 Nike: Moved '${task.title}' from ${oldStatus} → ${options.status}`;

  console.log(`📊 Moved task #${task.id}: ${oldStatus} → ${options.status}`);
  publishToGitHub(commitMsg);
}

// Delete task
function deleteTask(options) {
  const data = readKanban();
  const task = data.tasks.find((t) => t.id === parseInt(options.id));

  if (!task) {
    console.error(`❌ Task #${options.id} not found`);
    return;
  }

  const title = task.title;
  data.tasks = data.tasks.filter((t) => t.id !== parseInt(options.id));
  data.lastUpdated = new Date().toISOString();

  writeKanban(data);

  const commitMsg = `🤖 Nike: Deleted '${title}'`;

  console.log(`🗑️  Deleted task #${options.id}: ${title}`);
  publishToGitHub(commitMsg);
}

// List tasks
function listTasks(options) {
  const data = readKanban();
  const filter = options.status || null;
  const tasks = filter ? data.tasks.filter((t) => t.status === filter) : data.tasks;

  console.log(`\n📋 Kanban Tasks (${tasks.length} total)\n`);

  tasks.forEach((task) => {
    const urgentFlag = task.urgent ? "🔴" : "  ";
    const workerInfo = task.activeWorker ? ` [👷 ${task.activeWorker}]` : "";
    console.log(`${urgentFlag} #${task.id} [${task.status}] ${task.title}`);
    console.log(`   👤 ${task.owner} | 🏷️  ${task.category}${workerInfo}`);
    if (task.details) console.log(`   📝 ${task.details}`);
    console.log("");
  });
}

// Parse command line args
function parseArgs() {
  const args = process.argv.slice(2);
  const action = args[0];
  const options = {};

  for (let i = 1; i < args.length; i += 2) {
    const key = args[i].replace("--", "");
    const value = args[i + 1];
    options[key] = value;
  }

  return { action, options };
}

// Main
function main() {
  const { action, options } = parseArgs();

  switch (action) {
    case "add":
      if (!options.title) {
        console.error("❌ --title required");
        process.exit(1);
      }
      addTask(options);
      break;

    case "update":
      if (!options.id) {
        console.error("❌ --id required");
        process.exit(1);
      }
      updateTask(options);
      break;

    case "move":
      if (!options.id || !options.status) {
        console.error("❌ --id and --status required");
        process.exit(1);
      }
      moveTask(options);
      break;

    case "delete":
      if (!options.id) {
        console.error("❌ --id required");
        process.exit(1);
      }
      deleteTask(options);
      break;

    case "list":
      listTasks(options);
      break;

    default:
      console.log(`
🐾 Nike's Kanban Updater

Usage: node update-kanban.js <action> [options]

Actions:
  add       Add a new task
  update    Update existing task
  move      Move task to different status
  delete    Delete a task
  list      List all tasks

Examples:
  node update-kanban.js add --title "Call Alex" --owner Arvind --category property --urgent true
  node update-kanban.js move --id 5 --status done
  node update-kanban.js update --id 3 --details "New details here"
  node update-kanban.js list
  node update-kanban.js list --status doing
  node update-kanban.js delete --id 10
            `);
  }
}

main();

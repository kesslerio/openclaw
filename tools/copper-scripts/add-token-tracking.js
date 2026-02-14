#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const DATA_FILE = path.join(__dirname, "../kanban-data.json");
const TOKEN_FILE = path.join(__dirname, "../memory/token-tracking.json");

// Read files
const kanbanData = JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
const tokenData = JSON.parse(fs.readFileSync(TOKEN_FILE, "utf8"));

// Add token tracking to each task
kanbanData.tasks = kanbanData.tasks.map((task) => {
  const tracking = tokenData.taskTokenUsage[task.id.toString()] || {
    totalTokens: 0,
    todayTokens: 0,
    estimatedRemaining: 1000,
    history: [],
  };

  return {
    ...task,
    tokenUsage: {
      total: tracking.totalTokens,
      today: tracking.todayTokens,
      estimated: tracking.estimatedRemaining,
      lastUpdated: new Date().toISOString(),
    },
  };
});

// Write back
fs.writeFileSync(DATA_FILE, JSON.stringify(kanbanData, null, 2));

console.log("✅ Token tracking added to all tasks!");
console.log(`📊 Total tasks updated: ${kanbanData.tasks.length}`);

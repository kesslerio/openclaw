/**
 * Kanban Mission Control Server
 * Upgraded with status API and remote access
 */

const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 8888;

// CRITICAL: Bind to 0.0.0.0 for Tailscale access
const HOST = "0.0.0.0";

// Single source of truth - UPDATED PATH
const DATA_PATH = path.resolve(__dirname, "../data/kanban.json");

// Middleware
app.use(cors());
app.use(express.json());

// Serve static frontend (production)
app.use(express.static(path.resolve(__dirname, "../frontend/dist")));

// ============================================
// KANBAN API ROUTES
// ============================================

// Get all data
app.get("/api/kanban", (req, res) => {
  try {
    const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: "Failed to load kanban data", details: error.message });
  }
});

// Get tasks with optional filters
app.get("/api/tasks", (req, res) => {
  try {
    const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
    let tasks = data.tasks || [];

    const { status, priority, category, tag } = req.query;

    if (status) {
      tasks = tasks.filter((t) => t.status === status.toLowerCase());
    }
    if (priority) {
      tasks = tasks.filter((t) => t.priority === priority.toLowerCase());
    }
    if (category) {
      tasks = tasks.filter((t) => t.category === category);
    }
    if (tag) {
      tasks = tasks.filter((t) => t.tags && t.tags.includes(tag));
    }

    // Sort by priority (high first) then by due date
    tasks.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      const pDiff = (priorityOrder[a.priority] || 1) - (priorityOrder[b.priority] || 1);
      if (pDiff !== 0) return pDiff;

      if (a.dueDate && b.dueDate) {
        return new Date(a.dueDate) - new Date(b.dueDate);
      }
      return a.dueDate ? -1 : 1;
    });

    res.json(tasks);
  } catch (error) {
    res.status(500).json({ error: "Failed to load tasks", details: error.message });
  }
});

// Create task
app.post("/api/tasks", (req, res) => {
  try {
    const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));

    const task = {
      id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      title: req.body.title || "Untitled",
      description: req.body.description || "",
      status: req.body.status || "backlog",
      priority: req.body.priority || "medium",
      dueDate: req.body.dueDate || null,
      tags: req.body.tags || [],
      category: req.body.category || "General",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    data.tasks.push(task);

    // Add to column
    if (data.columns[task.status]) {
      data.columns[task.status].tasks.push(task.id);
    }

    data.meta = data.meta || {};
    data.meta.lastUpdated = new Date().toISOString();

    fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
    res.status(201).json(task);
  } catch (error) {
    res.status(500).json({ error: "Failed to create task", details: error.message });
  }
});

// Update task
app.put("/api/tasks/:id", (req, res) => {
  try {
    const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
    const taskIndex = data.tasks.findIndex((t) => t.id === req.params.id);

    if (taskIndex === -1) {
      return res.status(404).json({ error: "Task not found" });
    }

    const oldStatus = data.tasks[taskIndex].status;
    const newStatus = req.body.status || oldStatus;

    data.tasks[taskIndex] = {
      ...data.tasks[taskIndex],
      ...req.body,
      id: req.params.id, // Preserve ID
      updatedAt: new Date().toISOString(),
    };

    // Handle completion
    if (newStatus === "done" && oldStatus !== "done") {
      data.tasks[taskIndex].completedAt = new Date().toISOString();
    }

    // Update column lists if status changed
    if (oldStatus !== newStatus) {
      if (data.columns[oldStatus]) {
        data.columns[oldStatus].tasks = data.columns[oldStatus].tasks.filter(
          (id) => id !== req.params.id,
        );
      }
      if (data.columns[newStatus]) {
        data.columns[newStatus].tasks.push(req.params.id);
      }
    }

    data.meta = data.meta || {};
    data.meta.lastUpdated = new Date().toISOString();

    fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
    res.json(data.tasks[taskIndex]);
  } catch (error) {
    res.status(500).json({ error: "Failed to update task", details: error.message });
  }
});

// Delete task
app.delete("/api/tasks/:id", (req, res) => {
  try {
    const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
    const task = data.tasks.find((t) => t.id === req.params.id);

    if (!task) {
      return res.status(404).json({ error: "Task not found" });
    }

    // Remove from tasks array
    data.tasks = data.tasks.filter((t) => t.id !== req.params.id);

    // Remove from column
    if (data.columns[task.status]) {
      data.columns[task.status].tasks = data.columns[task.status].tasks.filter(
        (id) => id !== req.params.id,
      );
    }

    data.meta = data.meta || {};
    data.meta.lastUpdated = new Date().toISOString();

    fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
    res.json({ success: true, deleted: req.params.id });
  } catch (error) {
    res.status(500).json({ error: "Failed to delete task", details: error.message });
  }
});

// Move task (convenience endpoint)
app.post("/api/tasks/:id/move", (req, res) => {
  try {
    const { status } = req.body;

    if (!status) {
      return res.status(400).json({ error: "Status required" });
    }

    const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
    const task = data.tasks.find((t) => t.id === req.params.id);

    if (!task) {
      return res.status(404).json({ error: "Task not found" });
    }

    const oldStatus = task.status;
    task.status = status;
    task.updatedAt = new Date().toISOString();

    if (status === "done") {
      task.completedAt = new Date().toISOString();
    }

    // Update columns
    if (data.columns[oldStatus]) {
      data.columns[oldStatus].tasks = data.columns[oldStatus].tasks.filter((id) => id !== task.id);
    }
    if (data.columns[status]) {
      data.columns[status].tasks.push(task.id);
    }

    fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
    res.json(task);
  } catch (error) {
    res.status(500).json({ error: "Failed to move task", details: error.message });
  }
});

// ============================================
// STATUS API - NEW ENDPOINT
// ============================================

app.get("/api/status", async (req, res) => {
  try {
    const status = {
      timestamp: new Date().toISOString(),
      gateway: await checkGatewayHealth(),
      tokens: await getTokenUsage(),
      sprint: getSprintStatus(),
      system: getSystemInfo(),
    };

    res.json(status);
  } catch (error) {
    res.status(500).json({
      error: "Status check failed",
      details: error.message,
      timestamp: new Date().toISOString(),
    });
  }
});

// Gateway health check (OpenClaw port 18789)
async function checkGatewayHealth() {
  const GATEWAY_PORT = 18789;
  const GATEWAY_HOST = "localhost";

  return new Promise((resolve) => {
    const net = require("net");
    const socket = new net.Socket();

    socket.setTimeout(2000);

    socket.on("connect", () => {
      socket.destroy();
      resolve({
        alive: true,
        port: GATEWAY_PORT,
        latency: Date.now() - startTime,
      });
    });

    socket.on("timeout", () => {
      socket.destroy();
      resolve({
        alive: false,
        port: GATEWAY_PORT,
        error: "Timeout",
      });
    });

    socket.on("error", (err) => {
      resolve({
        alive: false,
        port: GATEWAY_PORT,
        error: err.message,
      });
    });

    const startTime = Date.now();
    socket.connect(GATEWAY_PORT, GATEWAY_HOST);
  });
}

// Token usage from logs
async function getTokenUsage() {
  const LOG_DIR = path.join(process.env.HOME || "/root", ".openclaw/logs");

  try {
    if (!fs.existsSync(LOG_DIR)) {
      return { available: false, error: "Log directory not found" };
    }

    // Find today's log files
    const today = new Date().toISOString().split("T")[0];
    const files = fs
      .readdirSync(LOG_DIR)
      .filter((f) => f.includes(today) || f.endsWith(".log"))
      .map((f) => path.join(LOG_DIR, f));

    if (files.length === 0) {
      return { available: false, error: "No log files for today" };
    }

    let totalInputTokens = 0;
    let totalOutputTokens = 0;
    let requestCount = 0;

    // Token patterns to search for
    const tokenPatterns = [
      /input_tokens["\s:]+(\d+)/gi,
      /output_tokens["\s:]+(\d+)/gi,
      /prompt_tokens["\s:]+(\d+)/gi,
      /completion_tokens["\s:]+(\d+)/gi,
      /"usage":\s*{[^}]*"input":\s*(\d+)[^}]*"output":\s*(\d+)/gi,
    ];

    for (const file of files.slice(-5)) {
      // Last 5 log files
      try {
        const content = fs.readFileSync(file, "utf8");

        // Count input tokens
        const inputMatches = content.matchAll(/(?:input_tokens|prompt_tokens)["\s:]+(\d+)/gi);
        for (const match of inputMatches) {
          totalInputTokens += parseInt(match[1], 10);
          requestCount++;
        }

        // Count output tokens
        const outputMatches = content.matchAll(/(?:output_tokens|completion_tokens)["\s:]+(\d+)/gi);
        for (const match of outputMatches) {
          totalOutputTokens += parseInt(match[1], 10);
        }
      } catch (e) {
        continue;
      }
    }

    // Estimate cost (Claude pricing approximation)
    const inputCost = (totalInputTokens / 1000000) * 3.0; // $3/MTok input
    const outputCost = (totalOutputTokens / 1000000) * 15.0; // $15/MTok output
    const totalCost = inputCost + outputCost;

    return {
      available: true,
      date: today,
      inputTokens: totalInputTokens,
      outputTokens: totalOutputTokens,
      totalTokens: totalInputTokens + totalOutputTokens,
      estimatedCost: totalCost.toFixed(2),
      requestCount: Math.floor(requestCount / 2), // Approximate
    };
  } catch (error) {
    return { available: false, error: error.message };
  }
}

// Sprint status from Kanban
function getSprintStatus() {
  try {
    const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));

    const doingTasks = data.tasks.filter((t) => t.status === "doing");
    const todoTasks = data.tasks.filter((t) => t.status === "todo");
    const doneTodayTasks = data.tasks.filter((t) => {
      if (t.status !== "done" || !t.completedAt) return false;
      const completed = new Date(t.completedAt);
      const today = new Date();
      return completed.toDateString() === today.toDateString();
    });

    // Find highest priority active task
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    const topTask = doingTasks.sort(
      (a, b) => (priorityOrder[a.priority] || 1) - (priorityOrder[b.priority] || 1),
    )[0];

    // Find overdue tasks
    const now = new Date();
    const overdue = data.tasks.filter((t) => {
      if (t.status === "done" || !t.dueDate) return false;
      return new Date(t.dueDate) < now;
    });

    return {
      doing: doingTasks.length,
      todo: todoTasks.length,
      doneToday: doneTodayTasks.length,
      overdue: overdue.length,
      topTask: topTask
        ? {
            id: topTask.id,
            title: topTask.title,
            priority: topTask.priority,
            dueDate: topTask.dueDate,
          }
        : null,
      totalActive: doingTasks.length + todoTasks.length,
    };
  } catch (error) {
    return { error: error.message };
  }
}

// System info
function getSystemInfo() {
  const os = require("os");

  return {
    hostname: os.hostname(),
    platform: os.platform(),
    uptime: Math.floor(os.uptime() / 60), // minutes
    memory: {
      free: Math.round(os.freemem() / 1024 / 1024),
      total: Math.round(os.totalmem() / 1024 / 1024),
    },
    load: os.loadavg()[0].toFixed(2),
  };
}

// ============================================
// CATCH-ALL FOR SPA
// ============================================

app.get("*", (req, res) => {
  res.sendFile(path.resolve(__dirname, "../frontend/dist/index.html"));
});

// ============================================
// START SERVER
// ============================================

app.listen(PORT, HOST, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║           🚀 KANBAN MISSION CONTROL v2.0                    ║
╠══════════════════════════════════════════════════════════════╣
║  Server running on:                                          ║
║    Local:     http://localhost:${PORT}                         ║
║    Network:   http://${HOST}:${PORT}                           ║
║                                                              ║
║  Data file:   ${DATA_PATH}
║                                                              ║
║  API Endpoints:                                              ║
║    GET  /api/kanban      - Full board data                   ║
║    GET  /api/tasks       - Tasks with filters                ║
║    POST /api/tasks       - Create task                       ║
║    PUT  /api/tasks/:id   - Update task                       ║
║    GET  /api/status      - Mission Control metrics           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
  `);

  // Get Tailscale IP
  const { execSync } = require("child_process");
  try {
    const tailscaleIP = execSync("tailscale ip -4 2>/dev/null").toString().trim();
    console.log(`  📱 Tailscale URL: http://${tailscaleIP}:${PORT}\n`);
  } catch (e) {
    console.log(`  📱 Run 'tailscale ip -4' to get your remote access URL\n`);
  }
});

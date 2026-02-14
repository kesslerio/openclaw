#!/usr/bin/env node
/**
 * AI Task Analyzer using OpenClaw infrastructure
 * Uses openclaw message command to analyze tasks
 */

const fs = require("fs");
const { execSync } = require("child_process");

const DATA_PATH = "./tools/kanban/data/kanban.json";

console.log("🤖 AI Task Analyzer (via OpenClaw)...\n");

// Load tasks
const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
console.log(`📦 Loaded ${data.tasks.length} tasks\n`);

// Analyze a single task using OpenClaw
async function analyzeTask(task) {
  const prompt = `Analyze this task and provide a structured breakdown:

TASK: ${task.title}
DESCRIPTION: ${task.description || "No description provided"}
CATEGORY: ${task.category}
CURRENT STATUS: ${task.status}
PRIORITY: ${task.priority}
${task.assignee ? `ASSIGNEE: ${task.assignee}` : ""}

Provide analysis in this exact JSON format:
{
  "automationType": "llm" | "human" | "hybrid" | "blocked",
  "automationReason": "Brief explanation of why this classification",
  "isBlocked": true/false,
  "blockageReason": "What's blocking (if blocked, otherwise null)",
  "steps": [
    "Step 1: First concrete action",
    "Step 2: Next action",
    "Step 3: Final action"
  ],
  "estimatedMinutes": number,
  "aiCapabilities": ["capability1", "capability2"],
  "humanRequirements": ["requirement1", "requirement2"]
}

CLASSIFICATION GUIDE:
- "llm": Can be fully automated with AI (research, writing, analysis, data processing)
- "human": Requires human action (phone calls, physical tasks, legal signatures, in-person meetings)
- "hybrid": AI can help but human needed for key steps (AI drafts + human review/approval)
- "blocked": Cannot proceed until dependency resolved

Return ONLY the JSON, no markdown or explanation.`;

  try {
    // Write prompt to temp file
    const tempFile = `/tmp/task-analysis-${Date.now()}.txt`;
    fs.writeFileSync(tempFile, prompt);

    // Use OpenClaw to analyze
    const response = execSync(
      `openclaw message send --provider anthropic:manual --model claude-sonnet-4-20250514 "$(cat ${tempFile})"`,
      {
        encoding: "utf8",
        maxBuffer: 10 * 1024 * 1024,
        timeout: 30000,
      },
    );

    // Clean up temp file
    fs.unlinkSync(tempFile);

    // Extract JSON from response
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    } else {
      throw new Error("No JSON found in response");
    }
  } catch (error) {
    // Fallback analysis
    return {
      automationType: task.category === "CopperAI" ? "hybrid" : "human",
      automationReason: `Analysis via OpenClaw failed: ${error.message.substring(0, 100)}`,
      isBlocked: false,
      blockageReason: null,
      steps: ["Review task details", "Determine approach", "Execute", "Verify completion"],
      estimatedMinutes: 30,
      aiCapabilities: ["Research", "Documentation"],
      humanRequirements: ["Review", "Approval"],
    };
  }
}

// Process all tasks
async function analyzeTasks() {
  let analyzed = 0;
  let errors = 0;

  console.log(
    "⚠️  Note: Using OpenClaw message send (slower but works without separate API key)\n",
  );

  for (const task of data.tasks) {
    // Skip if already analyzed
    if (
      task.analysis &&
      task.analysis.automationReason &&
      !task.analysis.automationReason.includes("demo")
    ) {
      console.log(`⏭️  ${task.title.substring(0, 50)}... ALREADY ANALYZED`);
      continue;
    }

    try {
      process.stdout.write(`Analyzing: ${task.title.substring(0, 50)}...`);

      const analysis = await analyzeTask(task);
      task.analysis = analysis;

      const icons = {
        llm: "🤖",
        human: "👤",
        hybrid: "🤝",
        blocked: "🚫",
      };

      console.log(` ${icons[analysis.automationType]} ${analysis.automationType.toUpperCase()}`);
      analyzed++;

      // Save progress every 10 tasks
      if (analyzed % 10 === 0) {
        fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
        console.log(`   💾 Progress saved (${analyzed}/${data.tasks.length})`);
      }

      // Rate limit
      await new Promise((resolve) => setTimeout(resolve, 2000));
    } catch (error) {
      console.log(` ❌ ERROR: ${error.message}`);
      errors++;
    }
  }

  console.log(`\n✅ Analysis complete: ${analyzed} tasks, ${errors} errors\n`);

  // Show statistics
  const stats = {
    llm: 0,
    human: 0,
    hybrid: 0,
    blocked: 0,
  };

  data.tasks.forEach((task) => {
    if (task.analysis) {
      stats[task.analysis.automationType]++;
    }
  });

  console.log("📊 Automation Breakdown:");
  console.log(`   🤖 LLM (Fully Automated):  ${stats.llm} tasks`);
  console.log(`   🤝 Hybrid (AI + Human):    ${stats.hybrid} tasks`);
  console.log(`   👤 Human Required:         ${stats.human} tasks`);
  console.log(`   🚫 Blocked:                ${stats.blocked} tasks`);

  // Save final data
  data.meta.lastAnalysis = new Date().toISOString();
  data.meta.analysisVersion = "1.0";
  fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
  console.log(`\n💾 Saved analyzed tasks to: ${DATA_PATH}`);
}

// Run analysis
analyzeTasks().catch((error) => {
  console.error("❌ Fatal error:", error);
  process.exit(1);
});

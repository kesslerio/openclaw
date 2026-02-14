#!/usr/bin/env node
/**
 * AI Task Analyzer
 * Analyzes each task for:
 * - Automation potential (LLM/Human/Hybrid/Blocked)
 * - Logical step breakdown
 * - Blockage identification
 */

const fs = require("fs");
const path = require("path");
const https = require("https");

const DATA_PATH = "./tools/kanban/data/kanban.json";
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

if (!ANTHROPIC_API_KEY) {
  console.error("❌ ANTHROPIC_API_KEY environment variable not set");
  console.log("   Set it with: export ANTHROPIC_API_KEY=your-key-here");
  process.exit(1);
}

console.log("🤖 AI Task Analyzer Starting...\n");

// Load tasks
const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
console.log(`📦 Loaded ${data.tasks.length} tasks\n`);

// Analyze a single task using Claude
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

  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      messages: [
        {
          role: "user",
          content: prompt,
        },
      ],
    });

    const options = {
      hostname: "api.anthropic.com",
      port: 443,
      path: "/v1/messages",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Length": Buffer.byteLength(postData),
      },
    };

    const req = https.request(options, (res) => {
      let data = "";

      res.on("data", (chunk) => {
        data += chunk;
      });

      res.on("end", () => {
        try {
          const response = JSON.parse(data);
          if (response.content && response.content[0] && response.content[0].text) {
            const analysisText = response.content[0].text.trim();
            // Remove markdown code blocks if present
            const jsonMatch = analysisText.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              const analysis = JSON.parse(jsonMatch[0]);
              resolve(analysis);
            } else {
              reject(new Error("No JSON found in response"));
            }
          } else {
            reject(new Error("Invalid API response format"));
          }
        } catch (e) {
          reject(new Error(`Failed to parse response: ${e.message}`));
        }
      });
    });

    req.on("error", (e) => {
      reject(e);
    });

    req.write(postData);
    req.end();
  });
}

// Process all tasks
async function analyzeTasks() {
  let analyzed = 0;
  let errors = 0;

  for (const task of data.tasks) {
    try {
      process.stdout.write(`Analyzing: ${task.title.substring(0, 50)}...`);

      const analysis = await analyzeTask(task);

      // Add analysis to task
      task.analysis = analysis;

      // Add icon based on automation type
      const icons = {
        llm: "🤖",
        human: "👤",
        hybrid: "🤝",
        blocked: "🚫",
      };

      console.log(` ${icons[analysis.automationType]} ${analysis.automationType.toUpperCase()}`);
      analyzed++;

      // Rate limit: wait 1 second between requests
      await new Promise((resolve) => setTimeout(resolve, 1000));
    } catch (error) {
      console.log(` ❌ ERROR: ${error.message}`);
      errors++;

      // Add fallback analysis
      task.analysis = {
        automationType: "human",
        automationReason: "Analysis failed, defaulting to human",
        isBlocked: false,
        blockageReason: null,
        steps: ["Review task details", "Determine next action", "Execute"],
        estimatedMinutes: 30,
        aiCapabilities: [],
        humanRequirements: ["Manual review needed"],
      };
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

  // Save updated data
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

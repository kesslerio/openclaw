#!/usr/bin/env node
/**
 * Demo Task Analysis
 * Adds sample analysis to first 10 tasks to demonstrate the feature
 */

const fs = require("fs");
const DATA_PATH = "./tools/kanban/data/kanban.json";

console.log("🎨 Adding demo analysis to tasks...\n");

const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));

// Demo analyses for different task types
const demoAnalyses = {
  property: {
    automationType: "human",
    automationReason: "Requires phone call and negotiation with real estate agent",
    isBlocked: false,
    blockageReason: null,
    steps: [
      "Call Alex at 817-939-9971",
      "Negotiate offer from $108k to $111k",
      "Get verbal confirmation",
      "Follow up with written agreement",
      "Coordinate closing timeline",
    ],
    estimatedMinutes: 45,
    aiCapabilities: [
      "Draft negotiation talking points",
      "Research comparable properties",
      "Calculate offer math",
    ],
    humanRequirements: ["Phone call", "Negotiation skills", "Legal review"],
  },
  research: {
    automationType: "llm",
    automationReason: "Pure research and data analysis task, no human interaction needed",
    isBlocked: false,
    blockageReason: null,
    steps: [
      "Search for relevant research papers and articles",
      "Extract key findings and data points",
      "Synthesize information into structured report",
      "Generate summary with citations",
      "Format output for easy consumption",
    ],
    estimatedMinutes: 20,
    aiCapabilities: ["Web search", "Document analysis", "Summarization", "Citation formatting"],
    humanRequirements: [],
  },
  tech: {
    automationType: "hybrid",
    automationReason: "AI can write code and tests, but human needs to review and deploy",
    isBlocked: false,
    blockageReason: null,
    steps: [
      "AI: Analyze current implementation",
      "AI: Write code changes with tests",
      "Human: Review code quality and security",
      "AI: Generate documentation",
      "Human: Deploy to production",
      "Human: Monitor for issues",
    ],
    estimatedMinutes: 60,
    aiCapabilities: ["Code generation", "Test writing", "Documentation", "Bug analysis"],
    humanRequirements: ["Code review", "Deployment", "Production monitoring"],
  },
  blocked: {
    automationType: "blocked",
    automationReason: "Waiting on external dependency before work can begin",
    isBlocked: true,
    blockageReason: "Waiting for API access credentials from vendor",
    steps: [
      "Follow up with vendor for API credentials",
      "Once received: Set up API authentication",
      "Test API connection",
      "Implement integration",
      "Deploy and verify",
    ],
    estimatedMinutes: 120,
    aiCapabilities: ["Draft follow-up email", "API documentation review", "Integration code"],
    humanRequirements: ["Vendor communication", "Credential management", "Production deployment"],
  },
  daily: {
    automationType: "llm",
    automationReason: "Automated report generation from data sources",
    isBlocked: false,
    blockageReason: null,
    steps: [
      "Fetch latest data from all sources",
      "Analyze trends and anomalies",
      "Generate narrative summary",
      "Format as structured report",
      "Deliver via configured channels",
    ],
    estimatedMinutes: 5,
    aiCapabilities: ["Data aggregation", "Trend analysis", "Report writing", "Automated delivery"],
    humanRequirements: [],
  },
};

// Analyze first 10 tasks with demo data
let analyzed = 0;
for (let i = 0; i < Math.min(10, data.tasks.length); i++) {
  const task = data.tasks[i];

  // Choose analysis type based on task characteristics
  let analysisType = "tech";

  if (task.title.toLowerCase().includes("call") || task.title.toLowerCase().includes("meeting")) {
    analysisType = "property";
  } else if (
    task.title.toLowerCase().includes("research") ||
    task.title.toLowerCase().includes("analysis")
  ) {
    analysisType = "research";
  } else if (
    task.title.toLowerCase().includes("brief") ||
    task.title.toLowerCase().includes("report") ||
    task.title.toLowerCase().includes("daily")
  ) {
    analysisType = "daily";
  } else if (
    task._original?.wasBlocked ||
    task.title.toLowerCase().includes("blocked") ||
    task.title.toLowerCase().includes("waiting")
  ) {
    analysisType = "blocked";
  } else if (task.category === "CopperAI") {
    analysisType = "tech";
  }

  task.analysis = { ...demoAnalyses[analysisType] };

  console.log(`✅ ${task.title.substring(0, 60)} → ${task.analysis.automationType.toUpperCase()}`);
  analyzed++;
}

// Save
data.meta.lastAnalysis = new Date().toISOString();
data.meta.analysisVersion = "1.0-demo";
data.meta.demoAnalysisNote =
  "First 10 tasks have demo analysis. Run analyze-tasks.cjs with ANTHROPIC_API_KEY to analyze all tasks.";

fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));

console.log(`\n✅ Added demo analysis to ${analyzed} tasks`);
console.log("\n📊 Demo includes examples of:");
console.log("   🤖 LLM: Fully automated tasks (research, reports)");
console.log("   🤝 Hybrid: AI assists, human reviews (coding)");
console.log("   👤 Human: Requires human interaction (calls)");
console.log("   🚫 Blocked: Waiting on dependencies");
console.log("\n💡 To analyze all 85 tasks with AI:");
console.log("   export ANTHROPIC_API_KEY=your-key");
console.log("   node scripts/analyze-tasks.cjs");

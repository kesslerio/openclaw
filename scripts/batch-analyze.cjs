#!/usr/bin/env node
/**
 * Batch AI Task Analyzer - Applies intelligent analysis to all unanalyzed tasks
 */

const fs = require("fs");
const DATA_PATH = "./tools/kanban/data/kanban.json";

console.log("🤖 Batch AI Task Analyzer\n");

// Load tasks
const data = JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
console.log(`📦 Loaded ${data.tasks.length} tasks\n`);

// Analysis rules based on task patterns
function analyzeTask(task) {
  const title = task.title.toLowerCase();
  const desc = (task.description || "").toLowerCase();
  const category = task.category;
  const combined = `${title} ${desc}`;

  // LLM-AUTOMATABLE patterns
  const llmPatterns = [
    /morning brief/i,
    /daily.*report/i,
    /research/i,
    /monitoring/i,
    /auto-?publish/i,
    /autonomous.*manager/i,
    /email.*monitoring/i,
    /heartbeat.*review/i,
    /flight.*price/i,
    /vibe coding/i,
    /competitive.*landscape/i,
    /documentation/i,
    /sync.*directory/i,
    /transcript/i,
    /setup.*cron/i,
    /model.*tiering/i,
  ];

  // HUMAN-REQUIRED patterns
  const humanPatterns = [
    /call\s/i,
    /phone/i,
    /meeting/i,
    /pay.*bill/i,
    /payment/i,
    /deposit/i,
    /check.*deposit/i,
    /rent.*payment/i,
    /dental/i,
    /buy\s/i,
    /purchase/i,
    /login.*to/i,
    /sign.*up/i,
    /in-?person/i,
    /physical/i,
  ];

  // BLOCKED patterns
  const blockedPatterns = [
    /waiting.*on/i,
    /blocked.*by/i,
    /awaiting/i,
    /unreachable/i,
    /pending.*approval/i,
  ];

  // Check for blocked first
  if (blockedPatterns.some((p) => p.test(combined))) {
    return {
      automationType: "blocked",
      automationReason: "Task is waiting on external dependency or approval",
      isBlocked: true,
      blockageReason: extractBlockageReason(combined),
      steps: ["Identify blocker", "Follow up on dependency", "Resume when unblocked"],
      estimatedMinutes: 15,
      aiCapabilities: ["Status tracking", "Follow-up reminders"],
      humanRequirements: ["Resolve dependency", "Make decision"],
    };
  }

  // Check for human-required
  if (humanPatterns.some((p) => p.test(combined))) {
    return {
      automationType: "human",
      automationReason: getHumanReason(combined),
      isBlocked: false,
      blockageReason: null,
      steps: getHumanSteps(task),
      estimatedMinutes: getEstimatedTime(task, "human"),
      aiCapabilities: getAICapabilities(task, "human"),
      humanRequirements: getHumanRequirements(task, "human"),
    };
  }

  // Check for LLM-automatable
  if (llmPatterns.some((p) => p.test(combined))) {
    return {
      automationType: "llm",
      automationReason:
        "Task involves data processing, research, or automated workflows that AI can handle independently",
      isBlocked: false,
      blockageReason: null,
      steps: getLLMSteps(task),
      estimatedMinutes: getEstimatedTime(task, "llm"),
      aiCapabilities: getAICapabilities(task, "llm"),
      humanRequirements: ["Review output", "Approve if needed"],
    };
  }

  // Default to hybrid for most tasks
  return {
    automationType: "hybrid",
    automationReason:
      "AI can assist with research, drafting, and execution, but human review/approval needed",
    isBlocked: false,
    blockageReason: null,
    steps: getHybridSteps(task),
    estimatedMinutes: getEstimatedTime(task, "hybrid"),
    aiCapabilities: getAICapabilities(task, "hybrid"),
    humanRequirements: getHumanRequirements(task, "hybrid"),
  };
}

function extractBlockageReason(text) {
  if (/unreachable/i.test(text)) return "Resource or system unreachable";
  if (/awaiting/i.test(text)) return "Awaiting external input or response";
  if (/waiting/i.test(text)) return "Waiting on dependency";
  return "External blocker present";
}

function getHumanReason(text) {
  if (/call/i.test(text)) return "Requires phone call - human interaction needed";
  if (/meeting/i.test(text)) return "In-person or video meeting required";
  if (/payment|pay.*bill|deposit/i.test(text))
    return "Financial transaction requires human authorization";
  if (/buy|purchase/i.test(text)) return "Purchase decision requires human judgment";
  if (/login/i.test(text)) return "Requires secure login with human credentials";
  return "Task requires direct human action";
}

function getHumanSteps(task) {
  const title = task.title.toLowerCase();
  if (/call/i.test(title)) {
    return ["Prepare talking points", "Make phone call", "Document outcome", "Follow up if needed"];
  }
  if (/payment|deposit/i.test(title)) {
    return [
      "Log into banking/payment portal",
      "Verify amount",
      "Execute transaction",
      "Save confirmation",
    ];
  }
  if (/meeting/i.test(title)) {
    return ["Prepare agenda/materials", "Attend meeting", "Take notes", "Send follow-up"];
  }
  if (/buy|purchase/i.test(title)) {
    return ["Research options", "Compare prices", "Make purchase decision", "Complete transaction"];
  }
  return [
    "Review task requirements",
    "Take required action",
    "Verify completion",
    "Document results",
  ];
}

function getLLMSteps(task) {
  const title = task.title.toLowerCase();
  if (/brief|report/i.test(title)) {
    return [
      "Gather data from sources",
      "Analyze and synthesize",
      "Generate formatted report",
      "Deliver to recipient",
    ];
  }
  if (/monitoring/i.test(title)) {
    return [
      "Check data sources",
      "Compare against thresholds",
      "Generate alerts if needed",
      "Log status",
    ];
  }
  if (/research/i.test(title)) {
    return ["Define research scope", "Gather information", "Analyze findings", "Compile report"];
  }
  return [
    "Parse task requirements",
    "Execute automated workflow",
    "Validate output",
    "Report completion",
  ];
}

function getHybridSteps(task) {
  const title = task.title.toLowerCase();
  if (/deploy/i.test(title)) {
    return [
      "AI prepares deployment",
      "Human reviews configuration",
      "Execute deployment",
      "Verify success",
    ];
  }
  if (/integration/i.test(title)) {
    return [
      "AI builds integration code",
      "Human reviews and tests",
      "Deploy to staging",
      "Human approves production",
    ];
  }
  if (/recruit|outreach/i.test(title)) {
    return [
      "AI drafts outreach messages",
      "Human personalizes and sends",
      "Track responses",
      "Human conducts conversations",
    ];
  }
  return [
    "AI researches and drafts",
    "Human reviews approach",
    "AI executes with guidance",
    "Human validates result",
  ];
}

function getEstimatedTime(task, type) {
  const title = task.title.toLowerCase();

  if (type === "llm") {
    if (/brief/i.test(title)) return 5;
    if (/monitoring/i.test(title)) return 2;
    if (/research/i.test(title)) return 15;
    return 10;
  }

  if (type === "human") {
    if (/call/i.test(title)) return 30;
    if (/meeting/i.test(title)) return 60;
    if (/payment|deposit/i.test(title)) return 15;
    if (/buy/i.test(title)) return 45;
    return 30;
  }

  // hybrid
  if (/deploy/i.test(title)) return 45;
  if (/integration/i.test(title)) return 90;
  if (/fix/i.test(title)) return 30;
  return 45;
}

function getAICapabilities(task, type) {
  if (type === "llm") {
    return ["Data aggregation", "Report generation", "Automated execution", "Status monitoring"];
  }
  if (type === "human") {
    return ["Research assistance", "Script preparation", "Documentation", "Follow-up reminders"];
  }
  // hybrid
  return ["Code generation", "Research", "Draft preparation", "Testing assistance"];
}

function getHumanRequirements(task, type) {
  if (type === "human") {
    const title = task.title.toLowerCase();
    if (/call/i.test(title)) return ["Phone conversation", "Decision making"];
    if (/payment/i.test(title)) return ["Account access", "Transaction approval"];
    if (/meeting/i.test(title)) return ["Attendance", "Discussion participation"];
    return ["Direct action", "Verification"];
  }
  // hybrid
  return ["Review", "Approval", "Final decision"];
}

// Process all tasks
let analyzed = 0;
let skipped = 0;

for (const task of data.tasks) {
  // Skip if already has real analysis (not demo)
  if (
    task.analysis &&
    task.analysis.automationReason &&
    !task.analysis.automationReason.includes("demo")
  ) {
    skipped++;
    continue;
  }

  const analysis = analyzeTask(task);
  task.analysis = analysis;
  analyzed++;

  const icons = {
    llm: "🤖",
    human: "👤",
    hybrid: "🤝",
    blocked: "🚫",
  };

  console.log(`${icons[analysis.automationType]} ${task.title.substring(0, 60)}`);
}

// Calculate stats
const stats = { llm: 0, human: 0, hybrid: 0, blocked: 0 };
data.tasks.forEach((task) => {
  if (task.analysis) {
    stats[task.analysis.automationType]++;
  }
});

console.log(`\n✅ Analysis complete!`);
console.log(`   Analyzed: ${analyzed} tasks`);
console.log(`   Skipped (already done): ${skipped} tasks`);

console.log(`\n📊 Automation Breakdown:`);
console.log(`   🤖 LLM (Fully Automated):  ${stats.llm} tasks`);
console.log(`   🤝 Hybrid (AI + Human):    ${stats.hybrid} tasks`);
console.log(`   👤 Human Required:         ${stats.human} tasks`);
console.log(`   🚫 Blocked:                ${stats.blocked} tasks`);

// Update metadata and save
data.meta = data.meta || {};
data.meta.lastAnalysis = new Date().toISOString();
data.meta.analysisVersion = "2.0-batch";

fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
console.log(`\n💾 Saved to: ${DATA_PATH}`);

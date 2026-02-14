#!/usr/bin/env node
/**
 * Copper AI Metrics Tracker
 * Track key business metrics: customers, revenue, calls, retention
 * Usage: node copper-metrics-tracker.js [add|report|goals]
 */

const fs = require("fs");
const path = require("path");

const metricsFile = path.join(__dirname, "..", "data", "copper-metrics.json");

// Initialize metrics file if doesn't exist
function initMetrics() {
  const dataDir = path.join(__dirname, "..", "data");
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  if (!fs.existsSync(metricsFile)) {
    const initialData = {
      customers: [],
      revenue: [],
      calls: [],
      goals: {
        "2026-Q1": {
          customers: 50,
          arr: 180000, // $180k ARR
          calls: 150000,
          churnRate: 5,
        },
        "2026-Q2": {
          customers: 150,
          arr: 540000,
          calls: 450000,
          churnRate: 5,
        },
        "2026-Q3": {
          customers: 300,
          arr: 1080000,
          calls: 900000,
          churnRate: 5,
        },
        "2026-Q4": {
          customers: 500,
          arr: 1800000,
          calls: 1500000,
          churnRate: 5,
        },
      },
      notes: [],
    };
    fs.writeFileSync(metricsFile, JSON.stringify(initialData, null, 2));
  }

  return JSON.parse(fs.readFileSync(metricsFile, "utf8"));
}

function saveMetrics(data) {
  fs.writeFileSync(metricsFile, JSON.stringify(data, null, 2));
}

function addMetric(type, value, date = new Date().toISOString().split("T")[0]) {
  const data = initMetrics();

  if (!data[type]) {
    console.error(`Invalid metric type: ${type}`);
    console.log("Valid types: customers, revenue, calls, notes");
    return;
  }

  const entry = {
    date,
    value: parseFloat(value),
    timestamp: new Date().toISOString(),
  };

  data[type].push(entry);
  saveMetrics(data);

  console.log(`✅ Added ${type} metric: ${value} on ${date}`);
}

function generateReport() {
  const data = initMetrics();
  const today = new Date();
  const currentQuarter = `2026-Q${Math.ceil((today.getMonth() + 1) / 3)}`;

  console.log("=".repeat(80));
  console.log("COPPER AI - BUSINESS METRICS DASHBOARD");
  console.log("=".repeat(80));
  console.log();

  // Current snapshot
  const latestCustomers = data.customers[data.customers.length - 1];
  const latestRevenue = data.revenue[data.revenue.length - 1];
  const latestCalls = data.calls[data.calls.length - 1];

  console.log("📊 CURRENT SNAPSHOT");
  console.log("-".repeat(40));
  if (latestCustomers) {
    console.log(`Customers: ${latestCustomers.value} (as of ${latestCustomers.date})`);
  }
  if (latestRevenue) {
    console.log(`MRR: $${latestRevenue.value.toLocaleString()} (as of ${latestRevenue.date})`);
    console.log(`ARR: $${(latestRevenue.value * 12).toLocaleString()}`);
  }
  if (latestCalls) {
    console.log(`Calls/Month: ${latestCalls.value.toLocaleString()} (as of ${latestCalls.date})`);
  }
  console.log();

  // Goals for current quarter
  const goals = data.goals[currentQuarter];
  if (goals) {
    console.log(`🎯 ${currentQuarter} GOALS`);
    console.log("-".repeat(40));
    console.log(`Target Customers: ${goals.customers}`);
    console.log(`Target ARR: $${goals.arr.toLocaleString()}`);
    console.log(`Target Calls: ${goals.calls.toLocaleString()}/month`);
    console.log(`Max Churn Rate: ${goals.churnRate}%`);
    console.log();

    // Progress vs goals
    if (latestCustomers || latestRevenue) {
      console.log("📈 PROGRESS TO GOAL");
      console.log("-".repeat(40));

      if (latestCustomers) {
        const customerProgress = ((latestCustomers.value / goals.customers) * 100).toFixed(1);
        console.log(
          `Customers: ${latestCustomers.value} / ${goals.customers} (${customerProgress}%)`,
        );
        printProgressBar(latestCustomers.value, goals.customers);
      }

      if (latestRevenue) {
        const arr = latestRevenue.value * 12;
        const arrProgress = ((arr / goals.arr) * 100).toFixed(1);
        console.log(
          `ARR: $${arr.toLocaleString()} / $${goals.arr.toLocaleString()} (${arrProgress}%)`,
        );
        printProgressBar(arr, goals.arr);
      }

      if (latestCalls) {
        const callProgress = ((latestCalls.value / goals.calls) * 100).toFixed(1);
        console.log(
          `Calls: ${latestCalls.value.toLocaleString()} / ${goals.calls.toLocaleString()} (${callProgress}%)`,
        );
        printProgressBar(latestCalls.value, goals.calls);
      }

      console.log();
    }
  }

  // Growth trends
  if (data.customers.length > 1) {
    console.log("📈 GROWTH TRENDS");
    console.log("-".repeat(40));

    const customerGrowth = calculateGrowthRate(data.customers);
    const revenueGrowth = data.revenue.length > 1 ? calculateGrowthRate(data.revenue) : null;
    const callGrowth = data.calls.length > 1 ? calculateGrowthRate(data.calls) : null;

    if (customerGrowth !== null) {
      console.log(
        `Customer Growth: ${customerGrowth > 0 ? "+" : ""}${customerGrowth.toFixed(1)}% MoM`,
      );
    }
    if (revenueGrowth !== null) {
      console.log(
        `Revenue Growth: ${revenueGrowth > 0 ? "+" : ""}${revenueGrowth.toFixed(1)}% MoM`,
      );
    }
    if (callGrowth !== null) {
      console.log(`Call Volume Growth: ${callGrowth > 0 ? "+" : ""}${callGrowth.toFixed(1)}% MoM`);
    }
    console.log();
  }

  // Key Metrics
  if (latestCustomers && latestRevenue && latestCalls) {
    console.log("💰 KEY METRICS");
    console.log("-".repeat(40));

    const arpu = latestRevenue.value / latestCustomers.value;
    const callsPerCustomer = latestCalls.value / latestCustomers.value;

    console.log(`ARPU (Avg Revenue Per User): $${arpu.toFixed(2)}/month`);
    console.log(`Calls per Customer: ${callsPerCustomer.toFixed(0)}/month`);
    console.log(`Revenue per Call: $${(latestRevenue.value / latestCalls.value).toFixed(4)}`);
    console.log();
  }

  // Recent notes
  if (data.notes.length > 0) {
    console.log("📝 RECENT NOTES");
    console.log("-".repeat(40));
    data.notes
      .slice(-5)
      .reverse()
      .forEach((note) => {
        console.log(`[${note.date}] ${note.text}`);
      });
    console.log();
  }

  // Recommendations
  console.log("💡 RECOMMENDATIONS");
  console.log("-".repeat(40));

  if (latestCustomers && goals) {
    const daysInQuarter = 90;
    const daysRemaining = getDaysRemainingInQuarter();
    const customersNeeded = goals.customers - latestCustomers.value;
    const customersPerDay = customersNeeded / daysRemaining;

    if (customersNeeded > 0) {
      console.log(`• Need ${customersNeeded} more customers this quarter`);
      console.log(
        `• Pace: ${customersPerDay.toFixed(1)} customers/day (${(customersPerDay * 7).toFixed(0)}/week)`,
      );
    } else {
      console.log(`✅ Customer goal achieved! Time to raise the bar.`);
    }
  }

  if (latestRevenue && latestCustomers) {
    const arpu = latestRevenue.value / latestCustomers.value;
    if (arpu < 400) {
      console.log(`• ARPU is low ($${arpu.toFixed(0)}) - consider upselling to higher tiers`);
    } else if (arpu > 600) {
      console.log(`✅ Healthy ARPU ($${arpu.toFixed(0)}) - customers seeing value`);
    }
  }

  console.log();
}

function printProgressBar(current, goal, width = 40) {
  const percent = Math.min(current / goal, 1);
  const filled = Math.round(width * percent);
  const empty = width - filled;

  const bar = "█".repeat(filled) + "░".repeat(empty);
  console.log(`  ${bar} ${(percent * 100).toFixed(1)}%`);
}

function calculateGrowthRate(dataPoints) {
  if (dataPoints.length < 2) return null;

  const latest = dataPoints[dataPoints.length - 1];
  const previous = dataPoints[dataPoints.length - 2];

  return ((latest.value - previous.value) / previous.value) * 100;
}

function getDaysRemainingInQuarter() {
  const today = new Date();
  const currentMonth = today.getMonth();
  const quarterEndMonth = Math.ceil((currentMonth + 1) / 3) * 3 - 1;
  const quarterEnd = new Date(today.getFullYear(), quarterEndMonth + 1, 0);

  const diff = quarterEnd - today;
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

function showGoals() {
  const data = initMetrics();

  console.log("=".repeat(80));
  console.log("COPPER AI - 2026 GOALS");
  console.log("=".repeat(80));
  console.log();

  Object.keys(data.goals).forEach((quarter) => {
    const goals = data.goals[quarter];
    console.log(`${quarter}`);
    console.log("-".repeat(40));
    console.log(`  Customers: ${goals.customers}`);
    console.log(`  ARR: $${goals.arr.toLocaleString()}`);
    console.log(`  MRR: $${(goals.arr / 12).toLocaleString()}`);
    console.log(`  Calls/Month: ${goals.calls.toLocaleString()}`);
    console.log(`  Max Churn: ${goals.churnRate}%`);
    console.log();
  });

  console.log("YEAR-END TARGET (2026-Q4)");
  console.log("-".repeat(40));
  const q4 = data.goals["2026-Q4"];
  console.log(`  500 customers`);
  console.log(`  $1.8M ARR`);
  console.log(`  1.5M calls/month`);
  console.log();
}

function addNote(text) {
  const data = initMetrics();
  const note = {
    date: new Date().toISOString().split("T")[0],
    text,
    timestamp: new Date().toISOString(),
  };

  data.notes.push(note);
  saveMetrics(data);

  console.log(`✅ Note added: ${text}`);
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case "add":
    if (args.length < 3) {
      console.log("Usage: node copper-metrics-tracker.js add [type] [value] [date]");
      console.log("Types: customers, revenue, calls");
      console.log("Example: node copper-metrics-tracker.js add customers 52");
      process.exit(1);
    }
    addMetric(args[1], args[2], args[3]);
    break;

  case "note":
    if (args.length < 2) {
      console.log('Usage: node copper-metrics-tracker.js note "Your note here"');
      process.exit(1);
    }
    addNote(args.slice(1).join(" "));
    break;

  case "report":
    generateReport();
    break;

  case "goals":
    showGoals();
    break;

  case "init":
    initMetrics();
    console.log("✅ Metrics tracking initialized");
    break;

  default:
    console.log("Usage: node copper-metrics-tracker.js [command]");
    console.log();
    console.log("Commands:");
    console.log("  add [type] [value]  - Add a metric (customers, revenue, calls)");
    console.log('  note "text"         - Add a note/milestone');
    console.log("  report              - Show metrics dashboard");
    console.log("  goals               - Show 2026 goals");
    console.log("  init                - Initialize metrics tracking");
    console.log();
    console.log("Examples:");
    console.log("  node copper-metrics-tracker.js add customers 52");
    console.log("  node copper-metrics-tracker.js add revenue 24500");
    console.log("  node copper-metrics-tracker.js add calls 50000");
    console.log('  node copper-metrics-tracker.js note "Launched partnership with WellSky"');
    console.log("  node copper-metrics-tracker.js report");
}

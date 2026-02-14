#!/usr/bin/env node
/**
 * Copper AI + ClearCare ROI Calculator
 *
 * Use this tool when pitching pilot agencies to show potential savings.
 *
 * Usage:
 *   node roi-calculator.js --visits 500 --noshow-rate 20 --cost-per-visit 75
 *   node roi-calculator.js --interactive
 *
 * Created: Feb 6, 2026 (Overnight Vibe Coding)
 */

const readline = require("readline");

// Industry benchmarks and Copper AI performance data
const BENCHMARKS = {
  avgNoshowRate: 0.2, // 20% industry average
  copperNoshowReduction: 0.4, // 40% reduction with Copper AI (conservative)
  avgCostPerMissedVisit: 125, // Including caregiver time, travel, rescheduling
  avgVisitsPerMonth: 500, // Mid-size agency
  voiceEvvCompletionLift: 0.25, // 25% improvement in EVV completion
  evvPenaltyPerMiss: 50, // Typical state penalty per missed EVV
  schedulerHoursSaved: 10, // Hours saved per week on scheduling
  hourlySchedulerCost: 25, // Ops manager hourly rate
};

const PRICING = {
  basic: 500, // Per month
  pro: 800, // Per month (includes no-show predictor)
  enterprise: 1500, // Per month (full platform)
};

function calculateROI(params) {
  const {
    visitsPerMonth = BENCHMARKS.avgVisitsPerMonth,
    currentNoshowRate = BENCHMARKS.avgNoshowRate,
    costPerMissedVisit = BENCHMARKS.avgCostPerMissedVisit,
    evvMissRate = 0.15,
    plan = "pro",
  } = params;

  // Current costs
  const currentMissedVisits = visitsPerMonth * currentNoshowRate;
  const currentNoshowCost = currentMissedVisits * costPerMissedVisit;
  const currentEvvPenalties = visitsPerMonth * evvMissRate * BENCHMARKS.evvPenaltyPerMiss;
  const currentSchedulerCost = BENCHMARKS.schedulerHoursSaved * 4 * BENCHMARKS.hourlySchedulerCost; // Monthly

  // With Copper AI
  const reducedNoshowRate = currentNoshowRate * (1 - BENCHMARKS.copperNoshowReduction);
  const newMissedVisits = visitsPerMonth * reducedNoshowRate;
  const newNoshowCost = newMissedVisits * costPerMissedVisit;

  const reducedEvvMissRate = evvMissRate * (1 - BENCHMARKS.voiceEvvCompletionLift);
  const newEvvPenalties = visitsPerMonth * reducedEvvMissRate * BENCHMARKS.evvPenaltyPerMiss;

  const newSchedulerCost = currentSchedulerCost * 0.3; // 70% reduction

  // Savings calculations
  const noshowSavings = currentNoshowCost - newNoshowCost;
  const evvSavings = currentEvvPenalties - newEvvPenalties;
  const schedulerSavings = currentSchedulerCost - newSchedulerCost;
  const totalMonthlySavings = noshowSavings + evvSavings + schedulerSavings;

  const monthlyPlanCost = PRICING[plan];
  const netMonthlySavings = totalMonthlySavings - monthlyPlanCost;
  const annualSavings = netMonthlySavings * 12;
  const roi = (((totalMonthlySavings - monthlyPlanCost) / monthlyPlanCost) * 100).toFixed(0);

  return {
    inputs: {
      visitsPerMonth,
      currentNoshowRate: (currentNoshowRate * 100).toFixed(1) + "%",
      costPerMissedVisit,
      evvMissRate: (evvMissRate * 100).toFixed(1) + "%",
      plan,
    },
    currentState: {
      missedVisitsPerMonth: Math.round(currentMissedVisits),
      monthlyNoshowCost: Math.round(currentNoshowCost),
      monthlyEvvPenalties: Math.round(currentEvvPenalties),
      monthlySchedulerCost: Math.round(currentSchedulerCost),
      totalMonthlyCost: Math.round(currentNoshowCost + currentEvvPenalties + currentSchedulerCost),
    },
    withCopperAI: {
      missedVisitsPerMonth: Math.round(newMissedVisits),
      monthlyNoshowCost: Math.round(newNoshowCost),
      monthlyEvvPenalties: Math.round(newEvvPenalties),
      monthlySchedulerCost: Math.round(newSchedulerCost),
      totalMonthlyCost: Math.round(newNoshowCost + newEvvPenalties + newSchedulerCost),
    },
    savings: {
      noshowSavings: Math.round(noshowSavings),
      evvSavings: Math.round(evvSavings),
      schedulerSavings: Math.round(schedulerSavings),
      totalMonthlySavings: Math.round(totalMonthlySavings),
      monthlyPlanCost,
      netMonthlySavings: Math.round(netMonthlySavings),
      annualNetSavings: Math.round(annualSavings),
      roiPercent: roi + "%",
    },
  };
}

function formatCurrency(amount) {
  return "$" + amount.toLocaleString();
}

function printReport(results) {
  console.log("\n" + "=".repeat(60));
  console.log("🏥 COPPER AI + CLEARCARE ROI ANALYSIS");
  console.log("=".repeat(60));

  console.log("\n📊 AGENCY PROFILE:");
  console.log(`   Visits/Month: ${results.inputs.visitsPerMonth}`);
  console.log(`   Current No-Show Rate: ${results.inputs.currentNoshowRate}`);
  console.log(`   Cost per Missed Visit: ${formatCurrency(results.inputs.costPerMissedVisit)}`);
  console.log(`   EVV Miss Rate: ${results.inputs.evvMissRate}`);
  console.log(
    `   Selected Plan: ${results.inputs.plan.toUpperCase()} (${formatCurrency(PRICING[results.inputs.plan])}/mo)`,
  );

  console.log("\n📉 CURRENT STATE (Without Copper AI):");
  console.log(`   Missed Visits/Month: ${results.currentState.missedVisitsPerMonth}`);
  console.log(`   No-Show Costs: ${formatCurrency(results.currentState.monthlyNoshowCost)}/mo`);
  console.log(`   EVV Penalties: ${formatCurrency(results.currentState.monthlyEvvPenalties)}/mo`);
  console.log(
    `   Scheduler Overhead: ${formatCurrency(results.currentState.monthlySchedulerCost)}/mo`,
  );
  console.log(`   ─────────────────────────────`);
  console.log(`   TOTAL: ${formatCurrency(results.currentState.totalMonthlyCost)}/mo`);

  console.log("\n📈 WITH COPPER AI:");
  console.log(
    `   Missed Visits/Month: ${results.withCopperAI.missedVisitsPerMonth} (↓${results.currentState.missedVisitsPerMonth - results.withCopperAI.missedVisitsPerMonth})`,
  );
  console.log(`   No-Show Costs: ${formatCurrency(results.withCopperAI.monthlyNoshowCost)}/mo`);
  console.log(`   EVV Penalties: ${formatCurrency(results.withCopperAI.monthlyEvvPenalties)}/mo`);
  console.log(
    `   Scheduler Overhead: ${formatCurrency(results.withCopperAI.monthlySchedulerCost)}/mo`,
  );
  console.log(`   ─────────────────────────────`);
  console.log(`   TOTAL: ${formatCurrency(results.withCopperAI.totalMonthlyCost)}/mo`);

  console.log("\n💰 SAVINGS BREAKDOWN:");
  console.log(`   No-Show Reduction: ${formatCurrency(results.savings.noshowSavings)}/mo`);
  console.log(`   EVV Compliance: ${formatCurrency(results.savings.evvSavings)}/mo`);
  console.log(`   Scheduler Time: ${formatCurrency(results.savings.schedulerSavings)}/mo`);
  console.log(`   ─────────────────────────────`);
  console.log(`   Gross Savings: ${formatCurrency(results.savings.totalMonthlySavings)}/mo`);
  console.log(`   Copper AI Cost: -${formatCurrency(results.savings.monthlyPlanCost)}/mo`);
  console.log(`   ═════════════════════════════`);
  console.log(`   NET SAVINGS: ${formatCurrency(results.savings.netMonthlySavings)}/mo`);
  console.log(`   ANNUAL SAVINGS: ${formatCurrency(results.savings.annualNetSavings)}/yr`);
  console.log(`   ROI: ${results.savings.roiPercent}`);

  console.log("\n" + "=".repeat(60));
  console.log("📞 Ready to start a 30-day pilot? Contact: arvind@copperdigital.com");
  console.log("=".repeat(60) + "\n");
}

async function interactiveMode() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));

  console.log("\n🏥 Copper AI ROI Calculator - Interactive Mode\n");

  const visitsPerMonth = parseInt(await question("Visits per month [500]: ")) || 500;
  const currentNoshowRate =
    (parseFloat(await question("Current no-show rate % [20]: ")) || 20) / 100;
  const costPerMissedVisit = parseInt(await question("Cost per missed visit $ [125]: ")) || 125;
  const evvMissRate = (parseFloat(await question("EVV miss rate % [15]: ")) || 15) / 100;
  const plan = (await question("Plan (basic/pro/enterprise) [pro]: ")).toLowerCase() || "pro";

  rl.close();

  const results = calculateROI({
    visitsPerMonth,
    currentNoshowRate,
    costPerMissedVisit,
    evvMissRate,
    plan,
  });
  printReport(results);
}

// CLI handling
const args = process.argv.slice(2);

if (args.includes("--interactive") || args.includes("-i")) {
  interactiveMode();
} else if (args.includes("--help") || args.includes("-h")) {
  console.log(`
Copper AI + ClearCare ROI Calculator

Usage:
  node roi-calculator.js [options]

Options:
  --visits <n>         Visits per month (default: 500)
  --noshow-rate <n>    Current no-show rate % (default: 20)
  --cost-per-visit <n> Cost per missed visit $ (default: 125)
  --evv-miss-rate <n>  EVV miss rate % (default: 15)
  --plan <type>        Plan: basic, pro, enterprise (default: pro)
  --interactive, -i    Interactive mode
  --json               Output as JSON
  --help, -h           Show this help

Examples:
  node roi-calculator.js --visits 800 --noshow-rate 25 --plan pro
  node roi-calculator.js --interactive
  `);
} else {
  const params = {};

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace("--", "");
    const value = args[i + 1];

    switch (key) {
      case "visits":
        params.visitsPerMonth = parseInt(value);
        break;
      case "noshow-rate":
        params.currentNoshowRate = parseFloat(value) / 100;
        break;
      case "cost-per-visit":
        params.costPerMissedVisit = parseInt(value);
        break;
      case "evv-miss-rate":
        params.evvMissRate = parseFloat(value) / 100;
        break;
      case "plan":
        params.plan = value;
        break;
    }
  }

  const results = calculateROI(params);

  if (args.includes("--json")) {
    console.log(JSON.stringify(results, null, 2));
  } else {
    printReport(results);
  }
}

module.exports = { calculateROI, BENCHMARKS, PRICING };

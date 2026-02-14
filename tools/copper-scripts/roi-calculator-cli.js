#!/usr/bin/env node
/**
 * ROI Calculator CLI for Copper AI
 * Calculate cost savings vs alternatives
 * Usage: node roi-calculator-cli.js --calls 1000 --caregivers 30
 */

function calculateROI(callsPerMonth, caregivers, currentSolution = "answering-service") {
  const avgCallDuration = 3; // minutes
  const totalMinutes = callsPerMonth * avgCallDuration;

  // Copper AI Pricing
  let copperTier, copperPrice;
  if (callsPerMonth <= 500) {
    copperTier = "Starter";
    copperPrice = 297;
  } else if (callsPerMonth <= 1000) {
    copperTier = "Growth";
    copperPrice = 497;
  } else if (callsPerMonth <= 2500) {
    copperTier = "Pro";
    copperPrice = 797;
  } else {
    copperTier = "Enterprise";
    copperPrice = 1200; // estimated
  }

  // Alternative costs
  const costs = {
    "answering-service": {
      monthly: 2500,
      setup: 500,
      name: "Answering Service",
      breakdown: [
        `Base fee: $2,000`,
        `After-hours premium: $300`,
        `Holiday coverage: $200`,
        `Setup: $500 (one-time)`,
      ],
    },
    "manual-process": {
      monthly: caregivers * 100, // rough estimate: time cost
      setup: 0,
      name: "Manual Calling Process",
      breakdown: [
        `Office staff time: 15 hrs/week × $25/hr = $1,500/mo`,
        `Opportunity cost of lost revenue: $${caregivers * 50}/mo`,
        `No setup cost`,
      ],
    },
    "vapi-ai": {
      monthly: totalMinutes * 0.25 + 500, // platform + dev maintenance
      setup: 1500,
      name: "Vapi AI (DIY)",
      breakdown: [
        `Platform costs: $${(totalMinutes * 0.18).toFixed(0)}`,
        `STT/LLM/TTS: $${(totalMinutes * 0.07).toFixed(0)}`,
        `Developer maintenance: $500/mo`,
        `Setup dev time: $1,500 (one-time)`,
      ],
    },
    "retell-ai": {
      monthly: totalMinutes * 0.22 + 500,
      setup: 1500,
      name: "Retell AI (DIY)",
      breakdown: [
        `Voice + LLM + telephony: $${(totalMinutes * 0.22).toFixed(0)}`,
        `Developer maintenance: $500/mo`,
        `Setup dev time: $1,500 (one-time)`,
      ],
    },
    "dialora-ai": {
      monthly: callsPerMonth <= 1000 ? 197 : 397,
      setup: 0,
      name: "Dialora AI",
      breakdown: [
        `Platform: $${callsPerMonth <= 1000 ? 197 : 397}`,
        `Manual EVV sync: 5 hrs/week × $25/hr = $500/mo`,
        `No EVV integration`,
      ],
    },
  };

  const alternative = costs[currentSolution];
  const alternativeMonthly = alternative.monthly;
  const alternativeSetup = alternative.setup;

  // Calculate savings
  const monthlySavings = alternativeMonthly - copperPrice;
  const firstMonthSavings = alternativeMonthly + alternativeSetup - (copperPrice + 0); // Copper has no setup fee
  const annualSavings = monthlySavings * 12;
  const roi = ((annualSavings / (copperPrice * 12)) * 100).toFixed(0);

  // Time savings (for manual process)
  const timeSavedPerWeek = 15; // hours
  const timeSavedPerMonth = timeSavedPerWeek * 4;
  const timeSavedAnnual = timeSavedPerMonth * 12;

  // No-show impact
  const avgNoShowRate = 0.2; // 20%
  const avgShiftValue = 120;
  const shiftsPerMonth = callsPerMonth; // assume 1:1 calls to shifts
  const currentNoShowCost = shiftsPerMonth * avgNoShowRate * avgShiftValue;
  const reducedNoShowRate = 0.08; // 8% (60% reduction)
  const newNoShowCost = shiftsPerMonth * reducedNoShowRate * avgShiftValue;
  const noShowSavings = currentNoShowCost - newNoShowCost;

  return {
    copperTier,
    copperPrice,
    alternative: alternative.name,
    alternativeMonthly,
    alternativeSetup,
    alternativeBreakdown: alternative.breakdown,
    monthlySavings,
    firstMonthSavings,
    annualSavings,
    roi,
    timeSavedPerMonth,
    timeSavedAnnual,
    noShowSavings,
    totalMonthlySavings: monthlySavings + noShowSavings,
  };
}

function printROI(result) {
  console.log(`
===============================================================================
COPPER AI ROI CALCULATOR
===============================================================================

Your Inputs:
  • Calls per month: ${result.callsPerMonth || "N/A"}
  • Caregivers: ${result.caregivers || "N/A"}
  • Current solution: ${result.alternative}

===============================================================================
PRICING COMPARISON
===============================================================================

COPPER AI:
  • Recommended tier: ${result.copperTier}
  • Monthly cost: $${result.copperPrice}
  • Setup fee: $0
  • Annual cost: $${result.copperPrice * 12}

${result.alternative.toUpperCase()}:
  • Monthly cost: $${result.alternativeMonthly}
  • Setup fee: $${result.alternativeSetup}
  • Annual cost: $${result.alternativeMonthly * 12 + result.alternativeSetup}

Cost Breakdown:
${result.alternativeBreakdown.map((line) => `  ${line}`).join("\n")}

===============================================================================
SAVINGS ANALYSIS
===============================================================================

COST SAVINGS:
  • First month savings: $${result.firstMonthSavings}
  • Monthly savings (ongoing): $${result.monthlySavings}
  • Annual savings: $${result.annualSavings}
  • ROI: ${result.roi}%

TIME SAVINGS:
  • Hours saved per month: ${result.timeSavedPerMonth} hours
  • Annual time savings: ${result.timeSavedAnnual} hours
  • Value at $25/hr: $${result.timeSavedPerMonth * 25}/mo ($${result.timeSavedAnnual * 25}/year)

NO-SHOW REDUCTION (Estimated):
  • Current no-show cost: $${result.noShowSavings + (result.callsPerMonth || 0) * 0.08 * 120}/mo
  • After Copper AI: $${(result.callsPerMonth || 0) * 0.08 * 120}/mo
  • Monthly savings: $${result.noShowSavings}
  • Annual savings: $${result.noShowSavings * 12}

===============================================================================
TOTAL VALUE
===============================================================================

Total Monthly Savings:
  • Cost difference: $${result.monthlySavings}
  • No-show reduction: $${result.noShowSavings}
  • TOTAL: $${result.totalMonthlySavings}/month

Total Annual Value:
  • Cost savings: $${result.annualSavings}
  • No-show savings: $${result.noShowSavings * 12}
  • Time savings value: $${result.timeSavedAnnual * 25}
  • TOTAL: $${result.annualSavings + result.noShowSavings * 12 + result.timeSavedAnnual * 25}/year

Payback Period: ${result.copperPrice / result.totalMonthlySavings < 1 ? "Less than 1 month" : Math.ceil(result.copperPrice / result.totalMonthlySavings) + " months"}

===============================================================================
RECOMMENDATION
===============================================================================

Based on ${result.callsPerMonth || "your"} calls/month, we recommend:

  ✅ Copper AI ${result.copperTier} Plan - $${result.copperPrice}/month

What you get:
  • 24/7 AI voice agent
  • ${result.copperTier === "Starter" ? "500" : result.copperTier === "Growth" ? "1,000" : result.copperTier === "Pro" ? "2,500" : "Unlimited"} calls/month included
  • EVV integration (WellSky, Axxess, ClearCare, Sandata)
  • White-glove setup (7-10 days)
  • No setup fees
  • Month-to-month (cancel anytime)
  • 30-day money-back guarantee

Next Step: Book a 15-minute demo
→ copperdigital.com/demo

===============================================================================
`);
}

// CLI
const args = process.argv.slice(2);

if (args.length === 0 || args.includes("--help")) {
  console.log(`
Usage: node roi-calculator-cli.js [options]

Options:
  --calls [number]       Number of calls per month
  --caregivers [number]  Number of caregivers
  --compare [solution]   What to compare against

Compare options:
  answering-service (default)
  manual-process
  vapi-ai
  retell-ai
  dialora-ai

Examples:
  node roi-calculator-cli.js --calls 1000 --caregivers 30
  node roi-calculator-cli.js --calls 500 --compare manual-process
  node roi-calculator-cli.js --calls 2000 --caregivers 50 --compare vapi-ai
`);
  process.exit(0);
}

// Parse arguments
let callsPerMonth = 1000; // default
let caregivers = 30; // default
let currentSolution = "answering-service"; // default

for (let i = 0; i < args.length; i += 2) {
  const key = args[i];
  const value = args[i + 1];

  if (key === "--calls") callsPerMonth = parseInt(value);
  if (key === "--caregivers") caregivers = parseInt(value);
  if (key === "--compare") currentSolution = value;
}

const result = calculateROI(callsPerMonth, caregivers, currentSolution);
result.callsPerMonth = callsPerMonth;
result.caregivers = caregivers;

printROI(result);

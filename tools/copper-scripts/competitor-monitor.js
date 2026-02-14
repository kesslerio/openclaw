#!/usr/bin/env node
/**
 * Competitor Monitoring Script for Copper AI
 * Tracks pricing, features, and news from competitors
 * Usage: node competitor-monitor.js [check|report|add]
 */

const fs = require("fs");
const path = require("path");

const competitorDB = {
  "vapi-ai": {
    name: "Vapi AI",
    website: "https://vapi.ai",
    pricing: {
      platform: 0.05, // per minute
      advertised: "$0.05/min",
      actual: "$0.18-0.33/min (with all services)",
      model: "usage-based + multi-vendor stack",
      enterprise: "$40,000-70,000/year",
      lastUpdated: "2026-01-31",
    },
    strengths: [
      "Sub-500ms latency (industry-leading)",
      "Modular (bring your own STT/LLM/TTS)",
      "Excellent API documentation",
      "Strong developer brand",
    ],
    weaknesses: [
      "Hidden costs (6x advertised rate)",
      "Requires technical expertise",
      "No all-inclusive option",
      "Discord-only support (unless enterprise)",
    ],
    targetMarket: "Developer teams building custom voice products",
    monitorUrls: ["https://vapi.ai/pricing", "https://docs.vapi.ai", "https://twitter.com/vapi_ai"],
    threatLevel: "MEDIUM",
    notes: "Different buyer persona (devs vs agency owners), but strong healthcare presence",
  },

  "retell-ai": {
    name: "Retell AI",
    website: "https://retellai.com",
    pricing: {
      base: 0.07 - 0.08, // per minute voice
      llm: 0.003 - 0.08, // per minute LLM
      telephony: 0.015, // per minute US
      total: "$0.13-0.31/min typical",
      freeTier: "$10 credits, 20 concurrent calls",
      enterprise: ">$3k/month volume",
      lastUpdated: "2026-01-31",
    },
    strengths: [
      "Transparent pay-as-you-go pricing",
      "Healthcare implementation guides",
      "White-glove service (enterprise)",
      "No platform fees",
    ],
    weaknesses: [
      "Developer-focused (not SMB)",
      "Support via Discord/email only (free tier)",
      "Still requires vendor management",
    ],
    targetMarket: "Developers, technical teams",
    monitorUrls: [
      "https://retellai.com/pricing",
      "https://docs.retellai.com",
      "https://twitter.com/retellai",
    ],
    threatLevel: "MEDIUM",
    notes: "Honest pricing, healthcare focus, but technical barrier to entry",
  },

  "dialora-ai": {
    name: "Dialora AI",
    website: "https://dialora.ai",
    pricing: {
      starter: 97, // monthly
      model: "Flat-rate all-inclusive",
      includes: "Premium voices, LLMs, transcription, CRM integrations",
      lastUpdated: "2026-01-29",
    },
    strengths: [
      "True all-inclusive pricing",
      "No coding required",
      "Industry templates (healthcare)",
      "Fast deployment (days not weeks)",
    ],
    weaknesses: [
      "Generic templates (not vertical-specific)",
      "Horizontal platform (not home health only)",
    ],
    targetMarket: "Small businesses without dev teams",
    monitorUrls: ["https://dialora.ai/pricing", "https://dialora.ai/blog"],
    threatLevel: "HIGH",
    notes: "CLOSEST COMPETITOR - similar positioning, could go vertical",
  },

  "bland-ai": {
    name: "Bland AI",
    website: "https://bland.ai",
    pricing: {
      perMinute: 0.09,
      outboundMin: 0.015, // per call <10 sec
      transfers: 0.025, // per minute for Bland numbers
      plans: {
        start: { price: 0, daily: 100, concurrent: 10 },
        build: { price: 299, daily: 2000, concurrent: 50 },
        scale: { price: 499, daily: 5000, concurrent: 100 },
      },
      lastUpdated: "2026-01-31",
    },
    strengths: [
      "Voice cloning",
      "Programmable call flows",
      "HIPAA-compliant",
      "High call volumes supported",
    ],
    weaknesses: [
      "More expensive than advertised ($200-300+/mo)",
      "Requires developers",
      "Voice-only (no multichannel)",
    ],
    targetMarket: "Developer teams, high-volume sales/healthcare teams",
    monitorUrls: [
      "https://bland.ai/pricing",
      "https://docs.bland.ai",
      "https://twitter.com/bland_ai",
    ],
    threatLevel: "MEDIUM",
    notes: "Developer-focused, expensive, but healthcare traction",
  },

  "aircall-ai": {
    name: "Aircall AI",
    website: "https://aircall.io",
    pricing: {
      payAsYouGo: 0.49, // per minute
      plans: {
        essentials: { price: 40, minUsers: 3 },
        professional: { price: 70, minUsers: 3 },
        custom: { minUsers: 25 },
      },
      lastUpdated: "2026-01-30",
    },
    strengths: [
      "Mature enterprise platform",
      "Deep CRM integrations (200+)",
      "Plug-and-play setup",
      "Healthcare compliance features",
    ],
    weaknesses: [
      "Requires phone system subscription",
      "3-user minimum on all plans",
      "Expensive per-minute pricing ($0.49/min)",
      "No outbound AI calling yet",
    ],
    targetMarket: "SMB to mid-market teams (3-100+ users)",
    monitorUrls: ["https://aircall.io/pricing", "https://aircall.io/blog"],
    threatLevel: "MEDIUM",
    notes: "Phone system add-on, 3-user min excludes solo agencies",
  },
};

function checkPricing() {
  console.log("=".repeat(80));
  console.log("COPPER AI - COMPETITIVE PRICING MONITOR");
  console.log("=".repeat(80));
  console.log();

  Object.keys(competitorDB).forEach((key) => {
    const competitor = competitorDB[key];
    console.log(`\n${competitor.name}`);
    console.log("-".repeat(40));
    console.log(`Pricing Model: ${competitor.pricing.model || "N/A"}`);

    if (competitor.pricing.advertised) {
      console.log(`Advertised: ${competitor.pricing.advertised}`);
    }
    if (competitor.pricing.actual) {
      console.log(`Actual: ${competitor.pricing.actual}`);
    }
    if (competitor.pricing.starter || competitor.pricing.plans) {
      console.log(
        `Plans: ${JSON.stringify(competitor.pricing.plans || { starter: competitor.pricing.starter })}`,
      );
    }

    console.log(`Threat Level: ${competitor.threatLevel}`);
    console.log(`Last Updated: ${competitor.pricing.lastUpdated}`);
  });
}

function generateReport() {
  const reportDate = new Date().toISOString().split("T")[0];

  let report = `# Competitive Intelligence Report
*Generated: ${reportDate}*

## Executive Summary

**Total Competitors Tracked:** ${Object.keys(competitorDB).length}

**Threat Level Breakdown:**
`;

  const threatCounts = {};
  Object.values(competitorDB).forEach((c) => {
    threatCounts[c.threatLevel] = (threatCounts[c.threatLevel] || 0) + 1;
  });

  Object.keys(threatCounts).forEach((level) => {
    report += `- ${level}: ${threatCounts[level]}\n`;
  });

  report += `\n## Pricing Comparison\n\n`;
  report += `| Competitor | Model | Typical Cost | Threat Level |\n`;
  report += `|------------|-------|--------------|---------------|\n`;

  Object.values(competitorDB).forEach((c) => {
    const cost = c.pricing.actual || c.pricing.advertised || c.pricing.starter || "Varies";
    report += `| ${c.name} | ${c.pricing.model || "N/A"} | ${cost} | ${c.threatLevel} |\n`;
  });

  report += `\n## Key Insights\n\n`;

  // Find highest threat
  const highThreats = Object.values(competitorDB).filter((c) => c.threatLevel === "HIGH");
  if (highThreats.length > 0) {
    report += `### ⚠️ High-Threat Competitors\n\n`;
    highThreats.forEach((c) => {
      report += `**${c.name}**\n`;
      report += `- ${c.notes}\n`;
      report += `- Strengths: ${c.strengths.slice(0, 2).join(", ")}\n`;
      report += `- Our counter: ${getCounterStrategy(c)}\n\n`;
    });
  }

  report += `\n## Recommended Actions\n\n`;
  report += `1. **Monitor Dialora closely** - Most similar positioning\n`;
  report += `2. **Emphasize vertical focus** - We're home health ONLY, not generic\n`;
  report += `3. **Pricing advantage** - 50-70% cheaper than most competitors\n`;
  report += `4. **Continue EVV integration** - None of them have deep vertical integrations\n\n`;

  report += `## Monitoring Checklist\n\n`;
  report += `- [ ] Check Dialora pricing monthly (closest competitor)\n`;
  report += `- [ ] Monitor Vapi/Retell for healthcare vertical moves\n`;
  report += `- [ ] Track new entrants via Google Alerts\n`;
  report += `- [ ] Review Twitter/LinkedIn for competitor news\n`;

  return report;
}

function getCounterStrategy(competitor) {
  const strategies = {
    "Dialora AI": "Highlight vertical specialization (home health only) vs their generic templates",
    "Vapi AI": "Emphasize simplicity (no dev needed) and transparent pricing (no hidden fees)",
    "Retell AI": "Focus on all-inclusive model vs their multi-vendor complexity",
    "Bland AI": "Better pricing and non-technical buyer focus",
    "Aircall AI": "No 3-user minimum, no phone system requirement",
  };

  return strategies[competitor.name] || "Vertical focus + pricing advantage";
}

function saveReport() {
  const report = generateReport();
  const filename = `competitor-report-${new Date().toISOString().split("T")[0]}.md`;
  const filepath = path.join(__dirname, "..", "second-brain", filename);

  fs.writeFileSync(filepath, report);
  console.log(`Report saved to: ${filepath}`);
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case "check":
    checkPricing();
    break;
  case "report":
    console.log(generateReport());
    break;
  case "save":
    saveReport();
    break;
  default:
    console.log("Usage: node competitor-monitor.js [check|report|save]");
    console.log();
    console.log("Commands:");
    console.log("  check  - Quick pricing overview");
    console.log("  report - Generate full competitive intelligence report");
    console.log("  save   - Generate and save report to second-brain/");
}

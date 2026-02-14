#!/usr/bin/env node
/**
 * Sales Call Prep Tool
 * Generates customized prep sheet for sales calls based on prospect info
 * Usage: node sales-call-prep.js --agency "Agency Name" --evv "WellSky" --pain "no-shows"
 */

const prospectProfiles = {
  "small-agency": {
    size: "5-15 caregivers",
    challenges: [
      "Limited budget",
      "Wearing multiple hats",
      "Manual processes everywhere",
      "No IT staff",
    ],
    messaging: [
      "Focus on ROI and time savings",
      "Emphasize ease of setup (7-10 days)",
      "Highlight no developer required",
      "Compare to cost of hiring admin staff",
    ],
    pricing: "Starter tier ($297/mo) is perfect fit",
    objections: [
      '"Too expensive" → Show cost vs hiring part-time admin',
      '"Too complex" → White-glove setup, zero training',
      '"Not ready" → 30-day guarantee, no risk',
    ],
  },
  "medium-agency": {
    size: "15-40 caregivers",
    challenges: [
      "Scaling pains",
      "High no-show rates impacting growth",
      "Office team overwhelmed",
      "Need better systems",
    ],
    messaging: [
      "Focus on scalability",
      "Show how automation enables growth",
      "Emphasize EVV integration (eliminate double entry)",
      "Position as growth enabler, not just cost savings",
    ],
    pricing: "Growth tier ($497/mo) recommended",
    objections: [
      '"Already have a system" → Integration vs replacement',
      '"Need to think about it" → Offer pilot with 5-10 caregivers',
      '"What if it breaks?" → 99.9% uptime SLA',
    ],
  },
  "large-agency": {
    size: "40+ caregivers",
    challenges: [
      "Multi-location complexity",
      "High call volumes",
      "Compliance documentation burden",
      "Staff turnover",
    ],
    messaging: [
      "Enterprise reliability and scale",
      "Compliance and audit trails",
      "Multi-location support",
      "Dedicated success manager",
    ],
    pricing: "Pro tier ($797/mo) or custom Enterprise",
    objections: [
      '"Need vendor approval" → Provide security docs, references',
      '"Integration concerns" → Technical call with our engineers',
      '"Contract terms" → Flexible, can do annual with discount',
    ],
  },
};

const painPointPlaybook = {
  "no-shows": {
    discovery: [
      "What's your current no-show rate?",
      "How much does each no-show cost you?",
      "How are you tracking confirmations now?",
      "What happens when someone doesn't show up?",
    ],
    value: [
      "Reduce no-shows by 60% (industry avg: 20% → 8%)",
      "Catch cancellations 24 hours in advance (time to find coverage)",
      "Automatic escalation to coordinators for issues",
      "Real-time updates to EVV system",
    ],
    demo: [
      "Show outbound call flow (shift confirmation)",
      "Demonstrate EVV sync (real-time update)",
      "Show dashboard (confirmation status at a glance)",
      "Walk through escalation (when AI can't handle it)",
    ],
    roi: "If 20% no-show rate → 8%, save $15k-30k/year in lost revenue",
  },
  "time-savings": {
    discovery: [
      "How many hours per week on confirmation calls?",
      "Who makes those calls?",
      "What could they do instead?",
      "Ever miss confirmations due to being busy?",
    ],
    value: [
      "Save 15-20 hours/week on manual calls",
      "Staff can focus on care coordination, not phone trees",
      "Never miss a confirmation (AI never forgets)",
      "24/7 coverage (even nights and weekends)",
    ],
    demo: [
      "Show automated call schedule",
      "Demonstrate hands-off workflow",
      "Show time-of-day flexibility",
      "Highlight what happens while you sleep",
    ],
    roi: "15 hrs/week saved × $25/hr = $19.5k/year labor savings",
  },
  "evv-integration": {
    discovery: [
      "Which EVV system do you use?",
      "How do you currently sync confirmations?",
      "Double data entry happening?",
      "How long does manual entry take?",
    ],
    value: [
      "Native integration with [their EVV]",
      "Zero double data entry",
      "Real-time sync (no delays)",
      "Automatic updates both directions",
    ],
    demo: [
      "Show EVV connection",
      "Live demo of sync (confirmation → EVV update)",
      "Show bidirectional flow",
      "Demonstrate error handling",
    ],
    roi: "5-10 hrs/week saved on data entry = $6.5k-13k/year",
  },
  compliance: {
    discovery: [
      "When was your last state audit?",
      "What documentation do they require?",
      "How do you prove shifts were confirmed?",
      "Any deficiencies last time?",
    ],
    value: [
      "Automatic audit trail (every call logged)",
      "Timestamps, recordings available",
      "Export reports for auditors",
      "HIPAA-compliant from day one",
    ],
    demo: [
      "Show call logs and timestamps",
      "Demonstrate audit report export",
      "Show HIPAA compliance features",
      "Walk through documentation",
    ],
    roi: "Avoid fines, reduce audit prep time, peace of mind",
  },
};

const evvPlaybook = {
  WellSky: {
    integration: "Native API integration",
    setup: "7-10 days (OAuth authentication)",
    sync: "Real-time bidirectional",
    notes: "Most popular EVV system, we have deep integration experience",
    talking_points: [
      "We've integrated with 20+ WellSky customers",
      "Pull shifts, push confirmations automatically",
      "Works with WellSky ClearCare and Homecare Homebase",
    ],
  },
  Axxess: {
    integration: "Native API integration",
    setup: "7-10 days (API key authentication)",
    sync: "Real-time bidirectional",
    notes: "Fast-growing EVV, especially strong in Texas",
    talking_points: [
      "Growing Axxess customer base",
      "Seamless integration with their scheduling module",
      "Popular with Texas agencies",
    ],
  },
  ClearCare: {
    integration: "Native API integration (now part of WellSky)",
    setup: "7-10 days",
    sync: "Real-time bidirectional",
    notes: "Legacy ClearCare customers (pre-WellSky acquisition)",
    talking_points: [
      "Supporting both legacy ClearCare and new WellSky",
      "Integration unchanged after acquisition",
      "Proven track record",
    ],
  },
  Sandata: {
    integration: "API integration",
    setup: "10-14 days (more complex API)",
    sync: "Near real-time (5-min delay)",
    notes: "Enterprise-focused, more complex integration",
    talking_points: [
      "We support Sandata (though less common in SMB)",
      "Slightly longer setup due to API complexity",
      "Full feature parity once integrated",
    ],
  },
  Other: {
    integration: "Custom integration or CSV sync",
    setup: "2-4 weeks (custom development)",
    sync: "Varies (real-time to hourly)",
    notes: "Less common EVV systems require custom work",
    talking_points: [
      "We can integrate with most EVV systems",
      "May require custom development (2-4 weeks)",
      "CSV upload/download as fallback",
    ],
  },
};

const competitorBattlecard = {
  "answering-service": {
    positioning: "You're comparing apples to AI",
    advantages: [
      "Cost: $297-797 vs $2-3K/month (70% savings)",
      "Consistency: AI never tired, never forgets",
      "Integration: EVV sync vs none",
      "Availability: True 24/7 vs limited hours",
    ],
    objections: {
      prefer_human:
        "I understand. Many customers worried about that too. Reality: caregivers prefer consistent communication over varying quality. AI handles routine confirmations, humans handle complex situations.",
      relationship:
        "The relationship is in the care delivery, not the confirmation calls. Free up your humans for high-value interactions.",
    },
  },
  "vapi-retell": {
    positioning: "Built FOR home health, not adapted TO it",
    advantages: [
      "No developer required vs 40-60 hours of dev work",
      "All-inclusive pricing vs multi-vendor complexity",
      "EVV integration built-in vs custom development",
      "Home health workflows vs generic platform",
    ],
    objections: {
      cheaper_advertised:
        "Vapi advertises $0.05/min, but actual cost is $0.18-0.33/min once you add STT, LLM, TTS, and telephony. Plus 40+ hours of dev time. Our all-in $497/mo includes everything.",
      more_flexible:
        "True, Vapi is more flexible IF you have a dev team. But that flexibility costs time and money. We built for home health specifically so you don't need that flexibility.",
    },
  },
  dialora: {
    positioning: "Vertical focus vs horizontal platform",
    advantages: [
      "Home health ONLY vs generic templates",
      "EVV integration vs none",
      "Compliance features vs basic calling",
      "Industry expertise vs generalist",
    ],
    objections: {
      cheaper:
        "Dialora is $197 vs our $497, but you'll spend 5-10 hrs/week manually syncing to your EVV. At $25/hr, that's $500-1,000/month in labor. Our EVV integration makes us cheaper overall.",
      good_enough:
        "If you're just doing basic calling, Dialora works. But when you need EVV sync, compliance docs, and home health workflows, you'll outgrow it fast.",
    },
  },
};

function generatePrepSheet(options) {
  const { agency, evv, pain, size, competitor } = options;

  let prep = `
===============================================================================
SALES CALL PREP SHEET
===============================================================================

Agency: ${agency || "[Agency Name]"}
EVV System: ${evv || "[Unknown]"}
Primary Pain Point: ${pain || "[Unknown]"}
Agency Size: ${size || "[Unknown]"}
Comparing Against: ${competitor || "Answering service (assumed)"}

===============================================================================
PROSPECT PROFILE
===============================================================================
`;

  // Add size-based profile
  if (size && prospectProfiles[size]) {
    const profile = prospectProfiles[size];
    prep += `
Size: ${profile.size}

Typical Challenges:
${profile.challenges.map((c) => `  • ${c}`).join("\n")}

Messaging Strategy:
${profile.messaging.map((m) => `  ✓ ${m}`).join("\n")}

Recommended Pricing: ${profile.pricing}

Expected Objections:
${profile.objections.map((o) => `  ⚠ ${o}`).join("\n")}
`;
  }

  prep += `
===============================================================================
DISCOVERY QUESTIONS (Ask these first!)
===============================================================================
`;

  // Add pain-specific discovery
  if (pain && painPointPlaybook[pain]) {
    const painbook = painPointPlaybook[pain];
    prep += `
${pain.toUpperCase()} Focus:

${painbook.discovery.map((q, i) => `${i + 1}. ${q}`).join("\n")}

Listen for:
  • Quantify the problem (no-show %, hours spent, etc.)
  • Current workarounds
  • Impact on team morale
  • Budget authority
`;
  }

  prep += `
===============================================================================
VALUE PROPOSITION
===============================================================================
`;

  if (pain && painPointPlaybook[pain]) {
    const painbook = painPointPlaybook[pain];
    prep += `
Key Benefits for ${pain}:

${painbook.value.map((v) => `  ✅ ${v}`).join("\n")}

ROI Calculation:
  ${painbook.roi}
`;
  }

  prep += `
===============================================================================
DEMO FLOW
===============================================================================
`;

  if (pain && painPointPlaybook[pain]) {
    const painbook = painPointPlaybook[pain];
    prep += `
Demo Sequence (15 minutes):

${painbook.demo.map((step, i) => `${i + 1}. ${step} (3 min)`).join("\n")}

Last 3 min: Pricing discussion + next steps
`;
  }

  prep += `
===============================================================================
EVV INTEGRATION TALKING POINTS
===============================================================================
`;

  if (evv && evvPlaybook[evv]) {
    const evvInfo = evvPlaybook[evv];
    prep += `
${evv} Integration:

  • Type: ${evvInfo.integration}
  • Setup Time: ${evvInfo.setup}
  • Sync: ${evvInfo.sync}

Talking Points:
${evvInfo.talking_points.map((tp) => `  → ${tp}`).join("\n")}

Notes: ${evvInfo.notes}
`;
  }

  prep += `
===============================================================================
COMPETITOR POSITIONING
===============================================================================
`;

  if (competitor && competitorBattlecard[competitor]) {
    const battle = competitorBattlecard[competitor];
    prep += `
vs ${competitor.toUpperCase()}:

Positioning: "${battle.positioning}"

Our Advantages:
${battle.advantages.map((adv) => `  ✓ ${adv}`).join("\n")}

Objection Handlers:
`;
    Object.keys(battle.objections).forEach((obj) => {
      prep += `
  "${obj.replace("_", " ")}":
  ${battle.objections[obj]}
`;
    });
  }

  prep += `
===============================================================================
PRICING PRESENTATION
===============================================================================

Recommended Approach:
1. Confirm their pain and desired outcomes
2. Show how Copper AI solves it specifically
3. Present pricing as investment with ROI

Tiers:
  • Starter: $297/mo (500 calls) - Small agencies
  • Growth: $497/mo (1,000 calls) - Most popular
  • Pro: $797/mo (2,500 calls) - Larger agencies
  • Enterprise: Custom - Multi-location

Key Points:
  ✓ All-inclusive (no hidden fees)
  ✓ 30-day money-back guarantee
  ✓ Setup in 7-10 days
  ✓ Month-to-month (cancel anytime)

===============================================================================
CLOSING STRATEGY
===============================================================================

Trial Close Questions:
  • "Does this sound like it would solve [their pain point]?"
  • "Can you see this working for [Agency Name]?"
  • "What concerns do you have about moving forward?"

Next Steps Options:
  1. Sign up today (if ready)
  2. Trial for 30 days (if hesitant)
  3. Technical call (if integration questions)
  4. Speak to reference customer (if need social proof)

CLOSE: "Based on what you've told me about [pain point], I think [tier] is the right fit. We can have you live in 10 days. Should we get started?"

===============================================================================
POST-CALL FOLLOW-UP
===============================================================================

Within 2 hours:
  • Send thank you email
  • Attach demo recording
  • Include pricing summary
  • Add to CRM (track stage)

Day 2:
  • Follow-up email (address any concerns)

Day 7:
  • Check-in if no response

Day 14:
  • Breakup email (last chance)

===============================================================================
NOTES SECTION (Fill in during call)
===============================================================================

Pain Points Mentioned:


Budget: $________

Decision Makers:


Timeline:


Objections Raised:


Next Steps Agreed:


===============================================================================
`;

  return prep;
}

// CLI
const args = process.argv.slice(2);

// Parse arguments
const options = {};
for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace("--", "");
  const value = args[i + 1];
  options[key] = value;
}

if (args.length === 0 || args.includes("--help")) {
  console.log(`
Usage: node sales-call-prep.js [options]

Options:
  --agency "Agency Name"
  --evv "WellSky|Axxess|ClearCare|Sandata|Other"
  --pain "no-shows|time-savings|evv-integration|compliance"
  --size "small-agency|medium-agency|large-agency"
  --competitor "answering-service|vapi-retell|dialora"

Examples:
  node sales-call-prep.js --agency "ABC Home Health" --evv "WellSky" --pain "no-shows"
  node sales-call-prep.js --evv "Axxess" --pain "time-savings" --size "medium-agency"
  node sales-call-prep.js --competitor "dialora" --pain "no-shows"
`);
  process.exit(0);
}

console.log(generatePrepSheet(options));

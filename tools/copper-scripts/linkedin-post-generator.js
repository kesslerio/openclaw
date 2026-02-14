#!/usr/bin/env node
/**
 * LinkedIn Post Generator for Copper AI
 * Generates ready-to-post LinkedIn content based on templates and themes
 * Usage: node linkedin-post-generator.js [theme]
 */

const themes = {
  "no-shows": {
    hook: "20% no-show rate is costing your home health agency $20k-30k per month.",
    body: `Here's the math:
• 100 shifts/week × 20% no-show = 20 lost shifts
• Average shift value: $100-150
• Monthly loss: $8k-12k in revenue
• Plus: Staff frustration, patient dissatisfaction, schedule chaos

The traditional solution? Hire someone to call and confirm every shift.
Cost: $3,000-4,000/month in salary + benefits.

The 2026 solution? AI voice automation.

Copper AI handles shift confirmations 24/7:
✅ Calls caregivers automatically
✅ Confirms shifts in real-time
✅ Syncs with your EVV system
✅ Reduces no-shows by 60%

Cost: $297-797/month (all-inclusive)

Real customer result: No-shows dropped from 20% to 8% in 60 days.
ROI: Saved $18k in the first quarter.`,
    cta: "Ready to stop losing money to no-shows? Let's talk.",
    hashtags: ["#HomeHealth", "#HealthcareAI", "#VoiceAI", "#CareCoordination", "#HealthTech"],
  },

  "time-savings": {
    hook: "Your office manager spends 15 hours a week on the phone. What if they didn't have to?",
    body: `In most home health agencies, someone's full-time job is making calls:
• Shift confirmations (50+ calls/day)
• Patient check-ins
• Appointment scheduling
• Reminder calls

That's 15-20 hours per week of manual dialing.

What could your team do with that time back?
→ Focus on care coordination
→ Build caregiver relationships
→ Improve patient outcomes
→ Actually go home on time

Copper AI automates the phone work:
✅ 24/7 voice agent handles calls
✅ No training required
✅ Integrates with WellSky, Axxess, ClearCare
✅ Saves 15+ hours per week

Real customer quote:
"Before Copper AI, we had two people spending their entire day on confirmation calls. Now those calls happen automatically, and our team focuses on care coordination instead of dialing phones."`,
    cta: "Want your evenings back? Book a 15-min demo.",
    hashtags: [
      "#HomeHealth",
      "#ProductivityHacks",
      "#HealthcareAutomation",
      "#AIforGood",
      "#WorkLifeBalance",
    ],
  },

  "evv-integration": {
    hook: "Your EVV system tracks visits. But who confirms the visits actually happen?",
    body: `Most home health agencies have great EVV systems:
• WellSky
• Axxess
• ClearCare
• Sandata

But EVV doesn't prevent no-shows. It just documents them after the fact.

The missing piece? Proactive confirmation.

Copper AI fills the gap:
1. Pulls tomorrow's shifts from your EVV
2. Calls caregivers 24 hours in advance
3. Confirms (or flags if they can't make it)
4. Syncs results back to your EVV in real-time

No double data entry. No manual tracking. Just automatic, seamless workflow.

Result: 60% fewer no-shows, because you catch issues BEFORE the shift time.`,
    cta: "Using an EVV system? Add AI voice automation in 48 hours.",
    hashtags: ["#EVV", "#HomeHealth", "#HealthcareIT", "#CareCoordination", "#WorkflowAutomation"],
  },

  "cost-comparison": {
    hook: "Answering services charge $2,000-3,000/month. AI voice automation costs $297-797/month. Same service. 70% savings.",
    body: `Let's compare:

**Traditional Answering Service:**
• $2,000-3,000/month
• Human agents (inconsistent quality)
• Limited hours (9am-5pm, maybe 24/7 at premium)
• Slow response times
• No EVV integration
• Annual cost: $24k-36k

**Copper AI:**
• $297-797/month (all-inclusive)
• AI voice agent (consistent, never tired)
• True 24/7 coverage
• Instant responses
• Native EVV integration
• Annual cost: $3.6k-9.6k

**Savings: $15k-27k per year**

And unlike answering services, Copper AI:
✅ Never forgets to make a call
✅ Automatically syncs with your EVV
✅ Learns your workflows
✅ Provides real-time analytics

ROI? Usually positive in the first month.`,
    cta: "Ready to cut costs without cutting quality? Let's chat.",
    hashtags: ["#HomeHealth", "#CostSavings", "#HealthcareAI", "#ROI", "#SmartBusiness"],
  },

  compliance: {
    hook: "State audits are stressful. Copper AI makes compliance documentation automatic.",
    body: `During state audits, you need to prove:
• Shifts were confirmed
• Patients were contacted
• Documentation is complete
• Workflows were followed

Manually tracking all of this? Nightmare.

Copper AI creates an automatic compliance trail:
✅ Every call timestamped and logged
✅ Voice recordings available (HIPAA-compliant)
✅ Confirmation status synced to EVV
✅ Audit reports generated with one click

Real customer story:
"We passed our state audit with zero deficiencies. The auditor was impressed with our confirmation records. Copper AI gave us a 24/7 compliance officer."

When compliance is automatic, you sleep better.`,
    cta: "Next audit coming up? Let's make it easy.",
    hashtags: [
      "#Compliance",
      "#HomeHealth",
      "#HealthcareRegulations",
      "#QualityAssurance",
      "#RiskManagement",
    ],
  },

  "caregiver-experience": {
    hook: "Caregivers don't quit jobs. They quit bad communication.",
    body: `Top reasons caregivers leave agencies:
1. Poor communication
2. Schedule chaos
3. Feeling unappreciated
4. Last-minute changes

Most of these stem from one thing: Bad shift coordination.

When caregivers don't know their schedule:
→ They feel disrespected
→ They can't plan their lives
→ They look for agencies that have it together

Copper AI improves caregiver experience:
✅ Automatic shift confirmations (no more wondering "did they forget me?")
✅ Consistent communication (same voice, same script, every time)
✅ 24/7 availability (call back anytime to confirm or reschedule)
✅ Reduces last-minute chaos

Happy caregivers = Lower turnover = Better patient care.

It's that simple.`,
    cta: "Want to improve caregiver retention? Start with better communication.",
    hashtags: [
      "#CaregiverWellness",
      "#EmployeeRetention",
      "#HomeHealth",
      "#Workforce",
      "#PeopleCentric",
    ],
  },

  "founder-story": {
    hook: "I built Copper AI because my friend runs a home health agency and was drowning in admin work.",
    body: `True story:

A close friend runs a small home health agency in Texas. 15 caregivers, 40 patients, doing amazing work.

But every afternoon, she'd spend 2-3 hours on the phone:
• Confirming tomorrow's shifts
• Rescheduling no-shows
• Chasing caregivers who didn't answer

One day she said: "I became a nurse to help people, not to be a full-time receptionist."

That stuck with me.

I looked at the market:
• Answering services? Too expensive and generic.
• Voice AI platforms? Built for developers, not healthcare.
• Home health-specific tools? Didn't exist.

So I built Copper AI.

Six months later:
✅ 100+ agencies using it
✅ 50,000 calls/month automated
✅ My friend gets her evenings back

If you're stuck on the phone instead of focused on care, let's talk.`,
    cta: "Book a demo. Let's get you back to what you love.",
    hashtags: [
      "#FounderStory",
      "#HomeHealth",
      "#StartupJourney",
      "#HealthcareInnovation",
      "#PurposeDriven",
    ],
  },

  "industry-trends": {
    hook: "By 2027, there will be 1 million unfilled caregiver positions in the US. Automation isn't optional anymore.",
    body: `The home health industry is facing a perfect storm:

📈 Demand is exploding:
• Aging population (10,000 people turn 65 every day)
• Medicare expanding home health coverage
• Shift from institutional to home-based care

📉 Supply is shrinking:
• 1 million unfilled caregiver positions by 2027
• Burnout rates at all-time highs
• Wages can't keep up with demand

The agencies that survive will be the ones that automate.

Not "automate care" (that's impossible and wrong).

Automate the admin work:
✅ Shift confirmations
✅ Scheduling
✅ Documentation
✅ Compliance tracking

This frees humans to do what only humans can do: care for patients.

Copper AI is built for this future.

The question isn't "should we automate?"
It's "can we afford NOT to?"`,
    cta: "Ready to future-proof your agency? Let's talk strategy.",
    hashtags: [
      "#FutureOfWork",
      "#HealthcareTrends",
      "#HomeHealth",
      "#Automation",
      "#WorkforceShortage",
    ],
  },
};

function generatePost(theme) {
  const template = themes[theme];

  if (!template) {
    console.error(`Theme '${theme}' not found.`);
    console.log("\nAvailable themes:");
    Object.keys(themes).forEach((t) => console.log(`  - ${t}`));
    process.exit(1);
  }

  const post = `${template.hook}

${template.body}

${template.cta}

${template.hashtags.join(" ")}`;

  return post;
}

function generateAll() {
  console.log("=".repeat(80));
  console.log("COPPER AI - LINKEDIN POST LIBRARY");
  console.log("=".repeat(80));
  console.log();

  Object.keys(themes).forEach((theme, index) => {
    console.log(`\n${"=".repeat(80)}`);
    console.log(`POST ${index + 1}: ${theme.toUpperCase()}`);
    console.log("=".repeat(80));
    console.log();
    console.log(generatePost(theme));
    console.log();
    console.log(
      `Character count: ${generatePost(theme).length} ${generatePost(theme).length > 3000 ? "⚠️ TOO LONG" : "✅"}`,
    );
  });
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

if (!command || command === "all") {
  generateAll();
} else {
  console.log(generatePost(command));
  console.log();
  console.log(`Character count: ${generatePost(command).length}`);
}

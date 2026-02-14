/**
 * Follow-Up Email (Day 3)
 *
 * Goal: Re-engage non-responders with ROI focus
 */

module.exports = {
  name: "follow-up-day3",
  subject: "Quick follow-up: AI voice agents for [company]",

  body: `Hi [firstName],

Following up on my email about reducing no-shows with AI voice agents.

I know you're busy, so I'll be brief:

**What makes Copper AI different:**
1. Built FOR home health (not a generic chatbot)
2. Works with ClearCare/Axxess out-of-the-box
3. No-show PREDICTOR (not just confirmation calls)
4. Voice-first (40% of caregivers don't have smartphones)

**ROI calculator:** https://copper-ai.example.com/roi
• Enter your agency size → See your savings

Still have 2 pilot spots for February. Can we chat this week?

Best,
Nike

P.S. Our agencies average 9.6:1 ROI (every $1 spent = $9.60 saved).`,

  variables: ["firstName", "company"],

  followUp: {
    day: 7,
    template: "follow-up-day7",
  },
};

/**
 * Final Follow-Up Email (Day 7)
 *
 * Goal: Last chance, urgency-driven
 */

module.exports = {
  name: "follow-up-day7",
  subject: "Last call: February pilot spots closing",

  body: `Hi [firstName],

Last email - promise! 😊

We're launching our pilot program THIS WEEK with 5 home health agencies.

If you're still dealing with no-shows (and the $$$$ they cost), let's talk.

**What you get (free for 60 days):**
• AI voice confirmation calls (2 hours before shift)
• No-show risk prediction (ML-powered)
• EMR integration (auto-sync schedule)
• Weekly ROI reports (see exact $$ saved)

**What we ask:**
• Feedback to improve the product
• A case study if results are good

Only asking for 15 minutes: https://calendly.com/arvindsarin/copper-ai-demo

Best,
Nike

P.S. If no-shows aren't a problem for you, feel free to ignore. No hard feelings!`,

  variables: ["firstName"],

  followUp: null, // End of sequence
};

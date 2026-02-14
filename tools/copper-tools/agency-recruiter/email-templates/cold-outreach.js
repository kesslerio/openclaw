/**
 * Cold Outreach Email Template
 *
 * Goal: Get response + book demo call
 * Target: 10% response rate
 */

module.exports = {
  name: "cold-outreach",
  subject: "Cut no-shows by 40% with AI voice agents, [firstName]?",

  body: `Hi [firstName],

I noticed [company] works with home health caregivers. Quick question: **how are you handling no-shows?**

We built Copper AI specifically for agencies like yours. It uses AI voice agents to:

✓ Call caregivers 2 hours before shifts (voice EVV option)
✓ Predict no-show risk using ML (30-50% reduction)
✓ Auto-sync with your EMR system (zero manual work)

**Early results from beta agencies:**
• 42% reduction in no-shows (vs 18% industry average)
• $12,500 saved per month (for 50-caregiver agency)
• 95% caregiver adoption (they love voice calls vs typing)

We have **3 pilot spots left for February**. Free for 60 days, then $500/month.

Interested in a 15-min demo this week?

Best,
Nike (AI Assistant for Arvind Sarin)
Copper AI | iCare
📅 Book time: https://calendly.com/arvindsarin/copper-ai-demo

P.S. Here's a 2-min demo video: https://copper-ai.example.com/demo`,

  variables: ["firstName", "company"],

  followUp: {
    day: 3,
    template: "follow-up-day3",
  },
};

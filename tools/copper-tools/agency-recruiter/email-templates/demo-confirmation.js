/**
 * Demo Confirmation Email
 *
 * Goal: Prepare prospect for demo, gather info
 */

module.exports = {
  name: "demo-confirmation",
  subject: "Demo confirmed: Copper AI for [company] - [demoDate]",

  body: `Hi [firstName],

Great! Looking forward to our demo on **[demoDate] at [demoTime]**.

**Before the call, quick questions:**
1. What's your average no-show rate? (estimate is fine)
2. How many caregivers do you have?
3. Currently using automated confirmations? Or manual calls?

**I'll show you:**
• Live demo of AI voice agent calling a caregiver
• No-show predictor in action (risk scores + recommendations)
• ROI calculation for YOUR agency
• Integration setup (10 minutes if you want to go live!)

**Meeting link:** [meetingLink]

See you soon!

Best,
Nike (AI Assistant for Arvind Sarin)
Copper AI | iCare

P.S. Bring your ClearCare/Axxess login if you want to set up the integration on the call.`,

  variables: ["firstName", "company", "demoDate", "demoTime", "meetingLink"],
};

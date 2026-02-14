#!/usr/bin/env node
/**
 * Email Campaign Generator for Copper AI
 * Generates personalized email sequences for different customer segments
 * Usage: node email-campaign-generator.js [segment] [--preview]
 */

const segments = {
  "cold-outreach": {
    name: "Cold Outreach - Home Health Agencies",
    emails: [
      {
        day: 0,
        subject: "Quick question about [Agency Name]'s shift confirmations",
        body: `Hi {{firstName}},

I came across {{agencyName}} while researching home health agencies in {{city}}.

Quick question: How much time does your team spend on shift confirmation calls each week?

Most agencies we work with say 15-20 hours. That's nearly half a full-time employee just dialing phones.

We built Copper AI to solve this. It's voice automation specifically for home health—handles shift confirmations, patient scheduling, and check-ins 24/7.

**Real results from agencies like yours:**
• 60% fewer no-shows
• 15+ hours/week saved
• $18k-30k annual savings vs answering services

Worth a 15-minute conversation?

Best,
Arvind Sarin
Founder, Copper Digital
copperdigital.com`,
      },
      {
        day: 3,
        subject: "Re: Shift confirmations at [Agency Name]",
        body: `Hi {{firstName}},

Following up on my note from Tuesday about automating shift confirmations at {{agencyName}}.

I'm guessing you're busy (that's why automation matters!), so I'll keep this brief:

**If you're spending >10 hours/week on confirmation calls**, Copper AI can cut that to near-zero.

**If your no-show rate is >10%**, we can help you drop it by 60%.

**If you're paying $2,000+/month for an answering service**, we're 70% cheaper and better integrated with EVV systems.

Not sure if any of those apply to {{agencyName}}, but if they do, let's chat for 15 minutes.

No pressure. Just an offer to show you what's possible.

Best,
Arvind

P.S. - We integrate directly with {{evvSystem}}. Setup takes 48 hours, not weeks.`,
      },
      {
        day: 7,
        subject: "[Agency Name] + Copper AI = 60% fewer no-shows?",
        body: `Hi {{firstName}},

Last email from me (promise!).

I've reached out a couple times about automating shift confirmations at {{agencyName}}.

If this isn't a priority right now, no worries—I'll stop bothering you.

But if you're curious, here's what you'd get from a 15-min demo:

✅ See how Copper AI handles shift confirmations live
✅ Calculate your ROI (usually $15k-30k/year savings)
✅ Ask questions about EVV integration with {{evvSystem}}
✅ No commitment, just info

Click here to grab a time: [calendar link]

Or let me know you're not interested and I'll remove you from my list.

Thanks for your time,
Arvind`,
      },
      {
        day: 14,
        subject: "Breakup email (for real this time)",
        body: `Hi {{firstName}},

I'm going to assume shift confirmations and no-shows aren't a pain point for {{agencyName}} right now.

If that changes, you know where to find me.

Best of luck with everything,
Arvind

P.S. - If I'm wrong and this IS a problem, just reply "I'm interested" and I'll set up a demo. Otherwise, I won't email again.`,
      },
    ],
  },

  "demo-follow-up": {
    name: "Post-Demo Follow-Up Sequence",
    emails: [
      {
        day: 0,
        subject: "Thanks for the Copper AI demo, {{firstName}}",
        body: `Hi {{firstName}},

Thanks for taking the time to chat today about automating {{agencyName}}'s {{useCase}}.

**Quick recap of what we covered:**
• Your current process: {{currentProcess}}
• Pain points: {{painPoints}}
• How Copper AI solves it: {{solution}}
• Expected results: {{expectedResults}}

**Next steps:**
1. Review the pricing proposal (attached)
2. Share with your team if needed
3. Let me know if you have questions

**Resources:**
• [Demo recording]({{recordingLink}})
• [Case study: Similar agency]({{caseStudyLink}})
• [ROI calculator]({{roiCalculatorLink}})

I'm here if you need anything. When you're ready to move forward, we can have you live in 2 weeks.

Best,
Arvind`,
      },
      {
        day: 2,
        subject: "Re: Copper AI for [Agency Name]",
        body: `Hi {{firstName}},

Just checking in—did you have a chance to review the proposal?

I know decisions like this require some thought (and maybe team buy-in). Happy to answer any questions or jump on a quick call if it's helpful.

A few common questions I get after demos:

**Q: "How hard is setup?"**
A: We handle 90% of it. You provide EVV access, we configure everything. Usually live in 7-10 days.

**Q: "What if it doesn't work for us?"**
A: We offer a 30-day trial. If you're not seeing value, we refund you. No risk.

**Q: "Can we start small?"**
A: Absolutely. Many customers start with just shift confirmations, then expand to patient scheduling later.

Want to schedule a quick follow-up call? Or ready to move forward?

Best,
Arvind`,
      },
      {
        day: 7,
        subject: "Should I close your Copper AI file?",
        body: `Hi {{firstName}},

I haven't heard back since our demo last week, so I wanted to check in one more time.

Are you:
a) Still interested, just busy? (Totally get it—let me know when to follow up)
b) Not ready right now? (No problem—I can check back in a few months)
c) Going with another solution? (Would love to know what you chose, for my own learning)
d) Not interested at all? (That's fine too—I'll stop emailing)

Just let me know so I can plan accordingly.

Thanks,
Arvind

P.S. - If you're worried about budget, we have flexible payment options. Don't let pricing be the only thing holding you back.`,
      },
    ],
  },

  "trial-nurture": {
    name: "Trial Customer Nurture",
    emails: [
      {
        day: 7,
        subject: "Your first week with Copper AI—how's it going?",
        body: `Hi {{firstName}},

Quick check-in on your first week with Copper AI at {{agencyName}}.

**Your stats so far:**
• Calls made: {{callsMade}}
• Success rate: {{successRate}}%
• Estimated time saved: {{hoursSaved}} hours

How's it feeling? Any questions or issues?

**Pro tips for Week 2:**
1. Adjust call timing if needed (we can call earlier/later)
2. Refine scripts based on what's working
3. Enable SMS confirmations for extra coverage

Let's jump on a 15-min call this week to optimize. When works for you?

Best,
Arvind`,
      },
      {
        day: 14,
        subject: "2-week check-in: [Agency Name] + Copper AI",
        body: `Hi {{firstName}},

Two weeks in! Let's look at the numbers.

**Your results (14 days):**
• No-show rate: {{noShowRate}}% (down from {{baselineNoShowRate}}%)
• Time saved: ~{{totalHoursSaved}} hours total
• ROI: {{roiAmount}} saved so far

{{customNote}}

**Next steps:**
1. Lock in your pricing (trial rate expires in 2 weeks)
2. Expand to {{nextUseCase}}? (if interested)
3. Consider upgrading to {{suggestedTier}} tier for more volume

Want to schedule a business review call to discuss?

Best,
Arvind`,
      },
      {
        day: 21,
        subject: "Your trial ends in 7 days—let's talk next steps",
        body: `Hi {{firstName}},

Your Copper AI trial wraps up in 7 days ({{trialEndDate}}).

**What happens next?**
1. **Continue:** Convert to paid subscription (pricing below)
2. **Pause:** We can extend your trial if you need more time
3. **Cancel:** We'll turn off the service (no hard feelings!)

**Your trial performance:**
• {{totalCalls}} calls made
• {{successRate}}% success rate
• {{noShowReduction}}% reduction in no-shows
• {{estimatedSavings}} saved vs answering service

**Pricing to continue:**
{{pricingTier}}: {{price}}/month ({{callLimit}} calls/month included)

Ready to keep going? Just reply "Yes" and I'll send the contract.

Questions? Let's chat: [calendar link]

Best,
Arvind`,
      },
    ],
  },

  "customer-success": {
    name: "Existing Customer Check-Ins",
    emails: [
      {
        day: 30,
        subject: "30 days with Copper AI—your impact report",
        body: `Hi {{firstName}},

Happy 1-month anniversary! 🎉

Here's your impact report for {{agencyName}}:

**📊 Your 30-Day Results:**
• Total calls: {{totalCalls}}
• Success rate: {{successRate}}%
• No-show reduction: {{noShowReduction}}%
• Time saved: {{hoursSaved}} hours
• Estimated cost savings: {{savings}}

**💬 What's working:**
{{workingWell}}

**🎯 Opportunities:**
{{opportunities}}

**Next month's goals:**
{{nextMonthGoals}}

Let's schedule a quick 15-min call to celebrate and plan next steps.

Thanks for being an amazing customer!

Best,
Arvind`,
      },
      {
        day: 90,
        subject: "Quarterly business review: [Agency Name] + Copper AI",
        body: `Hi {{firstName}},

It's been 90 days since {{agencyName}} went live with Copper AI. Time for a quarterly review!

**📊 Q1 Results:**
• Total calls: {{totalCalls}}
• Average success rate: {{avgSuccessRate}}%
• No-show improvement: {{noShowImprovement}}%
• Total time saved: {{totalHoursSaved}} hours (~{{fullTimeEquivalent}} FTE)
• Total cost savings: {{totalSavings}}

**ROI:** For every $1 spent on Copper AI, you saved {{roiMultiple}}.

**🎯 What's next?**
I'd love to schedule a 30-min QBR to:
1. Celebrate wins
2. Discuss optimizations
3. Explore expansion opportunities ({{expansionIdeas}})

When's good for you next week?

Best,
Arvind`,
      },
    ],
  },
};

function generateEmail(segment, emailIndex) {
  const campaign = segments[segment];

  if (!campaign) {
    console.error(`Segment '${segment}' not found.`);
    console.log("\nAvailable segments:");
    Object.keys(segments).forEach((s) => console.log(`  - ${s}`));
    process.exit(1);
  }

  if (emailIndex >= campaign.emails.length) {
    console.error(`Email ${emailIndex} not found in segment '${segment}'.`);
    process.exit(1);
  }

  const email = campaign.emails[emailIndex];

  return `
=============================================================================
SEGMENT: ${campaign.name}
EMAIL ${emailIndex + 1} OF ${campaign.emails.length} (Day ${email.day})
=============================================================================

SUBJECT: ${email.subject}

BODY:
${email.body}

=============================================================================
MERGE FIELDS NEEDED:
${extractMergeFields(email.body + email.subject).join(", ")}
=============================================================================
`;
}

function extractMergeFields(text) {
  const matches = text.match(/{{(\w+)}}/g);
  if (!matches) return [];
  return [...new Set(matches)].sort();
}

function generateSequence(segment) {
  const campaign = segments[segment];

  if (!campaign) {
    console.error(`Segment '${segment}' not found.`);
    console.log("\nAvailable segments:");
    Object.keys(segments).forEach((s) => console.log(`  - ${s}`));
    process.exit(1);
  }

  console.log("=".repeat(80));
  console.log(`EMAIL SEQUENCE: ${campaign.name}`);
  console.log("=".repeat(80));
  console.log();

  campaign.emails.forEach((email, index) => {
    console.log(generateEmail(segment, index));
    console.log();
  });
}

function generateAll() {
  Object.keys(segments).forEach((segment) => {
    generateSequence(segment);
  });
}

// CLI
const args = process.argv.slice(2);
const segment = args[0];
const flag = args[1];

if (!segment || segment === "all") {
  generateAll();
} else if (flag === "--list") {
  const campaign = segments[segment];
  console.log(`${campaign.name} - ${campaign.emails.length} emails`);
  campaign.emails.forEach((email, i) => {
    console.log(`  ${i + 1}. Day ${email.day}: ${email.subject}`);
  });
} else {
  generateSequence(segment);
}

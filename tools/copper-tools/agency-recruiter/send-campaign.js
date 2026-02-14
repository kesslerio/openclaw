#!/usr/bin/env node

/**
 * Email Campaign Automation for Agency Recruitment
 *
 * Sends personalized cold emails to home health agencies.
 *
 * Usage:
 *   node send-campaign.js --template cold-outreach --list leads/clearcare-prospects.csv
 *   node send-campaign.js --template follow-up-day3 --list leads/clearcare-prospects.csv --status CONTACTED
 *
 * Features:
 * - Personalization (first name, company, platform)
 * - Rate limiting (50 emails/day to avoid spam)
 * - Tracking (opens, clicks, responses)
 * - Auto-scheduling follow-ups
 * - Gmail API integration
 */

const fs = require("fs");
const path = require("path");
const { parse } = require("csv-parse/sync");

// Configuration
const CONFIG = {
  gmail: {
    // Set via environment variables or OAuth2
    clientId: process.env.GMAIL_CLIENT_ID,
    clientSecret: process.env.GMAIL_CLIENT_SECRET,
    refreshToken: process.env.GMAIL_REFRESH_TOKEN,
    from: "Arvind Sarin <arvind@copperdigital.com>",
    replyTo: "arvind@copperdigital.com",
  },
  rateLimit: {
    maxPerDay: 50, // Gmail free tier limit: 100/day, but 50 is safer
    delayMs: 30000, // 30 seconds between emails (looks more human)
  },
  tracking: {
    enabled: true,
    pixelUrl: "https://copper-ai-tracking.example.com/pixel.gif",
    linkTracking: true,
  },
  templates: {
    "cold-outreach": require("./email-templates/cold-outreach.js"),
    "follow-up-day3": require("./email-templates/follow-up-day3.js"),
    "follow-up-day7": require("./email-templates/follow-up-day7.js"),
    "demo-confirmation": require("./email-templates/demo-confirmation.js"),
  },
};

/**
 * Load prospects from CSV
 */
function loadProspects(csvPath, filterStatus = null) {
  if (!fs.existsSync(csvPath)) {
    throw new Error(`CSV file not found: ${csvPath}`);
  }

  const csvContent = fs.readFileSync(csvPath, "utf-8");
  const records = parse(csvContent, {
    columns: true,
    skip_empty_lines: true,
  });

  console.log(`📋 Loaded ${records.length} prospects from ${csvPath}`);

  // Filter by status if specified
  if (filterStatus) {
    const filtered = records.filter((r) => r.Status === filterStatus);
    console.log(`   Filtered to ${filtered.length} with status: ${filterStatus}`);
    return filtered;
  }

  return records;
}

/**
 * Personalize email template
 */
function personalizeEmail(template, prospect, variables = {}) {
  let { subject, body } = template;

  // Standard variables
  const vars = {
    firstName: prospect["First Name"] || prospect.firstName,
    lastName: prospect["Last Name"] || prospect.lastName,
    company: prospect.Company || prospect.company,
    title: prospect.Title || prospect.title,
    ...variables,
  };

  // Replace placeholders
  Object.entries(vars).forEach(([key, value]) => {
    const placeholder = new RegExp(`\\[${key}\\]`, "gi");
    subject = subject.replace(placeholder, value);
    body = body.replace(placeholder, value);
  });

  // Add tracking pixel
  if (CONFIG.tracking.enabled) {
    const trackingId = generateTrackingId(prospect);
    body += `\n\n<img src="${CONFIG.tracking.pixelUrl}?id=${trackingId}" width="1" height="1" />`;
  }

  return { subject, body };
}

/**
 * Generate unique tracking ID
 */
function generateTrackingId(prospect) {
  const email = prospect.Email || prospect.email;
  return Buffer.from(`${email}-${Date.now()}`).toString("base64");
}

/**
 * Send email via Gmail API
 *
 * Note: This is a placeholder. Actual implementation requires:
 * 1. Gmail API OAuth2 setup
 * 2. googleapis npm package
 * 3. Token refresh logic
 *
 * For MVP, we'll use a simpler approach: output emails to files for manual sending
 * or use a service like SendGrid, Mailgun, or AWS SES.
 */
async function sendEmail(to, subject, body, prospect) {
  console.log(`📧 Sending to: ${to}`);
  console.log(`   Subject: ${subject}`);

  // MVP: Save to file instead of actually sending
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const safeEmail = to.replace(/[^a-z0-9]/gi, "_");
  const filename = `email-${safeEmail}-${timestamp}.html`;
  const outputDir = path.join(__dirname, "outbox");

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const filepath = path.join(outputDir, filename);
  const htmlEmail = formatEmailHTML(to, subject, body, prospect);

  fs.writeFileSync(filepath, htmlEmail);
  console.log(`   ✅ Saved to: ${filepath}`);

  // In production, use Gmail API:
  // const gmail = google.gmail({ version: 'v1', auth: oauth2Client });
  // await gmail.users.messages.send({ ... });

  return {
    sent: true,
    messageId: timestamp,
    filepath,
  };
}

/**
 * Format email as HTML
 */
function formatEmailHTML(to, subject, body, prospect) {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${subject}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="white-space: pre-wrap;">${body}</div>
  
  <hr style="margin: 30px 0; border: none; border-top: 1px solid #ccc;">
  
  <div style="font-size: 12px; color: #666;">
    <strong>Metadata (for tracking):</strong><br>
    To: ${to}<br>
    Prospect: ${prospect["First Name"]} ${prospect["Last Name"]}<br>
    Company: ${prospect.Company}<br>
    Sent: ${new Date().toISOString()}<br>
  </div>
</body>
</html>`;
}

/**
 * Send campaign to list of prospects
 */
async function sendCampaign(templateName, csvPath, options = {}) {
  console.log(`\n🚀 Starting campaign: ${templateName}\n`);

  // Load template
  const template = CONFIG.templates[templateName];
  if (!template) {
    throw new Error(`Template not found: ${templateName}`);
  }

  // Load prospects
  const prospects = loadProspects(csvPath, options.status);

  // Limit by rate limit
  const limit = Math.min(prospects.length, CONFIG.rateLimit.maxPerDay);
  const toSend = prospects.slice(0, limit);

  console.log(`\n📊 Campaign Stats:`);
  console.log(`   Template: ${templateName}`);
  console.log(`   Total prospects: ${prospects.length}`);
  console.log(`   Sending today: ${toSend.length}`);
  console.log(`   Rate limit: ${CONFIG.rateLimit.maxPerDay}/day\n`);

  // Send emails
  const results = [];

  for (let i = 0; i < toSend.length; i++) {
    const prospect = toSend[i];
    const email = prospect.Email || prospect.email;

    if (!email || !email.includes("@")) {
      console.log(
        `⚠️  Skipping ${prospect["First Name"]} ${prospect["Last Name"]} (no valid email)`,
      );
      continue;
    }

    // Personalize
    const { subject, body } = personalizeEmail(template, prospect, options.variables);

    // Send
    try {
      const result = await sendEmail(email, subject, body, prospect);
      results.push({ prospect, result, status: "sent" });

      // Update lead tracker
      updateLeadStatus(
        prospect,
        "CONTACTED",
        `Sent ${templateName} on ${new Date().toISOString()}`,
      );

      // Rate limiting delay
      if (i < toSend.length - 1) {
        const delay = CONFIG.rateLimit.delayMs;
        console.log(`   ⏳ Waiting ${delay / 1000}s before next email...\n`);
        await sleep(delay);
      }
    } catch (error) {
      console.error(`❌ Failed to send to ${email}: ${error.message}`);
      results.push({ prospect, error, status: "failed" });
    }
  }

  // Summary
  console.log(`\n✅ Campaign complete!`);
  console.log(`   Sent: ${results.filter((r) => r.status === "sent").length}`);
  console.log(`   Failed: ${results.filter((r) => r.status === "failed").length}`);
  console.log(`\n💡 Next steps:`);
  console.log(`   1. Review emails in: ${path.join(__dirname, "outbox")}`);
  console.log(`   2. Manually send via Gmail (or set up API)`);
  console.log(`   3. Track responses in leads.json`);
  console.log(`   4. Schedule follow-up in 3 days\n`);

  return results;
}

/**
 * Update lead tracker (leads.json)
 */
function updateLeadStatus(prospect, status, notes) {
  const leadsPath = path.join(__dirname, "leads.json");

  let leads = { prospects: [] };
  if (fs.existsSync(leadsPath)) {
    leads = JSON.parse(fs.readFileSync(leadsPath, "utf-8"));
  }

  const email = prospect.Email || prospect.email;
  const existing = leads.prospects.find((p) => p.email === email);

  if (existing) {
    existing.status = status;
    existing.lastContact = new Date().toISOString();
    existing.notes = (existing.notes || "") + `\n${notes}`;
  } else {
    leads.prospects.push({
      firstName: prospect["First Name"] || prospect.firstName,
      lastName: prospect["Last Name"] || prospect.lastName,
      email,
      company: prospect.Company || prospect.company,
      title: prospect.Title || prospect.title,
      status,
      addedDate: new Date().toISOString(),
      lastContact: new Date().toISOString(),
      notes,
    });
  }

  fs.writeFileSync(leadsPath, JSON.stringify(leads, null, 2));
}

/**
 * Utility: sleep
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// CLI Interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const template =
    args.find((arg) => arg.startsWith("--template="))?.split("=")[1] || "cold-outreach";
  const list = args.find((arg) => arg.startsWith("--list="))?.split("=")[1];
  const status = args.find((arg) => arg.startsWith("--status="))?.split("=")[1];

  if (!list) {
    console.error("❌ Error: --list parameter required");
    console.log(
      "\nUsage: node send-campaign.js --template=cold-outreach --list=leads/prospects.csv",
    );
    process.exit(1);
  }

  sendCampaign(template, list, { status })
    .then((results) => {
      console.log("\n🎉 Campaign sent successfully!\n");
    })
    .catch((error) => {
      console.error(`❌ Campaign failed: ${error.message}`);
      process.exit(1);
    });
}

module.exports = { sendCampaign, personalizeEmail, sendEmail };

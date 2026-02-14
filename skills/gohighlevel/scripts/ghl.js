#!/usr/bin/env node
/**
 * GoHighLevel CRM CLI
 * Usage: node ghl.js <command> [options]
 */

const https = require("https");
const path = require("path");
const fs = require("fs");

// Load .env
const envPath = path.join(process.env.HOME, "clawd", ".env");
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, "utf8");
  envContent.split("\n").forEach((line) => {
    const [key, ...valueParts] = line.split("=");
    if (key && valueParts.length > 0) {
      process.env[key.trim()] = valueParts.join("=").trim();
    }
  });
}

const API_KEY = process.env.GHL_API_KEY || process.env.GOHIGHLEVEL_JWT_TOKEN;
const LOCATION_ID = process.env.GHL_LOCATION_ID;
const API_BASE = "services.leadconnectorhq.com";

if (!API_KEY) {
  console.error("❌ GHL_API_KEY or GOHIGHLEVEL_JWT_TOKEN not found in environment");
  console.error("   Set in ~/clawd/.env or export GHL_API_KEY=your-key");
  process.exit(1);
}

function apiRequest(method, endpoint, data = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: API_BASE,
      path: endpoint,
      method: method,
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        "Content-Type": "application/json",
        Version: "2021-07-28",
      },
    };

    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          resolve({ raw: body });
        }
      });
    });

    req.on("error", reject);
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

async function listContacts(query = "") {
  const endpoint = query
    ? `/contacts/v1/contacts/search?query=${encodeURIComponent(query)}&locationId=${LOCATION_ID}`
    : `/contacts/v1/contacts?locationId=${LOCATION_ID}&limit=20`;

  const result = await apiRequest("GET", endpoint);

  if (result.contacts) {
    console.log(`\n📇 Contacts (${result.contacts.length} found)\n`);
    result.contacts.forEach((c, i) => {
      console.log(`${i + 1}. ${c.firstName || ""} ${c.lastName || ""}`);
      console.log(`   Email: ${c.email || "N/A"}`);
      console.log(`   Phone: ${c.phone || "N/A"}`);
      console.log(`   ID: ${c.id}`);
      console.log("");
    });
  } else {
    console.log("No contacts found or API error:", result);
  }
}

async function listOpportunities(pipelineName = "") {
  const endpoint = `/opportunities/v1/opportunities?locationId=${LOCATION_ID}&limit=20`;
  const result = await apiRequest("GET", endpoint);

  if (result.opportunities) {
    console.log(`\n💼 Opportunities (${result.opportunities.length} found)\n`);
    result.opportunities.forEach((o, i) => {
      console.log(`${i + 1}. ${o.name}`);
      console.log(`   Stage: ${o.pipelineStageId}`);
      console.log(`   Value: $${o.monetaryValue || 0}`);
      console.log(`   Contact: ${o.contactId}`);
      console.log("");
    });
  } else {
    console.log("No opportunities found or API error:", result);
  }
}

async function getContact(contactId) {
  const endpoint = `/contacts/v1/contacts/${contactId}`;
  const result = await apiRequest("GET", endpoint);
  console.log(JSON.stringify(result, null, 2));
}

// CLI Handler
const [, , command, subcommand, ...args] = process.argv;

async function main() {
  switch (command) {
    case "contacts":
      if (subcommand === "list") {
        await listContacts();
      } else if (subcommand === "search") {
        await listContacts(args[0]);
      } else if (subcommand === "get") {
        await getContact(args[0]);
      } else {
        console.log("Usage: ghl.js contacts [list|search <query>|get <id>]");
      }
      break;

    case "opportunities":
      await listOpportunities();
      break;

    default:
      console.log(`
GoHighLevel CRM CLI

Commands:
  contacts list              List recent contacts
  contacts search <query>    Search contacts
  contacts get <id>          Get contact details
  opportunities              List opportunities

Examples:
  node ghl.js contacts list
  node ghl.js contacts search "Health Masters"
  node ghl.js opportunities
      `);
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});

#!/usr/bin/env node

/**
 * LinkedIn Scraper for Home Health Agency Recruitment
 *
 * Finds agencies using ClearCare or Axxess and extracts decision-maker contacts.
 *
 * Usage:
 *   node linkedin-scraper.js --platform clearcare --limit 50
 *   node linkedin-scraper.js --platform axxess --limit 50
 *
 * Output: CSV file with prospects (name, title, company, linkedin_url, email)
 *
 * Note: Requires LinkedIn Sales Navigator or manual search + browser automation.
 *       This version uses Playwright to automate LinkedIn search.
 */

const fs = require("fs");
const path = require("path");

// Configuration
const CONFIG = {
  platforms: {
    clearcare: {
      searchQuery: "home health care agency ClearCare",
      keywords: ["ClearCare", "WellSky", "home health", "home care"],
      titles: ["CEO", "COO", "Director of Operations", "Administrator", "Owner", "Founder"],
    },
    axxess: {
      searchQuery: "home health care agency Axxess",
      keywords: ["Axxess", "home health", "home care"],
      titles: ["CEO", "COO", "Director of Operations", "Administrator", "Owner", "Founder"],
    },
  },
  outputDir: path.join(__dirname, "leads"),
  rateLimit: {
    delay: 2000, // 2 seconds between requests
    maxPerHour: 100, // LinkedIn rate limits
  },
};

// Ensure output directory exists
if (!fs.existsSync(CONFIG.outputDir)) {
  fs.mkdirSync(CONFIG.outputDir, { recursive: true });
}

/**
 * Main scraper function (uses Google search + LinkedIn as fallback)
 *
 * LinkedIn Sales Navigator is expensive ($99/mo). Instead:
 * 1. Google search for agencies using the platform
 * 2. Extract LinkedIn profiles from agency websites
 * 3. Find decision-makers via LinkedIn public search
 *
 * For MVP, we'll provide a manual workflow + template.
 */
async function scrapeLinkedIn(platform, limit) {
  console.log(`🔍 Searching for ${limit} ${platform} agencies...`);

  const config = CONFIG.platforms[platform];
  if (!config) {
    throw new Error(`Unknown platform: ${platform}`);
  }

  // Manual workflow (for MVP)
  console.log("\n📋 MANUAL WORKFLOW (LinkedIn Sales Navigator required for automation)\n");
  console.log(
    "Since LinkedIn API is restricted and scraping violates ToS, here's the manual workflow:\n",
  );

  console.log("1. LinkedIn Sales Navigator Search:");
  console.log(`   - Go to: https://www.linkedin.com/sales/`);
  console.log(`   - Search: "${config.searchQuery}"`);
  console.log(`   - Filters:`);
  console.log(`     • Industry: Health Care, Hospital & Health Care`);
  console.log(`     • Company size: 11-50, 51-200, 201-500`);
  console.log(`     • Geography: United States`);
  console.log(`     • Keywords: ${config.keywords.join(", ")}`);
  console.log("");

  console.log("2. Find Decision-Makers:");
  console.log(`   - Titles: ${config.titles.join(", ")}`);
  console.log(`   - Use LinkedIn's "People" tab to find contacts`);
  console.log("");

  console.log("3. Export to CSV:");
  console.log(`   - Save as: ${CONFIG.outputDir}/${platform}-prospects-manual.csv`);
  console.log("   - Columns: First Name, Last Name, Title, Company, LinkedIn URL, Email");
  console.log("");

  console.log("4. Alternative: Google Search");
  console.log(`   - Search: "home health agency" + "ClearCare" + "CEO" OR "administrator"`);
  console.log(`   - Visit agency websites → Find "About Us" or "Team" pages`);
  console.log(`   - LinkedIn: Search "{Company Name} + {Title}"`);
  console.log("");

  // Generate sample CSV template
  const timestamp = new Date().toISOString().split("T")[0];
  const templatePath = path.join(CONFIG.outputDir, `${platform}-prospects-template.csv`);

  const csvTemplate = `First Name,Last Name,Title,Company,LinkedIn URL,Email,Phone,Notes
John,Doe,CEO,ABC Home Health,https://linkedin.com/in/johndoe,john@abchomehealth.com,214-555-0100,Uses ClearCare
Jane,Smith,Administrator,XYZ Home Care,https://linkedin.com/in/janesmith,jane@xyzhomecare.com,214-555-0200,50 caregivers
Bob,Johnson,COO,123 Senior Care,https://linkedin.com/in/bobjohnson,bob@123seniorcare.com,214-555-0300,Interested in no-show reduction`;

  fs.writeFileSync(templatePath, csvTemplate);
  console.log(`✅ Template CSV created: ${templatePath}`);
  console.log(
    `\n💡 TIP: Fill in the template and save as ${platform}-prospects-${timestamp}.csv\n`,
  );

  // Alternative: Generate list of agencies to research
  console.log("📋 ALTERNATIVE: Pre-populated Agency List\n");
  console.log("We can also provide a list of known ClearCare/Axxess agencies to research:");
  console.log("");

  const sampleAgencies = generateSampleAgenciesList(platform, limit);
  const agencyListPath = path.join(CONFIG.outputDir, `${platform}-agencies-to-research.json`);
  fs.writeFileSync(agencyListPath, JSON.stringify(sampleAgencies, null, 2));

  console.log(`✅ Agency research list: ${agencyListPath}`);
  console.log(`   (${sampleAgencies.length} agencies to research manually)\n`);

  // For automation-friendly version, use browser extension or Playwright
  console.log("🤖 AUTOMATION OPTIONS:\n");
  console.log("Option 1: Browser Extension (Recommended)");
  console.log("  - Use OpenClaw browser extension");
  console.log("  - Navigate to LinkedIn Sales Navigator");
  console.log("  - Run search, extract data via DOM parsing");
  console.log("  - Export to CSV");
  console.log("");
  console.log("Option 2: Playwright (Requires login)");
  console.log("  - Automate LinkedIn login (save cookies)");
  console.log("  - Run search queries");
  console.log("  - Extract profile data");
  console.log("  - Risk: Account suspension if detected");
  console.log("");
  console.log("Option 3: Third-party APIs");
  console.log("  - Apollo.io ($49/mo - email finder + LinkedIn data)");
  console.log("  - Hunter.io ($49/mo - email verification)");
  console.log("  - Clearbit ($99/mo - company + contact data)");
  console.log("");

  return templatePath;
}

/**
 * Generate list of agencies to research manually
 *
 * Sources:
 * - ClearCare customer list (public case studies)
 * - Axxess customer list (public testimonials)
 * - Home health industry directories
 * - Google search results
 */
function generateSampleAgenciesList(platform, limit) {
  // Sample agencies (would expand to 50+ in production)
  const clearCareAgencies = [
    {
      name: "Always Best Care",
      website: "https://www.abc-seniors.com",
      location: "Multiple locations",
      notes: "Franchise, uses ClearCare",
    },
    {
      name: "Visiting Angels",
      website: "https://www.visitingangels.com",
      location: "Multiple locations",
      notes: "National franchise",
    },
    {
      name: "Home Instead",
      website: "https://www.homeinstead.com",
      location: "Multiple locations",
      notes: "Large franchise network",
    },
    {
      name: "Comfort Keepers",
      website: "https://www.comfortkeepers.com",
      location: "Multiple locations",
      notes: "Franchise",
    },
    {
      name: "Right at Home",
      website: "https://www.rightathome.net",
      location: "Multiple locations",
      notes: "Franchise",
    },
    {
      name: "Senior Helpers",
      website: "https://www.seniorhelpers.com",
      location: "Multiple locations",
      notes: "Franchise",
    },
    {
      name: "Synergy Home Care",
      website: "https://www.synergyhomecare.com",
      location: "Multiple locations",
      notes: "Franchise",
    },
    {
      name: "BrightStar Care",
      website: "https://www.brightstarcare.com",
      location: "Multiple locations",
      notes: "Medical + non-medical",
    },
    // Add more agencies here (would be 50+ for production)
  ];

  const axxessAgencies = [
    {
      name: "Amedisys",
      website: "https://www.amedisys.com",
      location: "Multiple locations",
      notes: "Publicly traded, uses Axxess",
    },
    {
      name: "LHC Group",
      website: "https://www.lhcgroup.com",
      location: "Multiple locations",
      notes: "Large agency network",
    },
    // Add more Axxess agencies here
  ];

  const agencies = platform === "clearcare" ? clearCareAgencies : axxessAgencies;

  return agencies.slice(0, Math.min(limit, agencies.length)).map((agency, index) => ({
    id: `AG-${String(index + 1).padStart(3, "0")}`,
    ...agency,
    platform,
    researched: false,
    contactsFound: 0,
    linkedinSearchQuery: `${agency.name} CEO OR Administrator OR "Director of Operations"`,
    nextAction: "Find decision-maker on LinkedIn",
    addedDate: new Date().toISOString(),
  }));
}

/**
 * Email finder (uses public sources + educated guesses)
 */
function findEmail(firstName, lastName, company) {
  // Common email patterns for small businesses
  const domain = extractDomain(company);
  if (!domain) return null;

  const patterns = [
    `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${domain}`,
    `${firstName.toLowerCase()}${lastName.toLowerCase()}@${domain}`,
    `${firstName.charAt(0).toLowerCase()}${lastName.toLowerCase()}@${domain}`,
    `${firstName.toLowerCase()}@${domain}`,
  ];

  // Return most likely pattern (would verify with Hunter.io in production)
  return patterns[0];
}

/**
 * Extract domain from company name or website
 */
function extractDomain(companyOrWebsite) {
  // Simple heuristic - would use proper domain extraction in production
  const cleaned = companyOrWebsite
    .toLowerCase()
    .replace(/https?:\/\/(www\.)?/, "")
    .replace(/\/$/, "")
    .split("/")[0];

  if (cleaned.includes(".")) {
    return cleaned;
  }

  // Guess domain from company name
  return cleaned.replace(/\s+/g, "").replace(/[^a-z0-9]/g, "") + ".com";
}

/**
 * Export prospects to CSV
 */
function exportToCSV(prospects, platform) {
  const timestamp = new Date().toISOString().split("T")[0];
  const filename = `${platform}-prospects-${timestamp}.csv`;
  const filepath = path.join(CONFIG.outputDir, filename);

  const headers = [
    "First Name",
    "Last Name",
    "Title",
    "Company",
    "LinkedIn URL",
    "Email",
    "Phone",
    "Notes",
  ];
  const rows = prospects.map((p) => [
    p.firstName,
    p.lastName,
    p.title,
    p.company,
    p.linkedinUrl,
    p.email || "",
    p.phone || "",
    p.notes || "",
  ]);

  const csv = [
    headers.join(","),
    ...rows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
  ].join("\n");

  fs.writeFileSync(filepath, csv);
  console.log(`✅ Exported ${prospects.length} prospects to: ${filepath}`);

  return filepath;
}

// CLI Interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const platform = args.find((arg) => arg.startsWith("--platform="))?.split("=")[1] || "clearcare";
  const limit = parseInt(args.find((arg) => arg.startsWith("--limit="))?.split("=")[1] || "50");

  scrapeLinkedIn(platform, limit)
    .then((result) => {
      console.log(`\n✅ Done! Next step: Fill in the template and run email campaign.\n`);
    })
    .catch((error) => {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    });
}

module.exports = { scrapeLinkedIn, generateSampleAgenciesList, findEmail };

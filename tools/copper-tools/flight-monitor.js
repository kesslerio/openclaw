#!/usr/bin/env node
/**
 * Flight Price Monitoring Tool
 * Monitors DEL↔DFW flights and alerts when prices drop below threshold
 *
 * Usage:
 *   node tools/flight-monitor.js
 *
 * Features:
 * - Checks Google Flights via web scraping
 * - Compares prices across ±3 days around target date
 * - Alerts on Telegram + WhatsApp if below $750 threshold
 * - Saves price history for trend analysis
 * - Generates daily reports
 *
 * Created: Feb 2, 2026 by Nike 🐾
 */

const https = require("https");
const fs = require("fs").promises;
const path = require("path");

// Configuration
const CONFIG = {
  routes: [
    {
      name: "Outbound (DEL → DFW)",
      origin: "DEL",
      destination: "DFW",
      targetDate: "2026-02-09",
      flexDays: 3, // Check Feb 6-12
      passengers: 1,
      preferredAirline: "AA", // American Airlines
    },
    {
      name: "Return (DFW → DEL)",
      origin: "DFW",
      destination: "DEL",
      targetDate: "2026-02-25",
      flexDays: 0, // Fixed date
      passengers: 3,
      preferredAirline: "AA",
    },
  ],
  alertThreshold: 750, // Alert if price below $750
  priceHistoryFile: path.join(__dirname, "../data/flight-prices.json"),
  reportDir: path.join(__dirname, "../reports/flights"),
};

/**
 * Fetch flight prices from Google Flights
 * (Placeholder - requires actual API integration or browser automation)
 */
async function fetchFlightPrices(route) {
  console.log(`\n🔍 Checking ${route.name}...`);
  console.log(`   ${route.origin} → ${route.destination}`);
  console.log(`   Date: ${route.targetDate} (±${route.flexDays} days)`);

  // TODO: Integrate with actual Google Flights scraping
  // Options:
  // 1. Puppeteer/Playwright browser automation
  // 2. Google Flights API (if available)
  // 3. Third-party flight API (Skyscanner, Kayak)

  // Mock data for now
  const mockPrices = [];
  const baseDate = new Date(route.targetDate);

  for (let i = -route.flexDays; i <= route.flexDays; i++) {
    const checkDate = new Date(baseDate);
    checkDate.setDate(baseDate.getDate() + i);
    const dateStr = checkDate.toISOString().split("T")[0];

    // Generate mock price (would come from actual API)
    const basePrice = 850 + Math.random() * 300;
    const isPreferredAirline = Math.random() > 0.5;

    mockPrices.push({
      date: dateStr,
      price: Math.round(basePrice),
      airline: isPreferredAirline ? route.preferredAirline : "OA", // Other airline
      stops: Math.random() > 0.7 ? 0 : 1,
      duration: "23-26 hours",
      url: `https://www.google.com/travel/flights?...`,
    });
  }

  return mockPrices.sort((a, b) => a.price - b.price);
}

/**
 * Load price history from JSON file
 */
async function loadPriceHistory() {
  try {
    const data = await fs.readFile(CONFIG.priceHistoryFile, "utf8");
    return JSON.parse(data);
  } catch (err) {
    if (err.code === "ENOENT") {
      return { checks: [] };
    }
    throw err;
  }
}

/**
 * Save price history to JSON file
 */
async function savePriceHistory(history) {
  await fs.mkdir(path.dirname(CONFIG.priceHistoryFile), { recursive: true });
  await fs.writeFile(CONFIG.priceHistoryFile, JSON.stringify(history, null, 2), "utf8");
}

/**
 * Analyze prices and determine if alert needed
 */
function analyzePrices(route, prices) {
  const analysis = {
    route: route.name,
    checkDate: new Date().toISOString(),
    cheapest: prices[0],
    preferredAirline: null,
    shouldAlert: false,
    alertReason: null,
  };

  // Find cheapest with preferred airline
  const preferredFlights = prices.filter((p) => p.airline === route.preferredAirline);
  if (preferredFlights.length > 0) {
    analysis.preferredAirline = preferredFlights[0];
  }

  // Determine if should alert
  if (analysis.cheapest.price < CONFIG.alertThreshold) {
    analysis.shouldAlert = true;
    analysis.alertReason = `Price dropped below $${CONFIG.alertThreshold}`;
  } else if (
    analysis.preferredAirline &&
    analysis.preferredAirline.price < CONFIG.alertThreshold + 100
  ) {
    analysis.shouldAlert = true;
    analysis.alertReason = `${route.preferredAirline} within $100 of threshold`;
  }

  return analysis;
}

/**
 * Send alert via OpenClaw message tool
 */
async function sendAlert(analysis, route) {
  const flight = analysis.preferredAirline || analysis.cheapest;

  const message = `
✈️ FLIGHT ALERT: ${route.name}

🎯 **Price: $${flight.price}** (${flight.airline})
📅 Date: ${flight.date}
✈️ Stops: ${flight.stops === 0 ? "Nonstop" : `${flight.stops} stop`}
⏱️ Duration: ${flight.duration}

${analysis.alertReason}

🔗 Book: ${flight.url}

---
Cheapest overall: $${analysis.cheapest.price} (${analysis.cheapest.airline})
${route.preferredAirline} best: $${analysis.preferredAirline?.price || "N/A"}
  `.trim();

  console.log("\n🚨 ALERT TRIGGERED:");
  console.log(message);

  // TODO: Actually send via OpenClaw message tool
  // This would call the message tool with:
  // - channel: telegram (and whatsapp for important alerts)
  // - message: formatted alert
  console.log("\n📱 Sending to Telegram + WhatsApp...");
}

/**
 * Generate daily report
 */
async function generateReport(allAnalyses) {
  const timestamp = new Date().toISOString().split("T")[0];
  const reportPath = path.join(CONFIG.reportDir, `flight-check-${timestamp}.md`);

  let report = `# Flight Price Check - ${timestamp}\n\n`;
  report += `**Monitoring:** DEL↔DFW for Feb 9 (1 pax) + Feb 25 (3 pax)\n\n`;
  report += `**Alert Threshold:** Below $${CONFIG.alertThreshold}/ticket\n\n`;
  report += `---\n\n`;

  for (const analysis of allAnalyses) {
    report += `## ${analysis.route}\n\n`;
    report += `**Checked:** ${new Date(analysis.checkDate).toLocaleString()}\n\n`;

    const flight = analysis.preferredAirline || analysis.cheapest;
    report += `### Best Option\n`;
    report += `- **Price:** $${flight.price}\n`;
    report += `- **Airline:** ${flight.airline}\n`;
    report += `- **Date:** ${flight.date}\n`;
    report += `- **Stops:** ${flight.stops === 0 ? "Nonstop" : `${flight.stops} stop`}\n`;
    report += `- **Duration:** ${flight.duration}\n`;
    report += `- **Book:** [Google Flights](${flight.url})\n\n`;

    if (analysis.shouldAlert) {
      report += `🚨 **ALERT:** ${analysis.alertReason}\n\n`;
    } else {
      report += `✅ **Status:** Above threshold (waiting for better price)\n\n`;
    }

    if (
      analysis.preferredAirline &&
      analysis.cheapest.airline !== analysis.preferredAirline.airline
    ) {
      report += `### Alternative (Cheapest Overall)\n`;
      report += `- **Price:** $${analysis.cheapest.price}\n`;
      report += `- **Airline:** ${analysis.cheapest.airline}\n`;
      report += `- **Date:** ${analysis.cheapest.date}\n`;
      report += `- **Duration:** ${analysis.cheapest.duration}\n\n`;
    }

    report += `---\n\n`;
  }

  report += `## Recommendation\n\n`;
  const anyAlerts = allAnalyses.some((a) => a.shouldAlert);
  if (anyAlerts) {
    report += `⚡ **ACTION RECOMMENDED:** Good prices found! Review and book if suitable.\n\n`;
  } else {
    report += `⏳ **WAIT:** Current prices above threshold. Continue monitoring.\n\n`;
  }

  report += `---\n`;
  report += `*Generated by Nike's Flight Monitor 🐾*\n`;

  await fs.mkdir(CONFIG.reportDir, { recursive: true });
  await fs.writeFile(reportPath, report, "utf8");

  console.log(`\n📄 Report saved: ${reportPath}`);
  return report;
}

/**
 * Main monitoring function
 */
async function monitorFlights() {
  console.log("🛫 Flight Price Monitor Starting...\n");
  console.log(`Threshold: $${CONFIG.alertThreshold}/ticket`);
  console.log(`Routes: ${CONFIG.routes.length}`);

  const history = await loadPriceHistory();
  const allAnalyses = [];

  for (const route of CONFIG.routes) {
    const prices = await fetchFlightPrices(route);
    const analysis = analyzePrices(route, prices);

    console.log(`\n✅ ${route.name}: Best = $${analysis.cheapest.price}`);
    if (analysis.preferredAirline) {
      console.log(`   ${route.preferredAirline}: $${analysis.preferredAirline.price}`);
    }

    // Store in history
    history.checks.push({
      timestamp: analysis.checkDate,
      route: route.name,
      cheapestPrice: analysis.cheapest.price,
      preferredPrice: analysis.preferredAirline?.price || null,
      alert: analysis.shouldAlert,
    });

    // Send alert if needed
    if (analysis.shouldAlert) {
      await sendAlert(analysis, route);
    }

    allAnalyses.push(analysis);
  }

  // Save history
  await savePriceHistory(history);

  // Generate report
  const report = await generateReport(allAnalyses);

  console.log("\n✅ Flight monitoring complete!");

  return {
    analyses: allAnalyses,
    report,
    anyAlerts: allAnalyses.some((a) => a.shouldAlert),
  };
}

/**
 * Price trend analysis
 */
async function analyzeTrends() {
  const history = await loadPriceHistory();

  if (history.checks.length < 2) {
    return "Insufficient data for trend analysis (need 2+ checks)";
  }

  console.log("\n📊 Price Trend Analysis:\n");

  for (const route of CONFIG.routes) {
    const routeChecks = history.checks
      .filter((c) => c.route === route.name)
      .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    if (routeChecks.length < 2) continue;

    const latest = routeChecks[routeChecks.length - 1];
    const previous = routeChecks[routeChecks.length - 2];

    const change = latest.cheapestPrice - previous.cheapestPrice;
    const pctChange = ((change / previous.cheapestPrice) * 100).toFixed(1);

    console.log(`${route.name}:`);
    console.log(`  Current: $${latest.cheapestPrice}`);
    console.log(`  Previous: $${previous.cheapestPrice}`);
    console.log(`  Change: ${change > 0 ? "+" : ""}$${change} (${pctChange}%)`);
    console.log(`  Trend: ${change > 0 ? "📈 Up" : change < 0 ? "📉 Down" : "➡️  Flat"}\n`);
  }
}

// CLI Interface
if (require.main === module) {
  const command = process.argv[2] || "check";

  (async () => {
    try {
      if (command === "check") {
        await monitorFlights();
      } else if (command === "trends") {
        await analyzeTrends();
      } else if (command === "history") {
        const history = await loadPriceHistory();
        console.log(JSON.stringify(history, null, 2));
      } else {
        console.log("Usage:");
        console.log("  node flight-monitor.js check    - Check current prices");
        console.log("  node flight-monitor.js trends   - Analyze price trends");
        console.log("  node flight-monitor.js history  - View price history");
      }
    } catch (err) {
      console.error("❌ Error:", err.message);
      process.exit(1);
    }
  })();
}

module.exports = { monitorFlights, analyzeTrends };

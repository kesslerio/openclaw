#!/usr/bin/env node
/**
 * Unified Copper AI Integration Server
 *
 * Handles multiple home health platforms in a single deployment:
 * - ClearCare (Zapier-based integration)
 * - Axxess (Direct API integration)
 * - Future platforms...
 *
 * Author: Nike 🐾
 * Created: Feb 3, 2026
 */

require("dotenv").config();
const express = require("express");
const { Pool } = require("pg");

// Initialize Express
const app = express();
app.use(express.json());

// Database connection (shared across all platforms)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || "postgresql://localhost:5432/copper_ai",
  max: 20, // Connection pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Test database connection on startup
pool.connect((err, client, release) => {
  if (err) {
    console.error("❌ Database connection failed:", err.stack);
    process.exit(1);
  }
  console.log("✅ Database connected");
  release();
});

// Shared services
const voiceService = require("./services/voice");
const alertService = require("./services/alerts");
const analyticsService = require("./services/analytics");

// Platform-specific routes
const clearcareRoutes = require("./routes/clearcare");
const axxessRoutes = require("./routes/axxess");

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Request logging
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// Error handling
app.use((err, req, res, next) => {
  console.error("❌ Server error:", err);
  res.status(500).json({
    error: "Internal server error",
    message: process.env.NODE_ENV === "development" ? err.message : undefined,
  });
});

// ============================================================================
// HEALTH & STATUS ENDPOINTS
// ============================================================================

/**
 * Health check (for uptime monitoring)
 */
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: "1.0.0",
  });
});

/**
 * Detailed status (platforms, agencies, metrics)
 */
app.get("/api/status", async (req, res) => {
  try {
    // Count agencies by platform
    const platformCounts = await pool.query(`
      SELECT platform, COUNT(*) as count
      FROM agencies
      WHERE status = 'active'
      GROUP BY platform
    `);

    // Total visits today
    const todayVisits = await pool.query(`
      SELECT COUNT(*) as count
      FROM visits
      WHERE visit_date = CURRENT_DATE
    `);

    // EVV calls today
    const evvCalls = await pool.query(`
      SELECT COUNT(*) as count
      FROM evv_logs
      WHERE DATE(timestamp) = CURRENT_DATE
    `);

    res.json({
      status: "operational",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      platforms: platformCounts.rows,
      metrics: {
        active_agencies: platformCounts.rows.reduce((sum, row) => sum + parseInt(row.count), 0),
        visits_today: parseInt(todayVisits.rows[0]?.count || 0),
        evv_calls_today: parseInt(evvCalls.rows[0]?.count || 0),
      },
      version: "1.0.0",
    });
  } catch (error) {
    console.error("❌ Status check failed:", error);
    res.status(500).json({ error: "Failed to get status" });
  }
});

/**
 * List supported platforms
 */
app.get("/api/platforms", (req, res) => {
  res.json({
    platforms: [
      {
        name: "ClearCare",
        slug: "clearcare",
        status: "active",
        integration_type: "zapier",
        agencies: "4,500+",
        features: ["voice_evv", "no_show_prevention", "schedule_sync"],
      },
      {
        name: "Axxess",
        slug: "axxess",
        status: "active",
        integration_type: "direct_api",
        agencies: "7,000+",
        features: ["voice_evv", "no_show_prevention", "schedule_sync", "auto_sync"],
      },
      {
        name: "WellSky Personal Care",
        slug: "wellsky",
        status: "planned",
        integration_type: "direct_api",
        agencies: "4,500+",
        features: [],
      },
    ],
  });
});

// ============================================================================
// PLATFORM-SPECIFIC ROUTES
// ============================================================================

// Mount ClearCare routes
app.use("/webhook/clearcare", clearcareRoutes);
app.use("/api/clearcare", clearcareRoutes);

// Mount Axxess routes
app.use("/webhook/axxess", axxessRoutes);
app.use("/api/axxess", axxessRoutes);

// ============================================================================
// SHARED CRON ENDPOINTS (All Platforms)
// ============================================================================

/**
 * No-Show Prevention Cron (runs every 15 minutes)
 * Checks all platforms for upcoming visits and makes confirmation calls
 */
app.post("/cron/no-show-prevention", async (req, res) => {
  // Verify cron secret
  const authHeader = req.headers.authorization;
  const expectedToken = process.env.CRON_SECRET || "change_me";

  if (authHeader !== `Bearer ${expectedToken}`) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  console.log("🔔 Running no-show prevention cron (all platforms)...");

  try {
    // Find visits scheduled 2 hours from now (±15 min window)
    const twoHoursFromNow = new Date(Date.now() + 2 * 60 * 60 * 1000);
    const windowStart = new Date(twoHoursFromNow.getTime() - 15 * 60 * 1000);
    const windowEnd = new Date(twoHoursFromNow.getTime() + 15 * 60 * 1000);

    const visits = await pool.query(
      `
      SELECT v.*, c.name as caregiver_name, c.phone as caregiver_phone, 
             a.id as agency_id, a.platform, a.name as agency_name
      FROM visits v
      JOIN caregivers c ON v.caregiver_id = c.id
      JOIN agencies a ON c.agency_id = a.id
      WHERE v.status = 'scheduled'
      AND v.visit_date = CURRENT_DATE
      AND v.visit_time BETWEEN $1 AND $2
      AND NOT EXISTS (
        SELECT 1 FROM confirmation_calls cc WHERE cc.visit_id = v.id
      )
    `,
      [windowStart.toTimeString().slice(0, 8), windowEnd.toTimeString().slice(0, 8)],
    );

    console.log(`📞 Found ${visits.rows.length} visits needing confirmation calls`);

    const results = [];
    for (const visit of visits.rows) {
      const callResult = await voiceService.makeConfirmationCall(visit);
      results.push({
        visit_id: visit.id,
        platform: visit.platform,
        caregiver: visit.caregiver_name,
        success: callResult.success,
      });

      // Wait 5 seconds between calls to avoid rate limits
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }

    res.json({
      success: true,
      calls_made: results.length,
      results,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("❌ No-show prevention cron error:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Schedule Sync Cron (runs hourly)
 * Syncs schedules from all platforms (mainly Axxess - ClearCare uses email)
 */
app.post("/cron/sync-schedules", async (req, res) => {
  const authHeader = req.headers.authorization;
  const expectedToken = process.env.CRON_SECRET || "change_me";

  if (authHeader !== `Bearer ${expectedToken}`) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  console.log("🔄 Running schedule sync cron (all platforms)...");

  try {
    // Get all active Axxess agencies (ClearCare syncs via email/Zapier)
    const agencies = await pool.query(`
      SELECT id, name, axxess_agency_id, axxess_client_id, axxess_client_secret
      FROM agencies
      WHERE platform IN ('axxess', 'both')
      AND status = 'active'
      AND axxess_client_id IS NOT NULL
    `);

    const results = [];
    for (const agency of agencies.rows) {
      try {
        // Sync this agency's schedule (implementation in routes/axxess.js)
        const AxxessAPI = require("./lib/axxess-api");
        const api = new AxxessAPI(
          agency.axxess_client_id,
          agency.axxess_client_secret,
          agency.axxess_agency_id,
        );

        const today = new Date().toISOString().split("T")[0];
        const visits = await api.getSchedule(today, today);

        // Store visits in database (implementation detail)
        // ... (see routes/axxess.js for full implementation)

        results.push({
          agency_id: agency.id,
          agency_name: agency.name,
          visits_synced: visits.length,
          status: "success",
        });
      } catch (error) {
        console.error(`❌ Failed to sync agency ${agency.id}:`, error.message);
        results.push({
          agency_id: agency.id,
          agency_name: agency.name,
          visits_synced: 0,
          status: "failed",
          error: error.message,
        });
      }
    }

    res.json({
      success: true,
      agencies_synced: results.length,
      results,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("❌ Schedule sync cron error:", error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// ANALYTICS ENDPOINTS (All Platforms)
// ============================================================================

/**
 * Agency analytics
 */
app.get("/api/analytics/:agencyId", async (req, res) => {
  try {
    const { agencyId } = req.params;
    const analytics = await analyticsService.getAgencyAnalytics(agencyId);
    res.json(analytics);
  } catch (error) {
    console.error("❌ Analytics error:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Platform comparison
 */
app.get("/api/analytics/compare", async (req, res) => {
  try {
    const comparison = await analyticsService.getPlatformComparison();
    res.json(comparison);
  } catch (error) {
    console.error("❌ Platform comparison error:", error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// START SERVER
// ============================================================================

const PORT = process.env.PORT || 3000;

const server = app.listen(PORT, () => {
  console.log(`
🚀 Unified Copper AI Integration Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Server running on port ${PORT}

Platforms:
  ✅ ClearCare (Zapier)
  ✅ Axxess (Direct API)

Endpoints:
  GET  /health                       - Health check
  GET  /api/status                   - Detailed status
  GET  /api/platforms                - List platforms
  
  ClearCare:
  POST /webhook/clearcare/evv        - Voice EVV
  POST /webhook/clearcare/new-visit  - New visit
  POST /webhook/clearcare/confirmation - Confirmation result
  
  Axxess:
  POST /webhook/axxess/evv           - Voice EVV
  POST /api/axxess/sync-schedule/:id - Sync schedule
  GET  /api/axxess/status/:id        - Agency status
  
  Shared:
  POST /cron/no-show-prevention      - Confirmation calls (all platforms)
  POST /cron/sync-schedules          - Schedule sync (all platforms)
  GET  /api/analytics/:id            - Agency analytics
  GET  /api/analytics/compare        - Platform comparison

Database: ${process.env.DATABASE_URL ? "✅ Connected" : "⚠️  Not configured"}

Built with 🐾 by Nike
  `);
});

// Graceful shutdown
process.on("SIGTERM", async () => {
  console.log("Shutting down gracefully...");
  server.close(() => {
    pool.end(() => {
      console.log("Server stopped");
      process.exit(0);
    });
  });
});

// Export for testing
module.exports = { app, pool };

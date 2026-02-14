/**
 * Axxess Routes
 *
 * Handles Axxess-specific webhooks and API endpoints.
 * Integration type: Direct API (OAuth 2.0 + REST)
 *
 * Author: Nike 🐾
 */

const express = require("express");
const router = express.Router();
const crypto = require("crypto");

// Shared services
const voiceService = require("../services/voice");
const alertService = require("../services/alerts");

// Axxess API client
const AxxessAPI = require("../lib/axxess-api");

// Database pool
const { Pool } = require("pg");
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// Webhook secret
const WEBHOOK_SECRET = process.env.ZAPIER_WEBHOOK_SECRET || "change_me_in_production";

// ============================================================================
// MIDDLEWARE
// ============================================================================

/**
 * Verify webhook signature
 */
function verifyWebhookSignature(req, res, next) {
  const signature = req.headers["x-webhook-signature"];
  if (!signature) {
    return res.status(401).json({ error: "Missing webhook signature" });
  }

  const payload = JSON.stringify(req.body);
  const expectedSignature = crypto
    .createHmac("sha256", WEBHOOK_SECRET)
    .update(payload)
    .digest("hex");

  if (signature !== expectedSignature) {
    return res.status(401).json({ error: "Invalid webhook signature" });
  }

  next();
}

/**
 * Get Axxess API client for an agency
 */
async function getAxxessClient(agencyId) {
  const result = await pool.query(
    "SELECT axxess_client_id, axxess_client_secret, axxess_agency_id FROM agencies WHERE id = $1",
    [agencyId],
  );

  if (result.rows.length === 0) {
    throw new Error("Agency not found");
  }

  const agency = result.rows[0];

  if (!agency.axxess_client_id || !agency.axxess_client_secret) {
    throw new Error("Axxess API credentials not configured for this agency");
  }

  return new AxxessAPI(
    agency.axxess_client_id,
    agency.axxess_client_secret,
    agency.axxess_agency_id,
  );
}

// ============================================================================
// WEBHOOK ENDPOINTS
// ============================================================================

/**
 * Voice EVV Clock In/Out
 * Receives EVV events from voice calls and submits to Axxess API
 */
router.post("/evv", verifyWebhookSignature, async (req, res) => {
  const {
    event,
    caregiver_phone,
    caregiver_name,
    client_name,
    timestamp,
    location,
    transcript,
    agency_id,
  } = req.body;

  console.log("📞 Axxess EVV Event:", event, caregiver_name, client_name);

  try {
    // Find caregiver
    const caregiverResult = await pool.query(
      "SELECT * FROM caregivers WHERE phone = $1 AND agency_id = $2",
      [caregiver_phone, agency_id],
    );

    if (caregiverResult.rows.length === 0) {
      console.warn(`⚠️  Axxess caregiver not found: ${caregiver_phone}`);
      return res.status(404).json({ error: "Caregiver not found" });
    }

    const caregiver = caregiverResult.rows[0];

    // Find today's visit
    const visitDate = new Date().toISOString().split("T")[0];
    const visitResult = await pool.query(
      `SELECT * FROM visits 
       WHERE caregiver_id = $1 AND client_name ILIKE $2 AND visit_date = $3
       AND synced_from = 'axxess'
       ORDER BY visit_time ASC LIMIT 1`,
      [caregiver.id, `%${client_name}%`, visitDate],
    );

    if (visitResult.rows.length === 0) {
      console.warn(`⚠️  No Axxess visit found for ${caregiver_name} with ${client_name} today`);
      return res.status(404).json({ error: "Visit not found" });
    }

    const visit = visitResult.rows[0];

    // Log EVV event in our database
    await pool.query(
      `INSERT INTO evv_logs (visit_id, event_type, timestamp, phone_number, location_lat, location_lon, transcript)
       VALUES ($1, $2, $3, $4, $5, $6, $7)`,
      [visit.id, event, timestamp, caregiver_phone, location?.lat, location?.lon, transcript],
    );

    // Submit to Axxess API
    const axxessClient = await getAxxessClient(agency_id);

    if (event === "clock_in") {
      await axxessClient.submitClockIn(
        visit.axxess_visit_id,
        caregiver.axxess_caregiver_id,
        timestamp,
        location,
      );
    } else {
      await axxessClient.submitClockOut(
        visit.axxess_visit_id,
        caregiver.axxess_caregiver_id,
        timestamp,
        location,
      );
    }

    // Update visit status in our database
    const newStatus = event === "clock_in" ? "in_progress" : "completed";
    await pool.query("UPDATE visits SET status = $1, updated_at = NOW() WHERE id = $2", [
      newStatus,
      visit.id,
    ]);

    // Record API call for rate limiting
    await pool.query(
      `INSERT INTO axxess_sync_log (agency_id, sync_type, sync_status, records_synced)
       VALUES ($1, 'evv', 'success', 1)`,
      [agency_id],
    );

    console.log(`✅ Axxess EVV submitted: ${event} for visit #${visit.id}`);

    res.json({
      success: true,
      platform: "axxess",
      visit_id: visit.id,
      status: newStatus,
      axxess_visit_id: visit.axxess_visit_id,
      message: `${event} submitted to Axxess API`,
    });
  } catch (error) {
    console.error("❌ Axxess EVV webhook error:", error);

    // Log failed sync
    if (agency_id) {
      await pool
        .query(
          `INSERT INTO axxess_sync_log (agency_id, sync_type, sync_status, error_message)
         VALUES ($1, 'evv', 'failed', $2)`,
          [agency_id, error.message],
        )
        .catch(console.error);
    }

    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// API ENDPOINTS (Manual Operations)
// ============================================================================

/**
 * Sync schedule from Axxess API
 */
router.post("/sync-schedule/:agencyId", async (req, res) => {
  const { agencyId } = req.params;
  const { startDate, endDate } = req.body;

  console.log(`🔄 Syncing Axxess schedule for agency ${agencyId}...`);

  try {
    const axxessClient = await getAxxessClient(agencyId);

    // Get schedule from Axxess
    const today = startDate || new Date().toISOString().split("T")[0];
    const end = endDate || today;

    const visits = await axxessClient.getSchedule(today, end);
    console.log(`Found ${visits.length} visits from Axxess`);

    let synced = 0;
    let errors = 0;

    for (const axxessVisit of visits) {
      try {
        // Find or create caregiver
        let caregiverResult = await pool.query(
          "SELECT * FROM caregivers WHERE axxess_caregiver_id = $1 AND agency_id = $2",
          [axxessVisit.caregiver_id, agencyId],
        );

        let caregiver;
        if (caregiverResult.rows.length === 0) {
          // Fetch caregiver details from Axxess
          const axxessCaregiver = await axxessClient.getCaregiver(axxessVisit.caregiver_id);

          // Create caregiver in our database
          const insertResult = await pool.query(
            `INSERT INTO caregivers (phone, name, agency_id, axxess_caregiver_id, axxess_employee_number)
             VALUES ($1, $2, $3, $4, $5) RETURNING *`,
            [
              axxessCaregiver.phone,
              axxessCaregiver.name,
              agencyId,
              axxessCaregiver.id,
              axxessCaregiver.employee_number,
            ],
          );
          caregiver = insertResult.rows[0];
        } else {
          caregiver = caregiverResult.rows[0];
        }

        // Check if visit already exists
        const existingVisit = await pool.query("SELECT id FROM visits WHERE axxess_visit_id = $1", [
          axxessVisit.id,
        ]);

        if (existingVisit.rows.length === 0) {
          // Create new visit
          await pool.query(
            `INSERT INTO visits (caregiver_id, client_name, visit_date, visit_time, duration_minutes, status, axxess_visit_id, axxess_client_id, synced_from)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'axxess')`,
            [
              caregiver.id,
              axxessVisit.client_name,
              axxessVisit.visit_date,
              axxessVisit.visit_time,
              axxessVisit.duration_minutes,
              axxessVisit.status || "scheduled",
              axxessVisit.id,
              axxessVisit.client_id,
            ],
          );
          synced++;
        } else {
          // Update existing visit
          await pool.query(
            `UPDATE visits SET 
             visit_date = $1, visit_time = $2, duration_minutes = $3, status = $4, updated_at = NOW()
             WHERE axxess_visit_id = $5`,
            [
              axxessVisit.visit_date,
              axxessVisit.visit_time,
              axxessVisit.duration_minutes,
              axxessVisit.status,
              axxessVisit.id,
            ],
          );
          synced++;
        }
      } catch (error) {
        console.error(`Error syncing visit ${axxessVisit.id}:`, error.message);
        errors++;
      }
    }

    // Log sync
    await pool.query(
      `INSERT INTO axxess_sync_log (agency_id, sync_type, sync_status, records_synced)
       VALUES ($1, 'schedule', $2, $3)`,
      [agencyId, errors > 0 ? "partial" : "success", synced],
    );

    res.json({
      success: true,
      platform: "axxess",
      agency_id: parseInt(agencyId),
      visits_synced: synced,
      errors,
      total: visits.length,
    });
  } catch (error) {
    console.error("❌ Axxess schedule sync error:", error);

    await pool
      .query(
        `INSERT INTO axxess_sync_log (agency_id, sync_type, sync_status, error_message)
       VALUES ($1, 'schedule', 'failed', $2)`,
        [agencyId, error.message],
      )
      .catch(console.error);

    res.status(500).json({ error: error.message });
  }
});

/**
 * Sync caregivers from Axxess API
 */
router.post("/sync-caregivers/:agencyId", async (req, res) => {
  const { agencyId } = req.params;

  console.log(`🔄 Syncing Axxess caregivers for agency ${agencyId}...`);

  try {
    const axxessClient = await getAxxessClient(agencyId);

    // Get caregivers from Axxess
    const caregivers = await axxessClient.getCaregivers("active");
    console.log(`Found ${caregivers.length} caregivers from Axxess`);

    let synced = 0;
    let errors = 0;

    for (const axxessCaregiver of caregivers) {
      try {
        // Check if caregiver exists
        const existingCaregiver = await pool.query(
          "SELECT id FROM caregivers WHERE axxess_caregiver_id = $1 AND agency_id = $2",
          [axxessCaregiver.id, agencyId],
        );

        if (existingCaregiver.rows.length === 0) {
          // Create new caregiver
          await pool.query(
            `INSERT INTO caregivers (phone, name, email, language, agency_id, axxess_caregiver_id, axxess_employee_number, status)
             VALUES ($1, $2, $3, $4, $5, $6, $7, 'active')`,
            [
              axxessCaregiver.phone,
              axxessCaregiver.name,
              axxessCaregiver.email,
              axxessCaregiver.language || "en",
              agencyId,
              axxessCaregiver.id,
              axxessCaregiver.employee_number,
            ],
          );
          synced++;
        } else {
          // Update existing caregiver
          await pool.query(
            `UPDATE caregivers SET 
             phone = $1, name = $2, email = $3, language = $4, updated_at = NOW()
             WHERE axxess_caregiver_id = $5 AND agency_id = $6`,
            [
              axxessCaregiver.phone,
              axxessCaregiver.name,
              axxessCaregiver.email,
              axxessCaregiver.language,
              axxessCaregiver.id,
              agencyId,
            ],
          );
          synced++;
        }
      } catch (error) {
        console.error(`Error syncing caregiver ${axxessCaregiver.id}:`, error.message);
        errors++;
      }
    }

    // Log sync
    await pool.query(
      `INSERT INTO axxess_sync_log (agency_id, sync_type, sync_status, records_synced)
       VALUES ($1, 'caregivers', $2, $3)`,
      [agencyId, errors > 0 ? "partial" : "success", synced],
    );

    res.json({
      success: true,
      platform: "axxess",
      agency_id: parseInt(agencyId),
      caregivers_synced: synced,
      errors,
      total: caregivers.length,
    });
  } catch (error) {
    console.error("❌ Axxess caregiver sync error:", error);

    await pool
      .query(
        `INSERT INTO axxess_sync_log (agency_id, sync_type, sync_status, error_message)
       VALUES ($1, 'caregivers', 'failed', $2)`,
        [agencyId, error.message],
      )
      .catch(console.error);

    res.status(500).json({ error: error.message });
  }
});

/**
 * Get Axxess agency status
 */
router.get("/status/:agencyId", async (req, res) => {
  const { agencyId } = req.params;

  try {
    // Get agency info
    const agencyResult = await pool.query(
      "SELECT * FROM agencies WHERE id = $1 AND platform IN ('axxess', 'both')",
      [agencyId],
    );

    if (agencyResult.rows.length === 0) {
      return res.status(404).json({ error: "Axxess agency not found" });
    }

    const agency = agencyResult.rows[0];

    // Get last sync times
    const lastSyncs = await pool.query(
      `SELECT sync_type, MAX(synced_at) as last_sync, sync_status
       FROM axxess_sync_log
       WHERE agency_id = $1
       GROUP BY sync_type, sync_status
       ORDER BY sync_type, last_sync DESC`,
      [agencyId],
    );

    // Test API connection
    let apiStatus = "unknown";
    try {
      const axxessClient = await getAxxessClient(agencyId);
      await axxessClient.testConnection();
      apiStatus = "connected";
    } catch (error) {
      apiStatus = "error: " + error.message;
    }

    res.json({
      success: true,
      platform: "axxess",
      agency: {
        id: agency.id,
        name: agency.name,
        axxess_agency_id: agency.axxess_agency_id,
        status: agency.status,
      },
      api_status: apiStatus,
      last_syncs: lastSyncs.rows,
      api_credentials_configured: !!(agency.axxess_client_id && agency.axxess_client_secret),
    });
  } catch (error) {
    console.error("❌ Error fetching Axxess status:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get Axxess agencies
 */
router.get("/agencies", async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT id, name, platform, status, owner_phone, axxess_agency_id, created_at
       FROM agencies
       WHERE platform IN ('axxess', 'both')
       ORDER BY created_at DESC`,
    );

    res.json({
      success: true,
      platform: "axxess",
      count: result.rows.length,
      agencies: result.rows,
    });
  } catch (error) {
    console.error("❌ Error fetching Axxess agencies:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

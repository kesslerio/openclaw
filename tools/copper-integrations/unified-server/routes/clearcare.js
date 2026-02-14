/**
 * ClearCare Routes
 *
 * Handles ClearCare-specific webhooks and API endpoints.
 * Integration type: Zapier-based (email + webhooks)
 *
 * Author: Nike 🐾
 */

const express = require("express");
const router = express.Router();
const crypto = require("crypto");

// Shared services
const voiceService = require("../services/voice");
const alertService = require("../services/alerts");

// Database pool (imported from server.js)
const { Pool } = require("pg");
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// Webhook secret for security
const WEBHOOK_SECRET = process.env.ZAPIER_WEBHOOK_SECRET || "change_me_in_production";

// ============================================================================
// MIDDLEWARE
// ============================================================================

/**
 * Verify webhook signature (security)
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

// ============================================================================
// WEBHOOK ENDPOINTS (from Zapier)
// ============================================================================

/**
 * Voice EVV Clock In/Out
 * Receives EVV events from Retell voice calls and updates ClearCare
 */
router.post("/evv", verifyWebhookSignature, async (req, res) => {
  const { event, caregiver_phone, caregiver_name, client_name, timestamp, location, transcript } =
    req.body;

  console.log("📞 ClearCare EVV Event:", event, caregiver_name, client_name);

  try {
    // Find caregiver by phone
    const caregiverResult = await pool.query("SELECT * FROM caregivers WHERE phone = $1", [
      caregiver_phone,
    ]);

    if (caregiverResult.rows.length === 0) {
      console.warn(`⚠️  Caregiver not found: ${caregiver_phone}`);
      return res.status(404).json({ error: "Caregiver not found" });
    }

    const caregiver = caregiverResult.rows[0];

    // Find today's visit for this caregiver + client
    const visitDate = new Date().toISOString().split("T")[0];
    const visitResult = await pool.query(
      `SELECT * FROM visits 
       WHERE caregiver_id = $1 AND client_name ILIKE $2 AND visit_date = $3 
       AND synced_from = 'clearcare'
       ORDER BY visit_time ASC LIMIT 1`,
      [caregiver.id, `%${client_name}%`, visitDate],
    );

    if (visitResult.rows.length === 0) {
      console.warn(`⚠️  No ClearCare visit found for ${caregiver_name} with ${client_name} today`);
      return res.status(404).json({ error: "Visit not found" });
    }

    const visit = visitResult.rows[0];

    // Log EVV event
    await pool.query(
      `INSERT INTO evv_logs (visit_id, event_type, timestamp, phone_number, location_lat, location_lon, transcript)
       VALUES ($1, $2, $3, $4, $5, $6, $7)`,
      [visit.id, event, timestamp, caregiver_phone, location?.lat, location?.lon, transcript],
    );

    // Update visit status
    const newStatus = event === "clock_in" ? "in_progress" : "completed";
    await pool.query("UPDATE visits SET status = $1, updated_at = NOW() WHERE id = $2", [
      newStatus,
      visit.id,
    ]);

    console.log(`✅ ClearCare EVV logged: ${event} for visit #${visit.id}`);

    // Send success response to Zapier (will update ClearCare via email)
    res.json({
      success: true,
      platform: "clearcare",
      visit_id: visit.id,
      status: newStatus,
      clearcare_visit_id: visit.clearcare_visit_id,
      message: `${event} recorded at ${timestamp}`,
      zapier_action: "send_email_to_clearcare",
    });
  } catch (error) {
    console.error("❌ ClearCare EVV webhook error:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * New Visit Assigned (from ClearCare)
 * Receives schedule changes from Zapier email parser
 */
router.post("/new-visit", verifyWebhookSignature, async (req, res) => {
  const {
    caregiver_name,
    caregiver_phone,
    client_name,
    visit_date,
    visit_time,
    duration_minutes,
    address,
    clearcare_visit_id,
  } = req.body;

  console.log("📅 ClearCare new visit:", caregiver_name, client_name, visit_date, visit_time);

  try {
    // Find or create caregiver
    let caregiverResult = await pool.query("SELECT * FROM caregivers WHERE phone = $1", [
      caregiver_phone,
    ]);

    let caregiver;
    if (caregiverResult.rows.length === 0) {
      // Auto-create caregiver from ClearCare data
      const insertResult = await pool.query(
        "INSERT INTO caregivers (phone, name, clearcare_caregiver_id) VALUES ($1, $2, $3) RETURNING *",
        [caregiver_phone, caregiver_name, `CC-AUTO-${Date.now()}`],
      );
      caregiver = insertResult.rows[0];
      console.log(`✨ Auto-created caregiver: ${caregiver_name}`);
    } else {
      caregiver = caregiverResult.rows[0];
    }

    // Create visit record
    const visitResult = await pool.query(
      `INSERT INTO visits (caregiver_id, client_name, client_address, visit_date, visit_time, duration_minutes, status, clearcare_visit_id, synced_from)
       VALUES ($1, $2, $3, $4, $5, $6, 'scheduled', $7, 'clearcare') RETURNING *`,
      [
        caregiver.id,
        client_name,
        address,
        visit_date,
        visit_time,
        duration_minutes,
        clearcare_visit_id,
      ],
    );
    const visit = visitResult.rows[0];

    // Call caregiver with notification
    const callResult = await voiceService.makeScheduleNotificationCall({
      caregiver_name,
      caregiver_phone,
      client_name,
      visit_date,
      visit_time,
      duration_minutes,
      client_address: address,
    });

    if (!callResult.success) {
      // Fallback to SMS
      const smsMessage = `NEW VISIT: ${client_name} on ${visit_date} at ${visit_time}. Duration: ${duration_minutes} min. Address: ${address || "Check ClearCare"}. Call (469) 420-CARE if questions.`;
      await alertService.sendSMSAlert(caregiver_phone, smsMessage);
    }

    res.json({
      success: true,
      platform: "clearcare",
      visit_id: visit.id,
      clearcare_visit_id,
      call_result: callResult,
      message: "Caregiver notified",
    });
  } catch (error) {
    console.error("❌ ClearCare new visit webhook error:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Confirmation Call Result (from Retell)
 * Receives outcome of 2-hour pre-visit confirmation calls
 */
router.post("/confirmation", verifyWebhookSignature, async (req, res) => {
  const { visit_id, answered, confirmed, transcript, call_duration_seconds } = req.body;

  console.log("☎️  ClearCare confirmation call result:", visit_id, answered, confirmed);

  try {
    // Calculate risk level
    let riskLevel = "LOW";
    if (!answered) {
      riskLevel = "HIGH";
    } else if (!confirmed) {
      riskLevel = "CRITICAL";
    }

    // Log confirmation call
    await pool.query(
      `INSERT INTO confirmation_calls (visit_id, call_time, answered, confirmed, transcript, risk_level, call_duration_seconds)
       VALUES ($1, NOW(), $2, $3, $4, $5, $6)`,
      [visit_id, answered, confirmed, transcript, riskLevel, call_duration_seconds],
    );

    // If HIGH or CRITICAL risk, alert agency
    if (riskLevel === "HIGH" || riskLevel === "CRITICAL") {
      const visitResult = await pool.query(
        `SELECT v.*, c.name as caregiver_name, c.phone as caregiver_phone, a.owner_phone, a.name as agency_name
         FROM visits v
         JOIN caregivers c ON v.caregiver_id = c.id
         JOIN agencies a ON c.agency_id = a.id
         WHERE v.id = $1`,
        [visit_id],
      );

      if (visitResult.rows.length > 0) {
        const visit = visitResult.rows[0];
        visit.risk_reason = !answered
          ? "Didn't answer confirmation call"
          : "Said they can't make it";
        visit.platform = "clearcare";

        await alertService.sendNoShowAlert(visit, riskLevel);
      }
    }

    res.json({
      success: true,
      platform: "clearcare",
      risk_level: riskLevel,
      alert_sent: riskLevel !== "LOW",
    });
  } catch (error) {
    console.error("❌ ClearCare confirmation webhook error:", error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// API ENDPOINTS (for manual operations)
// ============================================================================

/**
 * Get ClearCare agencies
 */
router.get("/agencies", async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT id, name, platform, status, owner_phone, created_at
       FROM agencies
       WHERE platform IN ('clearcare', 'both')
       ORDER BY created_at DESC`,
    );

    res.json({
      success: true,
      platform: "clearcare",
      count: result.rows.length,
      agencies: result.rows,
    });
  } catch (error) {
    console.error("❌ Error fetching ClearCare agencies:", error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get ClearCare agency details
 */
router.get("/agencies/:id", async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      "SELECT * FROM agencies WHERE id = $1 AND platform IN ('clearcare', 'both')",
      [id],
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "ClearCare agency not found" });
    }

    res.json({
      success: true,
      platform: "clearcare",
      agency: result.rows[0],
    });
  } catch (error) {
    console.error("❌ Error fetching ClearCare agency:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

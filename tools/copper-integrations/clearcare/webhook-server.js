#!/usr/bin/env node
/**
 * Copper AI - ClearCare Integration Webhook Server
 * 
 * Handles webhooks from Zapier and triggers voice calls via Retell.
 * 
 * Author: Nike 🐾
 * Created: Feb 3, 2026
 */

const express = require('express');
const { Pool } = require('pg');
const axios = require('axios');
const crypto = require('crypto');

// Initialize Express
const app = express();
app.use(express.json());

// Database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://localhost:5432/copper_ai'
});

// Retell API configuration
const RETELL_API_KEY = process.env.RETELL_API_KEY;
const RETELL_API_URL = 'https://api.retellai.com/v2';

// Telegram notification (for pilot agencies)
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const ARVIND_TELEGRAM_ID = process.env.ARVIND_TELEGRAM_ID || '7372113399';

// Twilio SMS (backup alerts)
const TWILIO_ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID;
const TWILIO_AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN;
const TWILIO_PHONE_NUMBER = process.env.TWILIO_PHONE_NUMBER || '+14697421095';

// Webhook secret for security
const WEBHOOK_SECRET = process.env.ZAPIER_WEBHOOK_SECRET || 'change_me_in_production';

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Verify webhook signature (security)
function verifyWebhookSignature(req, res, next) {
  const signature = req.headers['x-webhook-signature'];
  if (!signature) {
    return res.status(401).json({ error: 'Missing webhook signature' });
  }

  const payload = JSON.stringify(req.body);
  const expectedSignature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');

  if (signature !== expectedSignature) {
    return res.status(401).json({ error: 'Invalid webhook signature' });
  }

  next();
}

// Logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// ============================================================================
// RETELL VOICE AI FUNCTIONS
// ============================================================================

/**
 * Make a voice call via Retell API
 */
async function makeVoiceCall(phoneNumber, prompt, metadata = {}) {
  try {
    const response = await axios.post(
      `${RETELL_API_URL}/create-phone-call`,
      {
        from_number: TWILIO_PHONE_NUMBER,
        to_number: phoneNumber,
        override_agent_id: process.env.RETELL_AGENT_ID,
        retell_llm_dynamic_variables: {
          custom_prompt: prompt,
          ...metadata
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${RETELL_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log(`✅ Call initiated to ${phoneNumber}:`, response.data);
    return {
      success: true,
      call_id: response.data.call_id,
      status: response.data.call_status
    };
  } catch (error) {
    console.error(`❌ Failed to call ${phoneNumber}:`, error.response?.data || error.message);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

/**
 * Generate confirmation call prompt
 */
function generateConfirmationPrompt(caregiver, visit) {
  const visitTime = new Date(visit.visit_time).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });

  return `Hi ${caregiver.name}, this is Copper AI calling to confirm your upcoming visit.

You have a visit scheduled with ${visit.client_name} today at ${visitTime}.

Can you confirm you'll be there on time?

Please respond with "yes I'll be there" or "no I can't make it" or "I need to reschedule."

This is an automated confirmation call to prevent no-shows. If you confirm, you're all set. If you can't make it, I'll alert the agency so they can find a replacement.

What's your response?`;
}

/**
 * Generate EVV clock-in/out prompt
 */
function generateEVVPrompt() {
  return `Hi! Welcome to the Copper AI EVV hotline.

I can help you clock in or clock out of your visits.

Please tell me:
1. Your name
2. Whether you're clocking IN or OUT
3. The client's name

For example: "This is Maria, I'm clocking in for Mrs. Johnson."

Go ahead!`;
}

/**
 * Generate schedule notification prompt
 */
function generateScheduleNotificationPrompt(caregiver, visit) {
  const visitDate = new Date(visit.visit_date).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric'
  });
  const visitTime = new Date(visit.visit_time).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });

  return `Hi ${caregiver.name}, this is Copper AI with an important schedule update.

You have a NEW visit assigned:

Client: ${visit.client_name}
Date: ${visitDate}
Time: ${visitTime}
Duration: ${visit.duration_minutes} minutes
Address: ${visit.address || 'Check ClearCare for address'}

Please confirm you received this message by saying "got it" or "I'll be there."

If you have any conflicts or questions, please contact your agency immediately.`;
}

// ============================================================================
// TELEGRAM ALERT FUNCTIONS
// ============================================================================

/**
 * Send Telegram alert
 */
async function sendTelegramAlert(message, chatId = ARVIND_TELEGRAM_ID) {
  if (!TELEGRAM_BOT_TOKEN) {
    console.warn('⚠️  Telegram bot token not configured, skipping alert');
    return { success: false, error: 'No token configured' };
  }

  try {
    const response = await axios.post(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        chat_id: chatId,
        text: message,
        parse_mode: 'Markdown'
      }
    );

    console.log('✅ Telegram alert sent');
    return { success: true, message_id: response.data.result.message_id };
  } catch (error) {
    console.error('❌ Failed to send Telegram alert:', error.response?.data || error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Send SMS alert via Twilio (backup)
 */
async function sendSMSAlert(phoneNumber, message) {
  if (!TWILIO_ACCOUNT_SID || !TWILIO_AUTH_TOKEN) {
    console.warn('⚠️  Twilio not configured, skipping SMS');
    return { success: false, error: 'No Twilio credentials' };
  }

  try {
    const auth = Buffer.from(`${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}`).toString('base64');
    
    const response = await axios.post(
      `https://api.twilio.com/2010-04-01/Accounts/${TWILIO_ACCOUNT_SID}/Messages.json`,
      new URLSearchParams({
        From: TWILIO_PHONE_NUMBER,
        To: phoneNumber,
        Body: message
      }),
      {
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );

    console.log(`✅ SMS sent to ${phoneNumber}`);
    return { success: true, sid: response.data.sid };
  } catch (error) {
    console.error(`❌ Failed to send SMS to ${phoneNumber}:`, error.response?.data || error.message);
    return { success: false, error: error.message };
  }
}

// ============================================================================
// DATABASE HELPER FUNCTIONS
// ============================================================================

/**
 * Find caregiver by phone number
 */
async function findCaregiver(phone) {
  const result = await pool.query(
    'SELECT * FROM caregivers WHERE phone = $1',
    [phone]
  );
  return result.rows[0];
}

/**
 * Find visit by ID or details
 */
async function findVisit(visitId, caregiverId, visitDate, visitTime) {
  if (visitId) {
    const result = await pool.query(
      'SELECT * FROM visits WHERE id = $1',
      [visitId]
    );
    return result.rows[0];
  }

  const result = await pool.query(
    'SELECT * FROM visits WHERE caregiver_id = $1 AND visit_date = $2 AND visit_time = $3',
    [caregiverId, visitDate, visitTime]
  );
  return result.rows[0];
}

/**
 * Log EVV event
 */
async function logEVV(visitId, eventType, phoneNumber, transcript, location = null) {
  await pool.query(
    `INSERT INTO evv_logs (visit_id, event_type, timestamp, phone_number, location_lat, location_lon, transcript)
     VALUES ($1, $2, NOW(), $3, $4, $5, $6)`,
    [visitId, eventType, phoneNumber, location?.lat, location?.lon, transcript]
  );
}

/**
 * Log confirmation call
 */
async function logConfirmationCall(visitId, answered, confirmed, transcript, riskLevel) {
  await pool.query(
    `INSERT INTO confirmation_calls (visit_id, call_time, answered, confirmed, transcript, risk_level)
     VALUES ($1, NOW(), $2, $3, $4, $5)`,
    [visitId, answered, confirmed, transcript, riskLevel]
  );
}

/**
 * Update visit status
 */
async function updateVisitStatus(visitId, status) {
  await pool.query(
    'UPDATE visits SET status = $1 WHERE id = $2',
    [status, visitId]
  );
}

// ============================================================================
// WEBHOOK ENDPOINTS
// ============================================================================

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

/**
 * Webhook: Voice EVV Clock In/Out
 * 
 * Receives EVV events from Retell voice calls and updates database.
 */
app.post('/webhook/evv', verifyWebhookSignature, async (req, res) => {
  const { event, caregiver_phone, caregiver_name, client_name, timestamp, location, transcript } = req.body;

  console.log('📞 EVV Event:', event, caregiver_name, client_name);

  try {
    // Find caregiver
    const caregiver = await findCaregiver(caregiver_phone);
    if (!caregiver) {
      console.warn(`⚠️  Caregiver not found: ${caregiver_phone}`);
      return res.status(404).json({ error: 'Caregiver not found' });
    }

    // Find today's visit for this caregiver + client
    const visitDate = new Date().toISOString().split('T')[0];
    const visit = await pool.query(
      `SELECT * FROM visits 
       WHERE caregiver_id = $1 AND client_name ILIKE $2 AND visit_date = $3 
       ORDER BY visit_time ASC LIMIT 1`,
      [caregiver.id, `%${client_name}%`, visitDate]
    );

    if (visit.rows.length === 0) {
      console.warn(`⚠️  No visit found for ${caregiver_name} with ${client_name} today`);
      return res.status(404).json({ error: 'Visit not found' });
    }

    const visitRecord = visit.rows[0];

    // Log EVV event
    await logEVV(visitRecord.id, event, caregiver_phone, transcript, location);

    // Update visit status
    const newStatus = event === 'clock_in' ? 'in_progress' : 'completed';
    await updateVisitStatus(visitRecord.id, newStatus);

    console.log(`✅ EVV logged: ${event} for visit #${visitRecord.id}`);

    // Send success response to Zapier (will update ClearCare)
    res.json({
      success: true,
      visit_id: visitRecord.id,
      status: newStatus,
      clearcare_visit_id: visitRecord.clearcare_visit_id,
      message: `${event} recorded at ${timestamp}`
    });

  } catch (error) {
    console.error('❌ EVV webhook error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Webhook: New Visit Assigned (from ClearCare)
 * 
 * Receives schedule changes from Zapier and calls caregiver to notify.
 */
app.post('/webhook/new-visit', verifyWebhookSignature, async (req, res) => {
  const { caregiver_name, caregiver_phone, client_name, visit_date, visit_time, duration_minutes, address } = req.body;

  console.log('📅 New visit assigned:', caregiver_name, client_name, visit_date, visit_time);

  try {
    // Find or create caregiver
    let caregiver = await findCaregiver(caregiver_phone);
    if (!caregiver) {
      // Auto-create caregiver (from ClearCare data)
      const result = await pool.query(
        'INSERT INTO caregivers (phone, name) VALUES ($1, $2) RETURNING *',
        [caregiver_phone, caregiver_name]
      );
      caregiver = result.rows[0];
      console.log(`✨ Auto-created caregiver: ${caregiver_name}`);
    }

    // Create visit record
    const visitResult = await pool.query(
      `INSERT INTO visits (caregiver_id, client_name, visit_date, visit_time, duration_minutes, status)
       VALUES ($1, $2, $3, $4, $5, 'scheduled') RETURNING *`,
      [caregiver.id, client_name, visit_date, visit_time, duration_minutes]
    );
    const visit = visitResult.rows[0];

    // Call caregiver with notification
    const prompt = generateScheduleNotificationPrompt(caregiver, { ...visit, address });
    const callResult = await makeVoiceCall(caregiver_phone, prompt, { visit_id: visit.id });

    if (!callResult.success) {
      // Fallback to SMS
      const smsMessage = `NEW VISIT: ${client_name} on ${visit_date} at ${visit_time}. Duration: ${duration_minutes} min. Address: ${address || 'Check ClearCare'}. Call (469) 420-CARE if questions.`;
      await sendSMSAlert(caregiver_phone, smsMessage);
    }

    res.json({
      success: true,
      visit_id: visit.id,
      call_result: callResult,
      message: 'Caregiver notified'
    });

  } catch (error) {
    console.error('❌ New visit webhook error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Webhook: Confirmation Call Result (from Retell)
 * 
 * Receives outcome of 2-hour pre-visit confirmation calls.
 */
app.post('/webhook/confirmation', verifyWebhookSignature, async (req, res) => {
  const { visit_id, answered, confirmed, transcript, call_duration_seconds } = req.body;

  console.log('☎️  Confirmation call result:', visit_id, answered, confirmed);

  try {
    // Calculate risk level
    let riskLevel = 'LOW';
    if (!answered) {
      riskLevel = 'HIGH';
    } else if (!confirmed) {
      riskLevel = 'CRITICAL';
    }

    // Log confirmation call
    await logConfirmationCall(visit_id, answered, confirmed, transcript, riskLevel);

    // If HIGH or CRITICAL risk, alert agency
    if (riskLevel === 'HIGH' || riskLevel === 'CRITICAL') {
      const visit = await pool.query(
        `SELECT v.*, c.name as caregiver_name, c.phone as caregiver_phone, a.owner_phone, a.name as agency_name
         FROM visits v
         JOIN caregivers c ON v.caregiver_id = c.id
         JOIN agencies a ON c.agency_id = a.id
         WHERE v.id = $1`,
        [visit_id]
      );

      if (visit.rows.length > 0) {
        const v = visit.rows[0];
        const alertMessage = `🚨 *NO-SHOW RISK: ${riskLevel}*

**Caregiver:** ${v.caregiver_name} (${v.caregiver_phone})
**Client:** ${v.client_name}
**Visit Time:** ${v.visit_time}
**Issue:** ${!answered ? 'Didn\\'t answer confirmation call' : 'Said they can\\'t make it'}

**ACTION NEEDED:** Find backup caregiver NOW to prevent no-show.

Transcript: ${transcript || 'No answer'}`;

        // Alert agency owner
        if (v.owner_phone) {
          await sendSMSAlert(v.owner_phone, alertMessage.replace(/\*/g, ''));
        }

        // Alert Arvind (for pilot agencies)
        await sendTelegramAlert(alertMessage);
      }
    }

    res.json({
      success: true,
      risk_level: riskLevel,
      alert_sent: riskLevel !== 'LOW'
    });

  } catch (error) {
    console.error('❌ Confirmation webhook error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Cron Job: Schedule No-Show Prevention Calls
 * 
 * Run every 15 minutes to check for upcoming visits (2 hours ahead).
 */
app.post('/cron/no-show-prevention', async (req, res) => {
  const authHeader = req.headers.authorization;
  const expectedToken = process.env.CRON_SECRET || 'change_me';
  
  if (authHeader !== `Bearer ${expectedToken}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  console.log('🔔 Running no-show prevention cron...');

  try {
    // Find visits scheduled 2 hours from now (±15 min window)
    const twoHoursFromNow = new Date(Date.now() + 2 * 60 * 60 * 1000);
    const windowStart = new Date(twoHoursFromNow.getTime() - 15 * 60 * 1000);
    const windowEnd = new Date(twoHoursFromNow.getTime() + 15 * 60 * 1000);

    const visits = await pool.query(
      `SELECT v.*, c.name as caregiver_name, c.phone as caregiver_phone, c.language
       FROM visits v
       JOIN caregivers c ON v.caregiver_id = c.id
       WHERE v.status = 'scheduled'
       AND v.visit_date = CURRENT_DATE
       AND v.visit_time BETWEEN $1 AND $2
       AND NOT EXISTS (
         SELECT 1 FROM confirmation_calls cc WHERE cc.visit_id = v.id
       )`,
      [windowStart.toTimeString().slice(0, 8), windowEnd.toTimeString().slice(0, 8)]
    );

    console.log(`📞 Found ${visits.rows.length} visits needing confirmation calls`);

    const results = [];
    for (const visit of visits.rows) {
      const prompt = generateConfirmationPrompt(
        { name: visit.caregiver_name },
        visit
      );

      const callResult = await makeVoiceCall(visit.caregiver_phone, prompt, {
        visit_id: visit.id,
        confirmation: true
      });

      results.push({
        visit_id: visit.id,
        caregiver: visit.caregiver_name,
        success: callResult.success
      });

      // Wait 5 seconds between calls to avoid rate limits
      await new Promise(resolve => setTimeout(resolve, 5000));
    }

    res.json({
      success: true,
      calls_made: results.length,
      results
    });

  } catch (error) {
    console.error('❌ Cron error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// START SERVER
// ============================================================================

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`
🚀 Copper AI ClearCare Integration Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Server running on port ${PORT}

Endpoints:
  GET  /health                    - Health check
  POST /webhook/evv               - Voice EVV clock in/out
  POST /webhook/new-visit         - New visit assigned
  POST /webhook/confirmation      - Confirmation call result
  POST /cron/no-show-prevention   - Schedule confirmation calls

Database: ${process.env.DATABASE_URL ? '✅ Connected' : '⚠️  Not configured'}
Retell API: ${RETELL_API_KEY ? '✅ Configured' : '⚠️  Not configured'}
Telegram: ${TELEGRAM_BOT_TOKEN ? '✅ Configured' : '⚠️  Not configured'}
Twilio: ${TWILIO_ACCOUNT_SID ? '✅ Configured' : '⚠️  Not configured'}

Built with 🐾 by Nike
  `);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Shutting down gracefully...');
  await pool.end();
  process.exit(0);
});

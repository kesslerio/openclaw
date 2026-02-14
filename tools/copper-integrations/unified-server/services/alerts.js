/**
 * Alert Service (Shared across all platforms)
 * 
 * Handles alerts via:
 * - Telegram
 * - SMS (Twilio)
 * - Email (future)
 * 
 * Author: Nike 🐾
 */

const axios = require('axios');

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const ARVIND_TELEGRAM_ID = process.env.ARVIND_TELEGRAM_ID || '7372113399';
const TWILIO_ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID;
const TWILIO_AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN;
const TWILIO_PHONE_NUMBER = process.env.TWILIO_PHONE_NUMBER || '+14697421095';

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
 * Send SMS alert via Twilio
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

/**
 * Send no-show risk alert
 */
async function sendNoShowAlert(visit, riskLevel) {
  const message = `🚨 *NO-SHOW RISK: ${riskLevel}*

*Platform:* ${visit.platform?.toUpperCase()}
*Caregiver:* ${visit.caregiver_name} (${visit.caregiver_phone})
*Client:* ${visit.client_name}
*Visit Time:* ${visit.visit_time}
*Reason:* ${visit.risk_reason || 'Didn\\'t answer confirmation call'}

*ACTION REQUIRED:* Find backup caregiver NOW to prevent no-show.

_Copper AI Monitoring_`;

  // Send to both Telegram and SMS
  await sendTelegramAlert(message);
  
  if (visit.agency_owner_phone) {
    const smsMessage = message.replace(/\*/g, '').replace(/_/g, '');
    await sendSMSAlert(visit.agency_owner_phone, smsMessage);
  }
}

/**
 * Send platform error alert
 */
async function sendPlatformErrorAlert(platform, error) {
  const message = `⚠️ *PLATFORM ERROR: ${platform.toUpperCase()}*

*Error:* ${error.message}
*Time:* ${new Date().toISOString()}

Check server logs for details.

_Copper AI System Alert_`;

  await sendTelegramAlert(message);
}

module.exports = {
  sendTelegramAlert,
  sendSMSAlert,
  sendNoShowAlert,
  sendPlatformErrorAlert
};

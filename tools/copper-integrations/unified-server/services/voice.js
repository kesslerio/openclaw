/**
 * Voice Service (Shared across all platforms)
 *
 * Handles voice calls via Retell API for:
 * - Voice EVV (clock in/out)
 * - Confirmation calls (no-show prevention)
 * - Schedule notifications
 *
 * Author: Nike 🐾
 */

const axios = require("axios");

const RETELL_API_KEY = process.env.RETELL_API_KEY;
const RETELL_API_URL = "https://api.retellai.com/v2";
const TWILIO_PHONE_NUMBER = process.env.TWILIO_PHONE_NUMBER || "+14697421095";

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
          ...metadata,
        },
      },
      {
        headers: {
          Authorization: `Bearer ${RETELL_API_KEY}`,
          "Content-Type": "application/json",
        },
      },
    );

    console.log(`✅ Call initiated to ${phoneNumber}`);
    return {
      success: true,
      call_id: response.data.call_id,
      status: response.data.call_status,
    };
  } catch (error) {
    console.error(`❌ Failed to call ${phoneNumber}:`, error.response?.data || error.message);
    return {
      success: false,
      error: error.response?.data?.message || error.message,
    };
  }
}

/**
 * Generate confirmation call prompt
 */
function generateConfirmationPrompt(visit) {
  const visitTime = new Date(`${visit.visit_date}T${visit.visit_time}`).toLocaleTimeString(
    "en-US",
    {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    },
  );

  return `Hi ${visit.caregiver_name}, this is Copper AI calling to confirm your upcoming visit.

You have a visit scheduled with ${visit.client_name} today at ${visitTime}.

Can you confirm you'll be there on time?

Please respond with "yes I'll be there" or "no I can't make it" or "I need to reschedule."

This is an automated confirmation call to prevent no-shows. If you confirm, you're all set. If you can't make it, I'll alert the agency so they can find a replacement.

What's your response?`;
}

/**
 * Generate EVV prompt
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
function generateScheduleNotificationPrompt(visit) {
  const visitDate = new Date(visit.visit_date).toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
  const visitTime = new Date(`${visit.visit_date}T${visit.visit_time}`).toLocaleTimeString(
    "en-US",
    {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    },
  );

  return `Hi ${visit.caregiver_name}, this is Copper AI with an important schedule update.

You have a NEW visit assigned:

Client: ${visit.client_name}
Date: ${visitDate}
Time: ${visitTime}
Duration: ${visit.duration_minutes} minutes
Address: ${visit.client_address || "Check your schedule for address"}

Please confirm you received this message by saying "got it" or "I'll be there."

If you have any conflicts or questions, please contact your agency immediately.`;
}

/**
 * Make confirmation call (no-show prevention)
 */
async function makeConfirmationCall(visit) {
  const prompt = generateConfirmationPrompt(visit);
  return makeVoiceCall(visit.caregiver_phone, prompt, {
    visit_id: visit.id,
    confirmation: true,
    platform: visit.platform,
  });
}

/**
 * Make EVV call (alternative to mobile app)
 */
async function makeEVVCall(phoneNumber) {
  const prompt = generateEVVPrompt();
  return makeVoiceCall(phoneNumber, prompt, {
    evv: true,
  });
}

/**
 * Make schedule notification call
 */
async function makeScheduleNotificationCall(visit) {
  const prompt = generateScheduleNotificationPrompt(visit);
  return makeVoiceCall(visit.caregiver_phone, prompt, {
    visit_id: visit.id,
    notification: true,
    platform: visit.platform,
  });
}

module.exports = {
  makeVoiceCall,
  makeConfirmationCall,
  makeEVVCall,
  makeScheduleNotificationCall,
  generateConfirmationPrompt,
  generateEVVPrompt,
  generateScheduleNotificationPrompt,
};

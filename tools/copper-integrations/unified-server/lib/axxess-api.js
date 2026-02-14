#!/usr/bin/env node
/**
 * Axxess API Client
 *
 * OAuth 2.0 authenticated REST API client for Axxess Home Health/Home Care.
 *
 * Author: Nike 🐾
 * Created: Feb 3, 2026
 */

const axios = require("axios");

class AxxessAPI {
  /**
   * Initialize Axxess API client
   * @param {string} clientId - OAuth client ID from Axxess
   * @param {string} clientSecret - OAuth client secret from Axxess
   * @param {string} agencyId - Axxess agency ID
   * @param {string} baseURL - API base URL (default: production)
   */
  constructor(clientId, clientSecret, agencyId, baseURL = "https://api.axxess.com/v1") {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.agencyId = agencyId;
    this.baseURL = baseURL;
    this.accessToken = null;
    this.tokenExpiry = null;
    this.refreshToken = null;
  }

  /**
   * Authenticate with Axxess OAuth 2.0
   */
  async authenticate() {
    try {
      const response = await axios.post(
        `${this.baseURL}/oauth/token`,
        {
          grant_type: "client_credentials",
          client_id: this.clientId,
          client_secret: this.clientSecret,
          scope: "read:schedule write:evv read:caregivers",
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      this.accessToken = response.data.access_token;
      this.tokenExpiry = Date.now() + response.data.expires_in * 1000;
      this.refreshToken = response.data.refresh_token; // For future use

      console.log("✅ Axxess API authenticated successfully");
      return true;
    } catch (error) {
      console.error("❌ Axxess API authentication failed:", error.response?.data || error.message);
      throw new Error(
        `Authentication failed: ${error.response?.data?.error_description || error.message}`,
      );
    }
  }

  /**
   * Ensure we have a valid access token
   */
  async ensureAuthenticated() {
    if (!this.accessToken || Date.now() >= this.tokenExpiry - 60000) {
      // Refresh token 1 minute before expiry
      await this.authenticate();
    }
  }

  /**
   * Make an authenticated API request
   * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
   * @param {string} endpoint - API endpoint (e.g., '/schedule/visits')
   * @param {object} data - Request body (for POST/PUT)
   * @param {object} params - Query parameters
   * @returns {Promise<object>} API response data
   */
  async request(method, endpoint, data = null, params = null) {
    await this.ensureAuthenticated();

    const config = {
      method,
      url: `${this.baseURL}${endpoint}`,
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
        "X-Agency-ID": this.agencyId,
        Accept: "application/json",
      },
    };

    if (data) config.data = data;
    if (params) config.params = params;

    try {
      const response = await axios(config);
      return response.data;
    } catch (error) {
      // Handle token expiration
      if (error.response?.status === 401) {
        console.log("🔄 Access token expired, re-authenticating...");
        await this.authenticate();
        // Retry the request once
        return this.request(method, endpoint, data, params);
      }

      // Handle rate limiting
      if (error.response?.status === 429) {
        const retryAfter = parseInt(error.response.headers["retry-after"] || "60", 10);
        console.warn(`⏸️  Rate limited, retrying after ${retryAfter} seconds...`);
        await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
        return this.request(method, endpoint, data, params);
      }

      // Log and re-throw other errors
      console.error(
        `❌ Axxess API error (${method} ${endpoint}):`,
        error.response?.data || error.message,
      );
      throw error;
    }
  }

  // ============================================================================
  // SCHEDULE API
  // ============================================================================

  /**
   * Get visits for a date range
   * @param {string} startDate - Start date (YYYY-MM-DD)
   * @param {string} endDate - End date (YYYY-MM-DD)
   * @param {string} status - Filter by status (scheduled, in_progress, completed, cancelled)
   * @returns {Promise<Array>} List of visits
   */
  async getSchedule(startDate, endDate, status = null) {
    const params = {
      start_date: startDate,
      end_date: endDate,
    };
    if (status) params.status = status;

    const response = await this.request("GET", "/schedule/visits", null, params);
    return response.visits || [];
  }

  /**
   * Get today's visits
   * @returns {Promise<Array>} List of today's visits
   */
  async getTodaySchedule() {
    const today = new Date().toISOString().split("T")[0];
    return this.getSchedule(today, today);
  }

  /**
   * Get a specific visit by ID
   * @param {string} visitId - Axxess visit ID
   * @returns {Promise<object>} Visit details
   */
  async getVisit(visitId) {
    return this.request("GET", `/schedule/visits/${visitId}`);
  }

  /**
   * Get visits for a specific caregiver
   * @param {string} caregiverId - Axxess caregiver ID
   * @param {string} startDate - Start date (YYYY-MM-DD)
   * @param {string} endDate - End date (YYYY-MM-DD)
   * @returns {Promise<Array>} Caregiver's visits
   */
  async getCaregiverSchedule(caregiverId, startDate, endDate) {
    const params = {
      caregiver_id: caregiverId,
      start_date: startDate,
      end_date: endDate,
    };
    const response = await this.request("GET", "/schedule/visits", null, params);
    return response.visits || [];
  }

  // ============================================================================
  // EVV API
  // ============================================================================

  /**
   * Submit clock-in EVV data
   * @param {string} visitId - Axxess visit ID
   * @param {string} caregiverId - Axxess caregiver ID
   * @param {string} timestamp - ISO 8601 timestamp
   * @param {object} location - {lat, lon} GPS coordinates
   * @returns {Promise<object>} API response
   */
  async submitClockIn(visitId, caregiverId, timestamp, location = null) {
    const data = {
      caregiver_id: caregiverId,
      timestamp,
      event_type: "clock_in",
    };

    if (location) {
      data.latitude = location.lat;
      data.longitude = location.lon;
    }

    return this.request("POST", `/evv/visits/${visitId}/clock-in`, data);
  }

  /**
   * Submit clock-out EVV data
   * @param {string} visitId - Axxess visit ID
   * @param {string} caregiverId - Axxess caregiver ID
   * @param {string} timestamp - ISO 8601 timestamp
   * @param {object} location - {lat, lon} GPS coordinates
   * @returns {Promise<object>} API response
   */
  async submitClockOut(visitId, caregiverId, timestamp, location = null) {
    const data = {
      caregiver_id: caregiverId,
      timestamp,
      event_type: "clock_out",
    };

    if (location) {
      data.latitude = location.lat;
      data.longitude = location.lon;
    }

    return this.request("POST", `/evv/visits/${visitId}/clock-out`, data);
  }

  /**
   * Get EVV logs for a visit
   * @param {string} visitId - Axxess visit ID
   * @returns {Promise<Array>} EVV event logs
   */
  async getEVVLogs(visitId) {
    const response = await this.request("GET", `/evv/visits/${visitId}/logs`);
    return response.logs || [];
  }

  // ============================================================================
  // CAREGIVER API
  // ============================================================================

  /**
   * Get all caregivers for the agency
   * @param {string} status - Filter by status (active, inactive)
   * @returns {Promise<Array>} List of caregivers
   */
  async getCaregivers(status = "active") {
    const params = status ? { status } : {};
    const response = await this.request("GET", "/caregivers", null, params);
    return response.caregivers || [];
  }

  /**
   * Get a specific caregiver by ID
   * @param {string} caregiverId - Axxess caregiver ID
   * @returns {Promise<object>} Caregiver details
   */
  async getCaregiver(caregiverId) {
    return this.request("GET", `/caregivers/${caregiverId}`);
  }

  /**
   * Search caregivers by name or phone
   * @param {string} query - Search query
   * @returns {Promise<Array>} Matching caregivers
   */
  async searchCaregivers(query) {
    const params = { q: query };
    const response = await this.request("GET", "/caregivers/search", null, params);
    return response.caregivers || [];
  }

  // ============================================================================
  // CLIENT API
  // ============================================================================

  /**
   * Get all clients for the agency
   * @param {string} status - Filter by status (active, inactive, discharged)
   * @returns {Promise<Array>} List of clients
   */
  async getClients(status = "active") {
    const params = status ? { status } : {};
    const response = await this.request("GET", "/clients", null, params);
    return response.clients || [];
  }

  /**
   * Get a specific client by ID
   * @param {string} clientId - Axxess client ID
   * @returns {Promise<object>} Client details
   */
  async getClient(clientId) {
    return this.request("GET", `/clients/${clientId}`);
  }

  // ============================================================================
  // MISSED VISIT ALERTS API
  // ============================================================================

  /**
   * Get missed visit alerts
   * @param {string} date - Date to check (YYYY-MM-DD)
   * @returns {Promise<Array>} List of missed visits
   */
  async getMissedVisits(date) {
    const params = { date };
    const response = await this.request("GET", "/alerts/missed-visits", null, params);
    return response.alerts || [];
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  /**
   * Test API connection
   * @returns {Promise<boolean>} True if connection successful
   */
  async testConnection() {
    try {
      await this.authenticate();
      const caregivers = await this.getCaregivers();
      console.log(`✅ Connection successful. Found ${caregivers.length} active caregivers.`);
      return true;
    } catch (error) {
      console.error("❌ Connection test failed:", error.message);
      return false;
    }
  }

  /**
   * Get API usage stats (calls remaining, reset time)
   * @returns {Promise<object>} Usage stats
   */
  async getUsageStats() {
    // Axxess returns rate limit info in headers
    // This is a placeholder - actual implementation depends on Axxess API
    try {
      const response = await this.request("GET", "/usage");
      return response;
    } catch (error) {
      return {
        calls_remaining: "unknown",
        reset_time: "unknown",
      };
    }
  }
}

// ============================================================================
// EXAMPLE USAGE
// ============================================================================

if (require.main === module) {
  // Command-line test
  const clientId = process.env.AXXESS_CLIENT_ID;
  const clientSecret = process.env.AXXESS_CLIENT_SECRET;
  const agencyId = process.env.AXXESS_AGENCY_ID || "AG-TEST";

  if (!clientId || !clientSecret) {
    console.error("❌ Missing environment variables: AXXESS_CLIENT_ID, AXXESS_CLIENT_SECRET");
    process.exit(1);
  }

  const axxess = new AxxessAPI(clientId, clientSecret, agencyId);

  (async () => {
    try {
      // Test connection
      console.log("🧪 Testing Axxess API connection...\n");
      await axxess.testConnection();

      // Get today's schedule
      console.log("\n📅 Fetching today's schedule...");
      const visits = await axxess.getTodaySchedule();
      console.log(`Found ${visits.length} visits today`);
      if (visits.length > 0) {
        console.log("First visit:", visits[0]);
      }

      // Get caregivers
      console.log("\n👥 Fetching caregivers...");
      const caregivers = await axxess.getCaregivers();
      console.log(`Found ${caregivers.length} active caregivers`);
      if (caregivers.length > 0) {
        console.log("First caregiver:", caregivers[0]);
      }

      console.log("\n✅ All tests passed!");
    } catch (error) {
      console.error("\n❌ Test failed:", error.message);
      process.exit(1);
    }
  })();
}

module.exports = AxxessAPI;

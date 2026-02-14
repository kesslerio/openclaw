-- Axxess Integration Database Migrations
-- Adds Axxess-specific columns to existing ClearCare schema
-- Author: Nike 🐾
-- Created: Feb 3, 2026

-- ============================================================================
-- MIGRATION 1: Add Axxess IDs to existing tables
-- ============================================================================

-- Add Axxess columns to agencies table
ALTER TABLE agencies 
ADD COLUMN IF NOT EXISTS axxess_agency_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS axxess_client_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS axxess_client_secret VARCHAR(200),
ADD COLUMN IF NOT EXISTS axxess_api_url VARCHAR(200) DEFAULT 'https://api.axxess.com/v1',
ADD COLUMN IF NOT EXISTS axxess_access_token TEXT,
ADD COLUMN IF NOT EXISTS axxess_token_expiry TIMESTAMP,
ADD COLUMN IF NOT EXISTS platform VARCHAR(20) DEFAULT 'clearcare'; -- 'clearcare' or 'axxess' or 'both'

CREATE INDEX IF NOT EXISTS idx_agencies_axxess_id ON agencies(axxess_agency_id);
CREATE INDEX IF NOT EXISTS idx_agencies_platform ON agencies(platform);

-- Add Axxess columns to caregivers table
ALTER TABLE caregivers
ADD COLUMN IF NOT EXISTS axxess_caregiver_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS axxess_employee_number VARCHAR(50);

CREATE INDEX IF NOT EXISTS idx_caregivers_axxess_id ON caregivers(axxess_caregiver_id);

-- Add Axxess columns to visits table
ALTER TABLE visits
ADD COLUMN IF NOT EXISTS axxess_visit_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS axxess_client_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS synced_from VARCHAR(20) DEFAULT 'manual'; -- 'clearcare', 'axxess', 'manual'

CREATE INDEX IF NOT EXISTS idx_visits_axxess_id ON visits(axxess_visit_id);
CREATE INDEX IF NOT EXISTS idx_visits_synced_from ON visits(synced_from);

-- ============================================================================
-- MIGRATION 2: Create Axxess-specific tables
-- ============================================================================

-- API sync log (track when we last synced from Axxess)
CREATE TABLE IF NOT EXISTS axxess_sync_log (
  id SERIAL PRIMARY KEY,
  agency_id INT REFERENCES agencies(id) ON DELETE CASCADE,
  sync_type VARCHAR(50) NOT NULL, -- 'schedule', 'caregivers', 'clients', 'evv'
  sync_status VARCHAR(20) NOT NULL, -- 'success', 'failed', 'partial'
  records_synced INT DEFAULT 0,
  error_message TEXT,
  synced_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sync_log_agency ON axxess_sync_log(agency_id);
CREATE INDEX idx_sync_log_type ON axxess_sync_log(sync_type);
CREATE INDEX idx_sync_log_time ON axxess_sync_log(synced_at);

-- API rate limit tracking
CREATE TABLE IF NOT EXISTS axxess_rate_limits (
  id SERIAL PRIMARY KEY,
  agency_id INT REFERENCES agencies(id) ON DELETE CASCADE,
  calls_made INT DEFAULT 0,
  calls_remaining INT DEFAULT 1000,
  reset_time TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_rate_limits_agency ON axxess_rate_limits(agency_id);

-- ============================================================================
-- MIGRATION 3: Update analytics views for multi-platform support
-- ============================================================================

-- Drop and recreate daily_no_show_rates with platform filter
DROP VIEW IF EXISTS daily_no_show_rates;
CREATE VIEW daily_no_show_rates AS
SELECT 
  a.id as agency_id,
  a.name as agency_name,
  a.platform,
  v.visit_date,
  v.synced_from,
  COUNT(*) as total_visits,
  SUM(CASE WHEN v.status = 'no_show' THEN 1 ELSE 0 END) as no_shows,
  ROUND(100.0 * SUM(CASE WHEN v.status = 'no_show' THEN 1 ELSE 0 END) / COUNT(*), 2) as no_show_rate_percent,
  SUM(CASE WHEN v.status = 'completed' THEN 1 ELSE 0 END) as completed_visits,
  SUM(CASE WHEN v.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_visits
FROM visits v
JOIN caregivers c ON v.caregiver_id = c.id
JOIN agencies a ON c.agency_id = a.id
WHERE v.visit_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY a.id, a.name, a.platform, v.visit_date, v.synced_from
ORDER BY v.visit_date DESC, a.name;

-- Platform comparison view (ClearCare vs Axxess performance)
CREATE OR REPLACE VIEW platform_comparison AS
SELECT 
  a.platform,
  COUNT(DISTINCT a.id) as total_agencies,
  COUNT(DISTINCT c.id) as total_caregivers,
  COUNT(*) as total_visits,
  SUM(CASE WHEN v.status = 'no_show' THEN 1 ELSE 0 END) as total_no_shows,
  ROUND(100.0 * SUM(CASE WHEN v.status = 'no_show' THEN 1 ELSE 0 END) / COUNT(*), 2) as avg_no_show_rate,
  SUM(CASE WHEN v.status = 'completed' THEN 1 ELSE 0 END) as total_completed,
  ROUND(100.0 * SUM(CASE WHEN v.status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_rate,
  COUNT(DISTINCT DATE(evv.timestamp)) as days_active
FROM agencies a
LEFT JOIN caregivers c ON a.id = c.agency_id
LEFT JOIN visits v ON c.id = v.caregiver_id AND v.visit_date >= CURRENT_DATE - INTERVAL '30 days'
LEFT JOIN evv_logs evv ON v.id = evv.visit_id
GROUP BY a.platform
ORDER BY total_agencies DESC;

-- ============================================================================
-- MIGRATION 4: Helper functions for Axxess
-- ============================================================================

/**
 * Function: Get last successful sync time for an agency
 */
CREATE OR REPLACE FUNCTION get_last_sync_time(agency_id_param INT, sync_type_param VARCHAR)
RETURNS TIMESTAMP AS $$
DECLARE
  last_sync TIMESTAMP;
BEGIN
  SELECT synced_at INTO last_sync
  FROM axxess_sync_log
  WHERE agency_id = agency_id_param
    AND sync_type = sync_type_param
    AND sync_status = 'success'
  ORDER BY synced_at DESC
  LIMIT 1;

  RETURN last_sync;
END;
$$ LANGUAGE plpgsql;

/**
 * Function: Record API call (for rate limiting)
 */
CREATE OR REPLACE FUNCTION record_api_call(agency_id_param INT, calls_count INT DEFAULT 1)
RETURNS VOID AS $$
BEGIN
  INSERT INTO axxess_rate_limits (agency_id, calls_made, calls_remaining, reset_time, updated_at)
  VALUES (agency_id_param, calls_count, 1000 - calls_count, NOW() + INTERVAL '24 hours', NOW())
  ON CONFLICT (agency_id) 
  DO UPDATE SET 
    calls_made = axxess_rate_limits.calls_made + calls_count,
    calls_remaining = GREATEST(0, axxess_rate_limits.calls_remaining - calls_count),
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

/**
 * Function: Reset rate limits (run daily via cron)
 */
CREATE OR REPLACE FUNCTION reset_rate_limits()
RETURNS VOID AS $$
BEGIN
  UPDATE axxess_rate_limits
  SET 
    calls_made = 0,
    calls_remaining = 1000,
    reset_time = NOW() + INTERVAL '24 hours',
    updated_at = NOW()
  WHERE reset_time <= NOW();
  
  -- Log the reset
  RAISE NOTICE 'Rate limits reset for % agencies', (SELECT COUNT(*) FROM axxess_rate_limits WHERE reset_time <= NOW());
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MIGRATION 5: Sample Axxess agency data
-- ============================================================================

-- Insert test Axxess agency (comment out in production)
INSERT INTO agencies (name, owner_name, owner_phone, owner_email, plan, monthly_price, platform, axxess_agency_id)
VALUES ('XYZ Home Health (Axxess)', 'Jane Doe', '+14695555678', 'jane@xyzhomehealth.com', 'beta', 0.00, 'axxess', 'AG-AXXESS-TEST')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- MIGRATION 6: Data consistency checks
-- ============================================================================

-- Find visits synced from both platforms (shouldn't happen)
CREATE OR REPLACE VIEW duplicate_visits AS
SELECT 
  v.id,
  v.caregiver_id,
  v.client_name,
  v.visit_date,
  v.visit_time,
  v.clearcare_visit_id,
  v.axxess_visit_id,
  v.synced_from
FROM visits v
WHERE v.clearcare_visit_id IS NOT NULL 
  AND v.axxess_visit_id IS NOT NULL;

-- Find caregivers registered on both platforms
CREATE OR REPLACE VIEW caregivers_on_both_platforms AS
SELECT 
  c.id,
  c.name,
  c.phone,
  c.clearcare_caregiver_id,
  c.axxess_caregiver_id,
  a.platform
FROM caregivers c
JOIN agencies a ON c.agency_id = a.id
WHERE c.clearcare_caregiver_id IS NOT NULL 
  AND c.axxess_caregiver_id IS NOT NULL;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================

-- Uncomment to rollback migrations:

-- ALTER TABLE agencies DROP COLUMN IF EXISTS axxess_agency_id;
-- ALTER TABLE agencies DROP COLUMN IF EXISTS axxess_client_id;
-- ALTER TABLE agencies DROP COLUMN IF EXISTS axxess_client_secret;
-- ALTER TABLE agencies DROP COLUMN IF EXISTS axxess_api_url;
-- ALTER TABLE agencies DROP COLUMN IF EXISTS axxess_access_token;
-- ALTER TABLE agencies DROP COLUMN IF EXISTS axxess_token_expiry;
-- ALTER TABLE agencies DROP COLUMN IF EXISTS platform;

-- ALTER TABLE caregivers DROP COLUMN IF EXISTS axxess_caregiver_id;
-- ALTER TABLE caregivers DROP COLUMN IF EXISTS axxess_employee_number;

-- ALTER TABLE visits DROP COLUMN IF EXISTS axxess_visit_id;
-- ALTER TABLE visits DROP COLUMN IF EXISTS axxess_client_id;
-- ALTER TABLE visits DROP COLUMN IF EXISTS synced_from;

-- DROP TABLE IF EXISTS axxess_sync_log;
-- DROP TABLE IF EXISTS axxess_rate_limits;
-- DROP VIEW IF EXISTS platform_comparison;
-- DROP VIEW IF EXISTS duplicate_visits;
-- DROP VIEW IF EXISTS caregivers_on_both_platforms;
-- DROP FUNCTION IF EXISTS get_last_sync_time(INT, VARCHAR);
-- DROP FUNCTION IF EXISTS record_api_call(INT, INT);
-- DROP FUNCTION IF EXISTS reset_rate_limits();

-- ============================================================================
-- POST-MIGRATION CHECKS
-- ============================================================================

-- Verify migrations
-- SELECT COUNT(*) FROM agencies WHERE platform = 'axxess';
-- SELECT COUNT(*) FROM axxess_sync_log;
-- SELECT * FROM axxess_rate_limits;
-- SELECT * FROM platform_comparison;

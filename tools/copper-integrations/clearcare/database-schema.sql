-- Copper AI ClearCare Integration Database Schema
-- Author: Nike 🐾
-- Created: Feb 3, 2026

-- ============================================================================
-- AGENCIES TABLE
-- ============================================================================

CREATE TABLE agencies (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  owner_name VARCHAR(100),
  owner_phone VARCHAR(20),
  owner_email VARCHAR(100),
  clearcare_account_id VARCHAR(50),
  plan VARCHAR(20) DEFAULT 'beta', -- beta, basic, pro
  status VARCHAR(20) DEFAULT 'active', -- active, paused, churned
  monthly_price DECIMAL(10, 2) DEFAULT 0.00,
  trial_end_date DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agencies_status ON agencies(status);
CREATE INDEX idx_agencies_clearcare_id ON agencies(clearcare_account_id);

-- ============================================================================
-- CAREGIVERS TABLE
-- ============================================================================

CREATE TABLE caregivers (
  id SERIAL PRIMARY KEY,
  phone VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  agency_id INT REFERENCES agencies(id) ON DELETE CASCADE,
  language VARCHAR(10) DEFAULT 'en', -- en, es, etc.
  email VARCHAR(100),
  status VARCHAR(20) DEFAULT 'active', -- active, inactive
  clearcare_caregiver_id VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_caregivers_phone ON caregivers(phone);
CREATE INDEX idx_caregivers_agency ON caregivers(agency_id);
CREATE INDEX idx_caregivers_status ON caregivers(status);

-- ============================================================================
-- VISITS TABLE
-- ============================================================================

CREATE TABLE visits (
  id SERIAL PRIMARY KEY,
  caregiver_id INT REFERENCES caregivers(id) ON DELETE CASCADE,
  client_name VARCHAR(100) NOT NULL,
  client_address VARCHAR(200),
  visit_date DATE NOT NULL,
  visit_time TIME NOT NULL,
  duration_minutes INT NOT NULL,
  status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, confirmed, in_progress, completed, no_show, cancelled
  clearcare_visit_id VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_visits_caregiver ON visits(caregiver_id);
CREATE INDEX idx_visits_date ON visits(visit_date);
CREATE INDEX idx_visits_status ON visits(status);
CREATE INDEX idx_visits_datetime ON visits(visit_date, visit_time);
CREATE INDEX idx_visits_clearcare_id ON visits(clearcare_visit_id);

-- ============================================================================
-- EVV LOGS TABLE
-- ============================================================================

CREATE TABLE evv_logs (
  id SERIAL PRIMARY KEY,
  visit_id INT REFERENCES visits(id) ON DELETE CASCADE,
  event_type VARCHAR(20) NOT NULL, -- clock_in, clock_out
  timestamp TIMESTAMP NOT NULL,
  phone_number VARCHAR(20),
  location_lat DECIMAL(10, 8),
  location_lon DECIMAL(11, 8),
  call_duration_seconds INT,
  transcript TEXT,
  call_id VARCHAR(50), -- Retell call ID
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_evv_visit ON evv_logs(visit_id);
CREATE INDEX idx_evv_timestamp ON evv_logs(timestamp);
CREATE INDEX idx_evv_event_type ON evv_logs(event_type);

-- ============================================================================
-- CONFIRMATION CALLS TABLE
-- ============================================================================

CREATE TABLE confirmation_calls (
  id SERIAL PRIMARY KEY,
  visit_id INT REFERENCES visits(id) ON DELETE CASCADE,
  call_time TIMESTAMP NOT NULL,
  answered BOOLEAN,
  confirmed BOOLEAN,
  transcript TEXT,
  risk_level VARCHAR(20), -- LOW, MEDIUM, HIGH, CRITICAL
  call_duration_seconds INT,
  call_id VARCHAR(50), -- Retell call ID
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_confirmation_visit ON confirmation_calls(visit_id);
CREATE INDEX idx_confirmation_risk ON confirmation_calls(risk_level);
CREATE INDEX idx_confirmation_time ON confirmation_calls(call_time);

-- ============================================================================
-- ANALYTICS VIEW: Daily No-Show Rates
-- ============================================================================

CREATE VIEW daily_no_show_rates AS
SELECT 
  a.id as agency_id,
  a.name as agency_name,
  v.visit_date,
  COUNT(*) as total_visits,
  SUM(CASE WHEN v.status = 'no_show' THEN 1 ELSE 0 END) as no_shows,
  ROUND(100.0 * SUM(CASE WHEN v.status = 'no_show' THEN 1 ELSE 0 END) / COUNT(*), 2) as no_show_rate_percent,
  SUM(CASE WHEN v.status = 'completed' THEN 1 ELSE 0 END) as completed_visits,
  SUM(CASE WHEN v.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_visits
FROM visits v
JOIN caregivers c ON v.caregiver_id = c.id
JOIN agencies a ON c.agency_id = a.id
WHERE v.visit_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY a.id, a.name, v.visit_date
ORDER BY v.visit_date DESC, a.name;

-- ============================================================================
-- ANALYTICS VIEW: EVV Compliance Rates
-- ============================================================================

CREATE VIEW evv_compliance AS
SELECT 
  a.id as agency_id,
  a.name as agency_name,
  v.visit_date,
  COUNT(*) as total_visits,
  SUM(CASE WHEN EXISTS (
    SELECT 1 FROM evv_logs e 
    WHERE e.visit_id = v.id AND e.event_type = 'clock_in'
  ) AND EXISTS (
    SELECT 1 FROM evv_logs e 
    WHERE e.visit_id = v.id AND e.event_type = 'clock_out'
  ) THEN 1 ELSE 0 END) as compliant_visits,
  ROUND(100.0 * SUM(CASE WHEN EXISTS (
    SELECT 1 FROM evv_logs e 
    WHERE e.visit_id = v.id AND e.event_type = 'clock_in'
  ) AND EXISTS (
    SELECT 1 FROM evv_logs e 
    WHERE e.visit_id = v.id AND e.event_type = 'clock_out'
  ) THEN 1 ELSE 0 END) / COUNT(*), 2) as compliance_rate_percent
FROM visits v
JOIN caregivers c ON v.caregiver_id = c.id
JOIN agencies a ON c.agency_id = a.id
WHERE v.visit_date >= CURRENT_DATE - INTERVAL '30 days'
AND v.status IN ('completed', 'in_progress')
GROUP BY a.id, a.name, v.visit_date
ORDER BY v.visit_date DESC, a.name;

-- ============================================================================
-- ANALYTICS VIEW: Confirmation Call Effectiveness
-- ============================================================================

CREATE VIEW confirmation_effectiveness AS
SELECT 
  a.id as agency_id,
  a.name as agency_name,
  DATE(cc.call_time) as call_date,
  COUNT(*) as total_confirmation_calls,
  SUM(CASE WHEN cc.answered THEN 1 ELSE 0 END) as answered_calls,
  SUM(CASE WHEN cc.confirmed THEN 1 ELSE 0 END) as confirmed_calls,
  SUM(CASE WHEN cc.risk_level = 'HIGH' OR cc.risk_level = 'CRITICAL' THEN 1 ELSE 0 END) as high_risk_visits,
  ROUND(100.0 * SUM(CASE WHEN cc.answered THEN 1 ELSE 0 END) / COUNT(*), 2) as answer_rate_percent,
  ROUND(100.0 * SUM(CASE WHEN cc.confirmed THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN cc.answered THEN 1 ELSE 0 END), 0), 2) as confirmation_rate_percent
FROM confirmation_calls cc
JOIN visits v ON cc.visit_id = v.id
JOIN caregivers c ON v.caregiver_id = c.id
JOIN agencies a ON c.agency_id = a.id
WHERE cc.call_time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY a.id, a.name, DATE(cc.call_time)
ORDER BY call_date DESC, a.name;

-- ============================================================================
-- ANALYTICS VIEW: ROI Calculation
-- ============================================================================

CREATE VIEW agency_roi AS
WITH baseline AS (
  -- Assume 20% no-show rate before Copper AI
  SELECT 
    a.id as agency_id,
    COUNT(*) as total_visits,
    COUNT(*) * 0.20 as baseline_no_shows
  FROM visits v
  JOIN caregivers c ON v.caregiver_id = c.id
  JOIN agencies a ON c.agency_id = a.id
  WHERE v.visit_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY a.id
),
actual AS (
  SELECT 
    a.id as agency_id,
    SUM(CASE WHEN v.status = 'no_show' THEN 1 ELSE 0 END) as actual_no_shows
  FROM visits v
  JOIN caregivers c ON v.caregiver_id = c.id
  JOIN agencies a ON c.agency_id = a.id
  WHERE v.visit_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY a.id
)
SELECT 
  a.id as agency_id,
  a.name as agency_name,
  a.monthly_price,
  b.total_visits,
  b.baseline_no_shows as expected_no_shows_without_copper,
  ac.actual_no_shows as actual_no_shows_with_copper,
  b.baseline_no_shows - ac.actual_no_shows as no_shows_prevented,
  -- Assume $75 average visit value
  ROUND((b.baseline_no_shows - ac.actual_no_shows) * 75, 2) as monthly_savings,
  ROUND(((b.baseline_no_shows - ac.actual_no_shows) * 75) / NULLIF(a.monthly_price, 0), 2) as roi_ratio
FROM agencies a
JOIN baseline b ON a.id = b.agency_id
LEFT JOIN actual ac ON a.id = ac.agency_id
WHERE a.status = 'active'
ORDER BY roi_ratio DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

/**
 * Function: Calculate caregiver risk score
 * Returns 0-100 risk score based on historical behavior
 */
CREATE OR REPLACE FUNCTION calculate_caregiver_risk_score(caregiver_id_param INT)
RETURNS INT AS $$
DECLARE
  total_visits INT;
  no_shows INT;
  late_cancellations INT;
  unanswered_confirmations INT;
  risk_score INT;
BEGIN
  -- Get historical stats (last 90 days)
  SELECT 
    COUNT(*) INTO total_visits
  FROM visits v
  WHERE v.caregiver_id = caregiver_id_param
  AND v.visit_date >= CURRENT_DATE - INTERVAL '90 days';

  SELECT 
    COUNT(*) INTO no_shows
  FROM visits v
  WHERE v.caregiver_id = caregiver_id_param
  AND v.status = 'no_show'
  AND v.visit_date >= CURRENT_DATE - INTERVAL '90 days';

  SELECT 
    COUNT(*) INTO unanswered_confirmations
  FROM confirmation_calls cc
  JOIN visits v ON cc.visit_id = v.id
  WHERE v.caregiver_id = caregiver_id_param
  AND cc.answered = FALSE
  AND cc.call_time >= CURRENT_DATE - INTERVAL '90 days';

  -- Calculate risk score (0-100)
  risk_score := 0;

  -- No-show rate contributes up to 50 points
  IF total_visits > 0 THEN
    risk_score := risk_score + (no_shows * 50 / GREATEST(total_visits, 1));
  END IF;

  -- Unanswered confirmations contribute up to 30 points
  IF total_visits > 0 THEN
    risk_score := risk_score + (unanswered_confirmations * 30 / GREATEST(total_visits, 1));
  END IF;

  -- Recent no-show adds 20 points
  IF EXISTS (
    SELECT 1 FROM visits v
    WHERE v.caregiver_id = caregiver_id_param
    AND v.status = 'no_show'
    AND v.visit_date >= CURRENT_DATE - INTERVAL '7 days'
  ) THEN
    risk_score := risk_score + 20;
  END IF;

  RETURN LEAST(risk_score, 100);
END;
$$ LANGUAGE plpgsql;

/**
 * Function: Update visit status triggers
 */
CREATE OR REPLACE FUNCTION update_visit_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER visits_update_timestamp
BEFORE UPDATE ON visits
FOR EACH ROW
EXECUTE FUNCTION update_visit_timestamp();

CREATE TRIGGER caregivers_update_timestamp
BEFORE UPDATE ON caregivers
FOR EACH ROW
EXECUTE FUNCTION update_visit_timestamp();

CREATE TRIGGER agencies_update_timestamp
BEFORE UPDATE ON agencies
FOR EACH ROW
EXECUTE FUNCTION update_visit_timestamp();

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert test agency
INSERT INTO agencies (name, owner_name, owner_phone, owner_email, plan, monthly_price)
VALUES ('ABC Home Care', 'John Smith', '+14695551234', 'john@abchomecare.com', 'beta', 0.00);

-- Insert test caregivers
INSERT INTO caregivers (phone, name, agency_id, language)
VALUES 
  ('+14697421001', 'Maria Garcia', 1, 'es'),
  ('+14697421002', 'James Wilson', 1, 'en'),
  ('+14697421003', 'Sarah Johnson', 1, 'en');

-- Insert test visits (today + tomorrow)
INSERT INTO visits (caregiver_id, client_name, client_address, visit_date, visit_time, duration_minutes, status)
VALUES 
  (1, 'Mrs. Anderson', '123 Main St, Dallas, TX', CURRENT_DATE, '10:00:00', 120, 'scheduled'),
  (1, 'Mr. Thompson', '456 Oak Ave, Dallas, TX', CURRENT_DATE, '14:00:00', 60, 'scheduled'),
  (2, 'Mrs. Davis', '789 Elm St, Plano, TX', CURRENT_DATE + INTERVAL '1 day', '09:00:00', 180, 'scheduled'),
  (3, 'Mr. Martinez', '321 Pine Rd, Frisco, TX', CURRENT_DATE + INTERVAL '1 day', '15:00:00', 90, 'scheduled');

-- ============================================================================
-- GRANTS (adjust for your user)
-- ============================================================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO copper_ai_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO copper_ai_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO copper_ai_user;

-- ============================================================================
-- BACKUP QUERIES (useful for ops)
-- ============================================================================

-- Count visits by status (last 30 days)
-- SELECT status, COUNT(*) FROM visits WHERE visit_date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY status;

-- EVV compliance rate (last 7 days)
-- SELECT * FROM evv_compliance WHERE visit_date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY visit_date DESC;

-- High-risk visits needing attention
-- SELECT v.*, c.name as caregiver, calculate_caregiver_risk_score(v.caregiver_id) as risk_score
-- FROM visits v JOIN caregivers c ON v.caregiver_id = c.id
-- WHERE v.status = 'scheduled' AND calculate_caregiver_risk_score(v.caregiver_id) > 50
-- ORDER BY risk_score DESC;

-- Agency ROI summary
-- SELECT * FROM agency_roi ORDER BY roi_ratio DESC;

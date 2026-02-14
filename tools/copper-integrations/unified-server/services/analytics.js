/**
 * Analytics Service (Shared across all platforms)
 *
 * Generates analytics and insights for:
 * - Individual agencies
 * - Platform comparisons (ClearCare vs Axxess)
 * - System-wide metrics
 *
 * Author: Nike 🐾
 */

const { Pool } = require("pg");
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

/**
 * Get agency analytics
 */
async function getAgencyAnalytics(agencyId, days = 30) {
  try {
    // Basic agency info
    const agency = await pool.query("SELECT * FROM agencies WHERE id = $1", [agencyId]);

    if (agency.rows.length === 0) {
      throw new Error("Agency not found");
    }

    const agencyData = agency.rows[0];

    // No-show metrics
    const noShowStats = await pool.query(
      `
      SELECT 
        COUNT(*) as total_visits,
        SUM(CASE WHEN status = 'no_show' THEN 1 ELSE 0 END) as no_shows,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
        ROUND(100.0 * SUM(CASE WHEN status = 'no_show' THEN 1 ELSE 0 END) / COUNT(*), 2) as no_show_rate
      FROM visits v
      JOIN caregivers c ON v.caregiver_id = c.id
      WHERE c.agency_id = $1
      AND v.visit_date >= CURRENT_DATE - INTERVAL '${days} days'
    `,
      [agencyId],
    );

    // EVV compliance
    const evvStats = await pool.query(
      `
      SELECT 
        COUNT(*) as total_visits,
        SUM(CASE WHEN EXISTS (
          SELECT 1 FROM evv_logs e WHERE e.visit_id = v.id AND e.event_type = 'clock_in'
        ) AND EXISTS (
          SELECT 1 FROM evv_logs e WHERE e.visit_id = v.id AND e.event_type = 'clock_out'
        ) THEN 1 ELSE 0 END) as compliant_visits,
        ROUND(100.0 * SUM(CASE WHEN EXISTS (
          SELECT 1 FROM evv_logs e WHERE e.visit_id = v.id AND e.event_type = 'clock_in'
        ) AND EXISTS (
          SELECT 1 FROM evv_logs e WHERE e.visit_id = v.id AND e.event_type = 'clock_out'
        ) THEN 1 ELSE 0 END) / COUNT(*), 2) as compliance_rate
      FROM visits v
      JOIN caregivers c ON v.caregiver_id = c.id
      WHERE c.agency_id = $1
      AND v.visit_date >= CURRENT_DATE - INTERVAL '${days} days'
      AND v.status IN ('completed', 'in_progress')
    `,
      [agencyId],
    );

    // Confirmation call effectiveness
    const confirmationStats = await pool.query(
      `
      SELECT 
        COUNT(*) as total_calls,
        SUM(CASE WHEN answered THEN 1 ELSE 0 END) as answered,
        SUM(CASE WHEN confirmed THEN 1 ELSE 0 END) as confirmed,
        ROUND(100.0 * SUM(CASE WHEN answered THEN 1 ELSE 0 END) / COUNT(*), 2) as answer_rate,
        ROUND(100.0 * SUM(CASE WHEN confirmed THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN answered THEN 1 ELSE 0 END), 0), 2) as confirmation_rate
      FROM confirmation_calls cc
      JOIN visits v ON cc.visit_id = v.id
      JOIN caregivers c ON v.caregiver_id = c.id
      WHERE c.agency_id = $1
      AND cc.call_time >= CURRENT_DATE - INTERVAL '${days} days'
    `,
      [agencyId],
    );

    // ROI calculation (assume $75 avg visit value, 20% baseline no-show rate)
    const roi = await pool.query(
      `
      WITH baseline AS (
        SELECT COUNT(*) * 0.20 as baseline_no_shows
        FROM visits v
        JOIN caregivers c ON v.caregiver_id = c.id
        WHERE c.agency_id = $1
        AND v.visit_date >= CURRENT_DATE - INTERVAL '${days} days'
      ),
      actual AS (
        SELECT COUNT(*) as actual_no_shows
        FROM visits v
        JOIN caregivers c ON v.caregiver_id = c.id
        WHERE c.agency_id = $1
        AND v.status = 'no_show'
        AND v.visit_date >= CURRENT_DATE - INTERVAL '${days} days'
      )
      SELECT 
        baseline.baseline_no_shows,
        actual.actual_no_shows,
        baseline.baseline_no_shows - actual.actual_no_shows as no_shows_prevented,
        ROUND((baseline.baseline_no_shows - actual.actual_no_shows) * 75, 2) as monthly_savings,
        ROUND(((baseline.baseline_no_shows - actual.actual_no_shows) * 75) / NULLIF($2, 0), 2) as roi_ratio
      FROM baseline, actual
    `,
      [agencyId, agencyData.monthly_price],
    );

    return {
      agency: {
        id: agencyData.id,
        name: agencyData.name,
        platform: agencyData.platform,
        plan: agencyData.plan,
        monthly_price: parseFloat(agencyData.monthly_price),
      },
      period_days: days,
      no_show_metrics: {
        total_visits: parseInt(noShowStats.rows[0].total_visits),
        no_shows: parseInt(noShowStats.rows[0].no_shows),
        completed: parseInt(noShowStats.rows[0].completed),
        confirmed: parseInt(noShowStats.rows[0].confirmed),
        no_show_rate: parseFloat(noShowStats.rows[0].no_show_rate || 0),
      },
      evv_metrics: {
        total_visits: parseInt(evvStats.rows[0].total_visits),
        compliant_visits: parseInt(evvStats.rows[0].compliant_visits),
        compliance_rate: parseFloat(evvStats.rows[0].compliance_rate || 0),
      },
      confirmation_calls: {
        total_calls: parseInt(confirmationStats.rows[0].total_calls || 0),
        answered: parseInt(confirmationStats.rows[0].answered || 0),
        confirmed: parseInt(confirmationStats.rows[0].confirmed || 0),
        answer_rate: parseFloat(confirmationStats.rows[0].answer_rate || 0),
        confirmation_rate: parseFloat(confirmationStats.rows[0].confirmation_rate || 0),
      },
      roi: {
        baseline_no_shows: parseFloat(roi.rows[0]?.baseline_no_shows || 0),
        actual_no_shows: parseInt(roi.rows[0]?.actual_no_shows || 0),
        no_shows_prevented: parseFloat(roi.rows[0]?.no_shows_prevented || 0),
        monthly_savings: parseFloat(roi.rows[0]?.monthly_savings || 0),
        roi_ratio: parseFloat(roi.rows[0]?.roi_ratio || 0),
      },
    };
  } catch (error) {
    console.error("❌ Analytics error:", error);
    throw error;
  }
}

/**
 * Get platform comparison (ClearCare vs Axxess)
 */
async function getPlatformComparison(days = 30) {
  try {
    const comparison = await pool.query(`
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
      LEFT JOIN visits v ON c.id = v.caregiver_id 
        AND v.visit_date >= CURRENT_DATE - INTERVAL '${days} days'
      LEFT JOIN evv_logs evv ON v.id = evv.visit_id
      WHERE a.status = 'active'
      GROUP BY a.platform
      ORDER BY total_agencies DESC
    `);

    return {
      period_days: days,
      platforms: comparison.rows.map((row) => ({
        platform: row.platform,
        agencies: parseInt(row.total_agencies),
        caregivers: parseInt(row.total_caregivers),
        visits: parseInt(row.total_visits),
        no_shows: parseInt(row.total_no_shows),
        no_show_rate: parseFloat(row.avg_no_show_rate || 0),
        completed: parseInt(row.total_completed),
        completion_rate: parseFloat(row.completion_rate || 0),
        days_active: parseInt(row.days_active || 0),
      })),
    };
  } catch (error) {
    console.error("❌ Platform comparison error:", error);
    throw error;
  }
}

/**
 * Get system-wide metrics
 */
async function getSystemMetrics() {
  try {
    const metrics = await pool.query(`
      SELECT 
        (SELECT COUNT(*) FROM agencies WHERE status = 'active') as active_agencies,
        (SELECT COUNT(*) FROM caregivers WHERE status = 'active') as active_caregivers,
        (SELECT COUNT(*) FROM visits WHERE visit_date = CURRENT_DATE) as visits_today,
        (SELECT COUNT(*) FROM evv_logs WHERE DATE(timestamp) = CURRENT_DATE) as evv_calls_today,
        (SELECT COUNT(*) FROM confirmation_calls WHERE DATE(call_time) = CURRENT_DATE) as confirmation_calls_today
    `);

    return {
      timestamp: new Date().toISOString(),
      active_agencies: parseInt(metrics.rows[0].active_agencies),
      active_caregivers: parseInt(metrics.rows[0].active_caregivers),
      visits_today: parseInt(metrics.rows[0].visits_today),
      evv_calls_today: parseInt(metrics.rows[0].evv_calls_today),
      confirmation_calls_today: parseInt(metrics.rows[0].confirmation_calls_today),
    };
  } catch (error) {
    console.error("❌ System metrics error:", error);
    throw error;
  }
}

module.exports = {
  getAgencyAnalytics,
  getPlatformComparison,
  getSystemMetrics,
};

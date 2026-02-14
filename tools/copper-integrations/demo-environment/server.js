#!/usr/bin/env node

/**
 * Copper AI Demo Server
 *
 * Runs demo environment on localhost:3001
 * - Serves demo dashboard
 * - Simulates voice calls
 * - Generates real-time demo data
 * - No external dependencies (all mocked)
 */

const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = process.env.DEMO_PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static("public"));

// Load demo data
let demoData = {};
const dataPath = path.join(__dirname, "demo-data.json");

if (fs.existsSync(dataPath)) {
  demoData = JSON.parse(fs.readFileSync(dataPath, "utf-8"));
  console.log("✅ Loaded demo data:", demoData.stats);
} else {
  console.log("⚠️  No demo data found. Run: node demo-data-generator.js");
}

// --- API ENDPOINTS ---

/**
 * GET /api/agencies
 * List all demo agencies
 */
app.get("/api/agencies", (req, res) => {
  res.json({
    ok: true,
    agencies: demoData.agencies || [],
    count: demoData.agencies?.length || 0,
  });
});

/**
 * GET /api/agencies/:id
 * Get agency details
 */
app.get("/api/agencies/:id", (req, res) => {
  const agency = demoData.agencies?.find((a) => a.id === req.params.id);

  if (!agency) {
    return res.status(404).json({ ok: false, error: "Agency not found" });
  }

  // Calculate current metrics
  const caregivers = demoData.caregivers?.filter((c) => c.agencyId === agency.id) || [];
  const scheduledVisits = demoData.scheduledVisits?.filter((v) => v.agencyId === agency.id) || [];
  const historicalVisits = demoData.historicalVisits?.filter((v) => v.agencyId === agency.id) || [];

  const noshows = historicalVisits.filter((v) => v.status === "no-show").length;
  const totalCompleted = historicalVisits.filter((v) => v.status === "completed").length;
  const currentNoshowRate = totalCompleted > 0 ? noshows / (noshows + totalCompleted) : 0;

  res.json({
    ok: true,
    agency: {
      ...agency,
      caregivers: caregivers.length,
      scheduledVisits: scheduledVisits.length,
      completedVisits: totalCompleted,
      noshows,
      currentNoshowRate: parseFloat((currentNoshowRate * 100).toFixed(1)),
      improvement: parseFloat(((agency.noshowRateBefore - currentNoshowRate) * 100).toFixed(1)),
    },
  });
});

/**
 * GET /api/caregivers
 * List caregivers (optionally filter by agency)
 */
app.get("/api/caregivers", (req, res) => {
  let caregivers = demoData.caregivers || [];

  if (req.query.agencyId) {
    caregivers = caregivers.filter((c) => c.agencyId === req.query.agencyId);
  }

  if (req.query.active === "true") {
    caregivers = caregivers.filter((c) => c.active);
  }

  res.json({
    ok: true,
    caregivers,
    count: caregivers.length,
  });
});

/**
 * GET /api/visits/scheduled
 * Get scheduled visits (next 7 days)
 */
app.get("/api/visits/scheduled", (req, res) => {
  let visits = demoData.scheduledVisits || [];

  if (req.query.agencyId) {
    visits = visits.filter((v) => v.agencyId === req.query.agencyId);
  }

  if (req.query.riskLevel) {
    visits = visits.filter((v) => v.riskLevel === req.query.riskLevel);
  }

  // Enrich with caregiver + patient details
  visits = visits.map((visit) => {
    const caregiver = demoData.caregivers?.find((c) => c.id === visit.caregiverId);
    const patient = demoData.patients?.find((p) => p.id === visit.patientId);

    return {
      ...visit,
      caregiver: caregiver
        ? {
            name: `${caregiver.firstName} ${caregiver.lastName}`,
            phone: caregiver.phone,
            reliability: caregiver.reliability,
            noshowRate: caregiver.noshowRate,
          }
        : null,
      patient: patient
        ? {
            name: `${patient.firstName} ${patient.lastName}`,
            address: patient.address,
            careType: patient.careType,
          }
        : null,
    };
  });

  res.json({
    ok: true,
    visits,
    count: visits.length,
    riskBreakdown: {
      LOW: visits.filter((v) => v.riskLevel === "LOW").length,
      MODERATE: visits.filter((v) => v.riskLevel === "MODERATE").length,
      HIGH: visits.filter((v) => v.riskLevel === "HIGH").length,
      CRITICAL: visits.filter((v) => v.riskLevel === "CRITICAL").length,
    },
  });
});

/**
 * GET /api/visits/:id
 * Get visit details with risk analysis
 */
app.get("/api/visits/:id", (req, res) => {
  const visit = demoData.scheduledVisits?.find((v) => v.id === req.params.id);

  if (!visit) {
    return res.status(404).json({ ok: false, error: "Visit not found" });
  }

  const caregiver = demoData.caregivers?.find((c) => c.id === visit.caregiverId);
  const patient = demoData.patients?.find((p) => p.id === visit.patientId);

  // Generate risk factors
  const riskFactors = [];

  if (caregiver) {
    if (caregiver.noshowRate > 0.15) {
      riskFactors.push({
        type: "caregiver_history",
        severity: "high",
        description: `${(caregiver.noshowRate * 100).toFixed(0)}% no-show rate (vs 8% average)`,
        impact: 30,
      });
    }

    if (caregiver.hoursPerWeek > 45) {
      riskFactors.push({
        type: "workload",
        severity: "moderate",
        description: `Working ${caregiver.hoursPerWeek} hours/week (burnout risk)`,
        impact: 15,
      });
    }

    if (!caregiver.hasReliableTransportation) {
      riskFactors.push({
        type: "transportation",
        severity: "high",
        description: "No reliable transportation on file",
        impact: 20,
      });
    }
  }

  if (visit.shiftType === "Overnight" || visit.shiftType === "Weekend") {
    riskFactors.push({
      type: "shift_difficulty",
      severity: "moderate",
      description: `${visit.shiftType} shift (harder to fill)`,
      impact: 15,
    });
  }

  if (visit.weather !== "clear") {
    riskFactors.push({
      type: "weather",
      severity: visit.weather === "snow" ? "high" : "moderate",
      description: `${visit.weather} forecast (driving hazard)`,
      impact: visit.weather === "snow" ? 25 : 10,
    });
  }

  // Recommended actions
  const actions = [];

  if (visit.riskLevel === "HIGH" || visit.riskLevel === "CRITICAL") {
    actions.push("URGENT: Call 6 hours before + 2 hours before shift");
    actions.push("Identify backup caregiver NOW");

    if (visit.weather !== "clear") {
      actions.push("Offer transportation assistance");
    }

    if (caregiver && caregiver.hoursPerWeek > 45) {
      actions.push("Consider reducing hours next week (burnout prevention)");
    }
  } else if (visit.riskLevel === "MODERATE") {
    actions.push("Standard confirmation call 2 hours before shift");
    actions.push("Have backup caregiver on standby");
  } else {
    actions.push("Optional: Light check-in 1 hour before shift");
  }

  res.json({
    ok: true,
    visit: {
      ...visit,
      caregiver: caregiver
        ? {
            id: caregiver.id,
            name: `${caregiver.firstName} ${caregiver.lastName}`,
            phone: caregiver.phone,
            reliability: caregiver.reliability,
            noshowRate: caregiver.noshowRate,
            hoursPerWeek: caregiver.hoursPerWeek,
            hasReliableTransportation: caregiver.hasReliableTransportation,
          }
        : null,
      patient: patient
        ? {
            id: patient.id,
            name: `${patient.firstName} ${patient.lastName}`,
            address: patient.address,
            phone: patient.phone,
            careType: patient.careType,
            difficultyScore: patient.difficultyScore,
          }
        : null,
      riskFactors,
      recommendedActions: actions,
    },
  });
});

/**
 * POST /api/visits/:id/confirm
 * Simulate confirmation call
 */
app.post("/api/visits/:id/confirm", (req, res) => {
  const visit = demoData.scheduledVisits?.find((v) => v.id === req.params.id);

  if (!visit) {
    return res.status(404).json({ ok: false, error: "Visit not found" });
  }

  // Simulate caregiver response (80% confirm, 20% can't make it)
  const confirmed = Math.random() > 0.2;

  visit.confirmationStatus = confirmed ? "confirmed" : "cancelled";
  visit.confirmationTime = new Date().toISOString();

  res.json({
    ok: true,
    confirmed,
    visit,
    message: confirmed
      ? "Caregiver confirmed - visit will proceed as scheduled"
      : "Caregiver cannot make it - ALERT: Find backup immediately!",
  });
});

/**
 * GET /api/reports/roi
 * ROI report (weekly/monthly)
 */
app.get("/api/reports/roi", (req, res) => {
  const agencyId = req.query.agencyId;
  const period = req.query.period || "week"; // week or month

  let visits = demoData.historicalVisits || [];
  if (agencyId) {
    visits = visits.filter((v) => v.agencyId === agencyId);
  }

  // Calculate metrics
  const totalVisits = visits.length;
  const noshows = visits.filter((v) => v.status === "no-show").length;
  const completed = visits.filter((v) => v.status === "completed").length;
  const noshowRate = totalVisits > 0 ? noshows / totalVisits : 0;

  // Estimate before/after (simulate 8-week improvement)
  const noshowRateBefore = 0.22; // Industry average
  const noshowRateAfter = noshowRate;
  const improvement = ((noshowRateBefore - noshowRateAfter) / noshowRateBefore) * 100;

  const noshowsPrevented = Math.round(totalVisits * (noshowRateBefore - noshowRateAfter));
  const avgRevenue = 200; // $200 per visit
  const revenueSaved = noshowsPrevented * avgRevenue;

  // Admin time saved
  const hoursPerVisit = 0.15; // 9 minutes per visit saved
  const timeSaved = Math.round(totalVisits * hoursPerVisit);
  const adminHourly = 25;
  const adminSavings = timeSaved * adminHourly;

  const totalSavings = revenueSaved + adminSavings;
  const copperCost = 800; // Pro plan
  const netSavings = totalSavings - copperCost;
  const roi = (netSavings / copperCost).toFixed(1);

  res.json({
    ok: true,
    period,
    metrics: {
      totalVisits,
      noshows,
      completed,
      noshowRate: parseFloat((noshowRate * 100).toFixed(1)),
      noshowRateBefore: parseFloat((noshowRateBefore * 100).toFixed(1)),
      improvement: parseFloat(improvement.toFixed(1)),
      noshowsPrevented,
      revenueSaved,
      timeSaved,
      adminSavings,
      totalSavings,
      copperCost,
      netSavings,
      roi: parseFloat(roi),
    },
  });
});

/**
 * GET /api/dashboard
 * Main dashboard data
 */
app.get("/api/dashboard", (req, res) => {
  const agencyId = req.query.agencyId;

  let agencies = demoData.agencies || [];
  let caregivers = demoData.caregivers || [];
  let scheduledVisits = demoData.scheduledVisits || [];
  let historicalVisits = demoData.historicalVisits || [];

  if (agencyId) {
    agencies = agencies.filter((a) => a.id === agencyId);
    caregivers = caregivers.filter((c) => c.agencyId === agencyId);
    scheduledVisits = scheduledVisits.filter((v) => v.agencyId === agencyId);
    historicalVisits = historicalVisits.filter((v) => v.agencyId === agencyId);
  }

  // High-risk visits today
  const today = new Date().toISOString().split("T")[0];
  const highRiskToday = scheduledVisits.filter((v) => {
    const visitDate = v.scheduledStart.split("T")[0];
    return visitDate === today && (v.riskLevel === "HIGH" || v.riskLevel === "CRITICAL");
  });

  res.json({
    ok: true,
    dashboard: {
      agencies: agencies.length,
      caregivers: caregivers.filter((c) => c.active).length,
      scheduledVisits: scheduledVisits.length,
      highRiskToday: highRiskToday.length,
      avgNoshowRate:
        agencies.length > 0
          ? parseFloat(
              (
                (agencies.reduce((sum, a) => sum + a.noshowRateAfter, 0) / agencies.length) *
                100
              ).toFixed(1),
            )
          : 0,
    },
    highRiskVisits: highRiskToday.slice(0, 5).map((v) => {
      const caregiver = caregivers.find((c) => c.id === v.caregiverId);
      const patient = demoData.patients?.find((p) => p.id === v.patientId);

      return {
        id: v.id,
        time: v.scheduledStart,
        riskLevel: v.riskLevel,
        riskScore: v.riskScore,
        caregiver: caregiver ? `${caregiver.firstName} ${caregiver.lastName}` : "Unknown",
        patient: patient ? `${patient.firstName} ${patient.lastName}` : "Unknown",
      };
    }),
  });
});

// --- SERVE DEMO DASHBOARD ---

app.get("/", (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Copper AI Demo Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
      color: #333;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 16px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 40px;
      text-align: center;
    }
    .header h1 { font-size: 32px; margin-bottom: 10px; }
    .header p { font-size: 18px; opacity: 0.9; }
    .content { padding: 40px; }
    .demo-nav {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }
    .demo-card {
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      padding: 30px;
      border-radius: 12px;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      text-decoration: none;
      color: #333;
    }
    .demo-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .demo-card h3 { font-size: 20px; margin-bottom: 10px; color: #667eea; }
    .demo-card p { font-size: 14px; color: #666; line-height: 1.5; }
    .api-docs {
      background: #f9fafb;
      padding: 20px;
      border-radius: 8px;
      margin-top: 20px;
    }
    .api-docs h3 { margin-bottom: 15px; color: #667eea; }
    .api-endpoint {
      background: white;
      padding: 12px;
      margin-bottom: 8px;
      border-radius: 6px;
      font-family: 'Courier New', monospace;
      font-size: 14px;
    }
    .api-endpoint .method {
      display: inline-block;
      background: #667eea;
      color: white;
      padding: 2px 8px;
      border-radius: 4px;
      margin-right: 10px;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🏥 Copper AI Demo Dashboard</h1>
      <p>Safe demo environment for testing and sales demos</p>
    </div>
    
    <div class="content">
      <h2 style="margin-bottom: 20px;">Demo Scenarios</h2>
      
      <div class="demo-nav">
        <a href="/api/agencies" class="demo-card">
          <h3>📊 View Agencies</h3>
          <p>See all 3 demo agencies with metrics</p>
        </a>
        
        <a href="/api/visits/scheduled?riskLevel=HIGH" class="demo-card">
          <h3>🚨 High-Risk Visits</h3>
          <p>View visits that need urgent attention</p>
        </a>
        
        <a href="/api/reports/roi?period=week" class="demo-card">
          <h3>💰 ROI Report</h3>
          <p>Weekly savings and ROI metrics</p>
        </a>
        
        <a href="/api/dashboard" class="demo-card">
          <h3>📈 Dashboard</h3>
          <p>Overview of all metrics</p>
        </a>
      </div>
      
      <div class="api-docs">
        <h3>API Endpoints</h3>
        
        <div class="api-endpoint">
          <span class="method">GET</span>
          /api/agencies - List all demo agencies
        </div>
        
        <div class="api-endpoint">
          <span class="method">GET</span>
          /api/agencies/:id - Get agency details
        </div>
        
        <div class="api-endpoint">
          <span class="method">GET</span>
          /api/caregivers?agencyId=XXX - List caregivers
        </div>
        
        <div class="api-endpoint">
          <span class="method">GET</span>
          /api/visits/scheduled?riskLevel=HIGH - Get scheduled visits
        </div>
        
        <div class="api-endpoint">
          <span class="method">GET</span>
          /api/visits/:id - Get visit details with risk analysis
        </div>
        
        <div class="api-endpoint">
          <span class="method">POST</span>
          /api/visits/:id/confirm - Simulate confirmation call
        </div>
        
        <div class="api-endpoint">
          <span class="method">GET</span>
          /api/reports/roi?period=week - Get ROI report
        </div>
        
        <div class="api-endpoint">
          <span class="method">GET</span>
          /api/dashboard?agencyId=XXX - Get dashboard metrics
        </div>
      </div>
      
      <div style="margin-top: 40px; padding: 20px; background: #e3f2fd; border-radius: 8px;">
        <h3 style="color: #1976d2; margin-bottom: 10px;">🎬 Next Steps</h3>
        <p style="line-height: 1.6;">
          1. Click on demo scenarios above to explore the data<br>
          2. Review the API endpoints and test them<br>
          3. Practice the 15-minute demo script (see README.md)<br>
          4. Use this in your first pilot recruitment calls!
        </p>
      </div>
    </div>
  </div>
</body>
</html>
  `);
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🚀 Copper AI Demo Server running!\n`);
  console.log(`   URL: http://localhost:${PORT}`);
  console.log(`   API: http://localhost:${PORT}/api/dashboard\n`);
  console.log(`📊 Demo Data Loaded:`);
  console.log(`   Agencies: ${demoData.agencies?.length || 0}`);
  console.log(`   Caregivers: ${demoData.caregivers?.length || 0}`);
  console.log(`   Scheduled Visits: ${demoData.scheduledVisits?.length || 0}`);
  console.log(`   Historical Visits: ${demoData.historicalVisits?.length || 0}\n`);
  console.log(`🎬 Ready for demos! Open http://localhost:${PORT} to get started.\n`);
});

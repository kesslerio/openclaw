#!/usr/bin/env node

/**
 * Demo Data Generator for Copper AI
 *
 * Generates realistic fake data for demo environment:
 * - Agencies (3 demo agencies)
 * - Caregivers (155 total with varied reliability)
 * - Visits (500+ scheduled, 5000+ historical)
 * - No-show events (realistic distribution)
 * - Confirmation calls (voice EVV logs)
 */

const { faker } = require("@faker-js/faker");

// Configuration
const CONFIG = {
  agencies: [
    {
      id: "demo-abc-001",
      name: "ABC Home Health",
      platform: "clearcare",
      caregivers: 50,
      noshowRate: 0.22, // 22% (before Copper AI)
      targetRate: 0.12, // 12% (after Copper AI)
    },
    {
      id: "demo-xyz-002",
      name: "XYZ Senior Care",
      platform: "axxess",
      caregivers: 30,
      noshowRate: 0.18,
      targetRate: 0.1,
    },
    {
      id: "demo-dfs-003",
      name: "Demo Family Services",
      platform: "both",
      caregivers: 75,
      noshowRate: 0.25,
      targetRate: 0.14,
      multiLocation: true,
      locations: ["Dallas", "Houston", "Austin"],
    },
  ],

  riskFactors: {
    LOW: { probability: 0.05, color: "green" },
    MODERATE: { probability: 0.15, color: "yellow" },
    HIGH: { probability: 0.35, color: "orange" },
    CRITICAL: { probability: 0.6, color: "red" },
  },

  shiftTypes: ["Morning", "Afternoon", "Evening", "Overnight", "Weekend", "24-hour"],

  visitDurations: [2, 3, 4, 6, 8, 12], // hours
};

/**
 * Generate realistic caregiver data
 */
function generateCaregivers(agencyId, count, platform) {
  const caregivers = [];

  for (let i = 0; i < count; i++) {
    const reliability = Math.random();
    let tier, noshowRate, hoursPerWeek;

    // 60% excellent, 25% good, 10% fair, 5% poor
    if (reliability > 0.95) {
      tier = "poor";
      noshowRate = 0.2 + Math.random() * 0.15; // 20-35%
      hoursPerWeek = 15 + Math.random() * 15; // 15-30 hrs (part-time, unreliable)
    } else if (reliability > 0.85) {
      tier = "fair";
      noshowRate = 0.1 + Math.random() * 0.1; // 10-20%
      hoursPerWeek = 25 + Math.random() * 20; // 25-45 hrs
    } else if (reliability > 0.6) {
      tier = "good";
      noshowRate = 0.05 + Math.random() * 0.05; // 5-10%
      hoursPerWeek = 30 + Math.random() * 15; // 30-45 hrs
    } else {
      tier = "excellent";
      noshowRate = 0.0 + Math.random() * 0.05; // 0-5%
      hoursPerWeek = 35 + Math.random() * 10; // 35-45 hrs (full-time, reliable)
    }

    const firstName = faker.person.firstName();
    const lastName = faker.person.lastName();
    const phone = faker.phone.number("###-###-####");

    caregivers.push({
      id: `${agencyId}-cg-${String(i + 1).padStart(3, "0")}`,
      agencyId,
      firstName,
      lastName,
      phone,
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@demo.com`,
      platform,
      reliability: tier,
      noshowRate: parseFloat(noshowRate.toFixed(3)),
      hoursPerWeek: Math.round(hoursPerWeek),
      hasReliableTransportation: Math.random() > 0.2, // 80% have reliable transport
      preferredShifts: faker.helpers.arrayElements(
        CONFIG.shiftTypes,
        faker.number.int({ min: 1, max: 3 }),
      ),
      active: Math.random() > 0.05, // 95% active, 5% inactive
      hiredDate: faker.date.past({ years: 2 }),
      languages: Math.random() > 0.7 ? ["English", "Spanish"] : ["English"],
    });
  }

  return caregivers;
}

/**
 * Generate realistic patient data
 */
function generatePatients(agencyId, count) {
  const patients = [];
  const texasCities = [
    "Dallas",
    "Houston",
    "Austin",
    "San Antonio",
    "Fort Worth",
    "Plano",
    "Arlington",
  ];

  for (let i = 0; i < count; i++) {
    const firstName = faker.person.firstName();
    const lastName = faker.person.lastName();
    const city = faker.helpers.arrayElement(texasCities);

    // Generate difficulty score (1-10, higher = harder visit)
    const hasComplexNeeds = Math.random() > 0.7; // 30% complex
    const difficultyScore = hasComplexNeeds
      ? 6 + Math.random() * 4 // 6-10 (complex)
      : 1 + Math.random() * 5; // 1-6 (standard)

    patients.push({
      id: `${agencyId}-pt-${String(i + 1).padStart(3, "0")}`,
      agencyId,
      firstName,
      lastName,
      address: `${faker.location.streetAddress()}, ${city}, TX ${faker.location.zipCode("#####")}`,
      phone: faker.phone.number("###-###-####"),
      difficultyScore: parseFloat(difficultyScore.toFixed(1)),
      complexNeeds: hasComplexNeeds,
      careType: hasComplexNeeds
        ? faker.helpers.arrayElement(["Hospice", "Post-surgical", "Dementia", "Palliative"])
        : faker.helpers.arrayElement([
            "Companion",
            "Personal Care",
            "Light Housekeeping",
            "Meal Prep",
          ]),
      emergencyContact: {
        name: faker.person.fullName(),
        phone: faker.phone.number("###-###-####"),
        relation: faker.helpers.arrayElement(["Daughter", "Son", "Spouse", "Sibling", "Friend"]),
      },
    });
  }

  return patients;
}

/**
 * Calculate visit risk score based on multiple factors
 */
function calculateRiskScore(caregiver, visit, weather = "clear") {
  let score = 0;

  // Factor 1: Caregiver history (40% weight)
  score += caregiver.noshowRate * 40;

  // Factor 2: Shift characteristics (30% weight)
  const shiftMultiplier = {
    Morning: 1.0,
    Afternoon: 1.1,
    Evening: 1.3,
    Overnight: 1.8,
    Weekend: 1.4,
    "24-hour": 1.5,
  };
  score += (shiftMultiplier[visit.shiftType] - 1) * 30;

  // Factor 3: Environmental factors (20% weight)
  const weatherMultiplier = {
    clear: 1.0,
    rain: 1.3,
    snow: 1.8,
    ice: 2.0,
    "extreme-cold": 1.5,
    "extreme-heat": 1.3,
  };
  score += (weatherMultiplier[weather] - 1) * 20;

  // Factor 4: Workload (10% weight)
  if (caregiver.hoursPerWeek > 45) {
    score += 10; // Burnout risk
  } else if (caregiver.hoursPerWeek < 20) {
    score += 5; // Unreliable part-timer
  }

  // Factor 5: Transportation
  if (!caregiver.hasReliableTransportation) {
    score += 15;
  }

  // Normalize to 0-100
  score = Math.min(100, Math.max(0, score));

  return score;
}

/**
 * Assign risk level based on score
 */
function getRiskLevel(score) {
  if (score < 15) return "LOW";
  if (score < 35) return "MODERATE";
  if (score < 60) return "HIGH";
  return "CRITICAL";
}

/**
 * Generate scheduled visits (next 7 days)
 */
function generateScheduledVisits(caregivers, patients, agencyId, count) {
  const visits = [];
  const now = new Date();

  for (let i = 0; i < count; i++) {
    const caregiver = faker.helpers.arrayElement(caregivers.filter((c) => c.active));
    const patient = faker.helpers.arrayElement(patients);

    // Schedule visit in next 7 days
    const daysOut = Math.floor(Math.random() * 7);
    const hour = faker.number.int({ min: 6, max: 20 }); // 6am-8pm starts
    const scheduledStart = new Date(now);
    scheduledStart.setDate(scheduledStart.getDate() + daysOut);
    scheduledStart.setHours(hour, 0, 0, 0);

    const duration = faker.helpers.arrayElement(CONFIG.visitDurations);
    const scheduledEnd = new Date(scheduledStart);
    scheduledEnd.setHours(scheduledEnd.getHours() + duration);

    // Determine shift type
    let shiftType;
    if (hour >= 6 && hour < 12) shiftType = "Morning";
    else if (hour >= 12 && hour < 17) shiftType = "Afternoon";
    else if (hour >= 17 && hour < 22) shiftType = "Evening";
    else shiftType = "Overnight";

    if (scheduledStart.getDay() === 0 || scheduledStart.getDay() === 6) {
      shiftType = "Weekend";
    }

    // Calculate risk
    const weather = faker.helpers.weighted([
      { value: "clear", weight: 60 },
      { value: "rain", weight: 20 },
      { value: "snow", weight: 10 },
      { value: "extreme-cold", weight: 5 },
      { value: "extreme-heat", weight: 5 },
    ]);

    const visit = {
      shiftType,
      duration,
      weather,
    };

    const riskScore = calculateRiskScore(caregiver, visit, weather);
    const riskLevel = getRiskLevel(riskScore);

    visits.push({
      id: `${agencyId}-visit-${String(i + 1).padStart(4, "0")}`,
      agencyId,
      caregiverId: caregiver.id,
      patientId: patient.id,
      scheduledStart: scheduledStart.toISOString(),
      scheduledEnd: scheduledEnd.toISOString(),
      duration,
      shiftType,
      status: "scheduled",
      riskScore: Math.round(riskScore),
      riskLevel,
      weather,
      confirmationRequired: true,
      confirmationStatus: riskLevel === "HIGH" || riskLevel === "CRITICAL" ? "pending" : null,
      createdAt: faker.date.recent({ days: 7 }).toISOString(),
    });
  }

  // Sort by scheduled start time
  visits.sort((a, b) => new Date(a.scheduledStart) - new Date(b.scheduledStart));

  return visits;
}

/**
 * Generate historical visits (past 90 days)
 */
function generateHistoricalVisits(caregivers, patients, agencyId, count, noshowRate) {
  const visits = [];
  const now = new Date();

  for (let i = 0; i < count; i++) {
    const caregiver = faker.helpers.arrayElement(caregivers);
    const patient = faker.helpers.arrayElement(patients);

    // Random date in past 90 days
    const daysAgo = Math.floor(Math.random() * 90);
    const scheduledStart = new Date(now);
    scheduledStart.setDate(scheduledStart.getDate() - daysAgo);
    scheduledStart.setHours(faker.number.int({ min: 6, max: 20 }), 0, 0, 0);

    const duration = faker.helpers.arrayElement(CONFIG.visitDurations);
    const scheduledEnd = new Date(scheduledStart);
    scheduledEnd.setHours(scheduledEnd.getHours() + duration);

    // Determine if no-show based on caregiver reliability + randomness
    const noshow = Math.random() < caregiver.noshowRate * (1 + (Math.random() - 0.5) * 0.5);

    const actualStart = noshow ? null : scheduledStart;
    const actualEnd = noshow ? null : scheduledEnd;

    visits.push({
      id: `${agencyId}-hist-${String(i + 1).padStart(5, "0")}`,
      agencyId,
      caregiverId: caregiver.id,
      patientId: patient.id,
      scheduledStart: scheduledStart.toISOString(),
      scheduledEnd: scheduledEnd.toISOString(),
      actualStart: actualStart ? actualStart.toISOString() : null,
      actualEnd: actualEnd ? actualEnd.toISOString() : null,
      duration,
      status: noshow ? "no-show" : "completed",
      confirmationMade: Math.random() > 0.3, // 70% got confirmation call
      createdAt: faker.date.past({ years: 1 }).toISOString(),
      completedAt: noshow ? null : actualEnd ? actualEnd.toISOString() : null,
    });
  }

  return visits;
}

/**
 * Generate all demo data
 */
function generateAllDemoData() {
  const data = {
    agencies: [],
    caregivers: [],
    patients: [],
    scheduledVisits: [],
    historicalVisits: [],
    metadata: {
      generated: new Date().toISOString(),
      version: "1.0.0",
      purpose: "Demo environment for Copper AI",
    },
  };

  // Generate for each agency
  CONFIG.agencies.forEach((agencyConfig) => {
    // Agency
    data.agencies.push({
      id: agencyConfig.id,
      name: agencyConfig.name,
      platform: agencyConfig.platform,
      active: true,
      caregiverCount: agencyConfig.caregivers,
      noshowRateBefore: agencyConfig.noshowRate,
      noshowRateAfter: agencyConfig.targetRate,
      multiLocation: agencyConfig.multiLocation || false,
      locations: agencyConfig.locations || null,
      createdAt: faker.date.past({ years: 2 }).toISOString(),
    });

    // Caregivers
    const caregivers = generateCaregivers(
      agencyConfig.id,
      agencyConfig.caregivers,
      agencyConfig.platform,
    );
    data.caregivers.push(...caregivers);

    // Patients (1.5x caregivers)
    const patientCount = Math.round(agencyConfig.caregivers * 1.5);
    const patients = generatePatients(agencyConfig.id, patientCount);
    data.patients.push(...patients);

    // Scheduled visits (next 7 days, ~3-4 per caregiver)
    const scheduledCount = Math.round(agencyConfig.caregivers * 3.5);
    const scheduledVisits = generateScheduledVisits(
      caregivers,
      patients,
      agencyConfig.id,
      scheduledCount,
    );
    data.scheduledVisits.push(...scheduledVisits);

    // Historical visits (past 90 days, ~30 per caregiver)
    const historicalCount = agencyConfig.caregivers * 30;
    const historicalVisits = generateHistoricalVisits(
      caregivers,
      patients,
      agencyConfig.id,
      historicalCount,
      agencyConfig.noshowRate,
    );
    data.historicalVisits.push(...historicalVisits);
  });

  // Statistics
  data.stats = {
    agencies: data.agencies.length,
    caregivers: data.caregivers.length,
    patients: data.patients.length,
    scheduledVisits: data.scheduledVisits.length,
    historicalVisits: data.historicalVisits.length,
    totalVisits: data.scheduledVisits.length + data.historicalVisits.length,
  };

  return data;
}

// Export for use in other scripts
module.exports = {
  generateAllDemoData,
  generateCaregivers,
  generatePatients,
  generateScheduledVisits,
  generateHistoricalVisits,
  calculateRiskScore,
  getRiskLevel,
};

// CLI usage
if (require.main === module) {
  console.log("🎲 Generating demo data for Copper AI...\n");

  const data = generateAllDemoData();

  console.log("📊 Generated:");
  console.log(`   Agencies: ${data.stats.agencies}`);
  console.log(`   Caregivers: ${data.stats.caregivers}`);
  console.log(`   Patients: ${data.stats.patients}`);
  console.log(`   Scheduled Visits: ${data.stats.scheduledVisits}`);
  console.log(`   Historical Visits: ${data.stats.historicalVisits}`);
  console.log(`   Total: ${data.stats.totalVisits} visits\n`);

  // Save to JSON
  const fs = require("fs");
  const outputPath = "./demo-data.json";
  fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));

  console.log(`✅ Saved to: ${outputPath}`);
  console.log(`📦 File size: ${(fs.statSync(outputPath).size / 1024).toFixed(1)} KB\n`);
}

# EVV Integration Guide for iCare

_Research compiled: January 31, 2026_

## What is EVV?

Electronic Visit Verification (EVV) is a federally mandated system to verify home health visits. Required by the 21st Century Cures Act for Medicaid-funded services.

**What it tracks:**

- Type of service performed
- Individual receiving the service
- Date of the service
- Location of service delivery
- Individual providing the service
- Time the service begins and ends

## Texas EVV Requirements

Texas requires EVV for certain Medicaid-funded home and community-based services through:

- Texas Health and Human Services Commission (HHSC)
- Managed Care Organizations (MCOs)

**Key Resource:** [Texas HHS EVV Page](https://www.hhs.texas.gov/providers/long-term-care-providers/long-term-care-provider-resources/electronic-visit-verification-evv)

**Aggregator:** TMHP (Texas Medicaid & Healthcare Partnership) handles EVV data aggregation.

---

## Top EVV Software Providers

### Tier 1: Enterprise / Medicaid Specialists

| Software                  | Best For                             | Pricing    | Integration Complexity |
| ------------------------- | ------------------------------------ | ---------- | ---------------------- |
| **HHAeXchange**           | Medicaid-only agencies               | Enterprise | High                   |
| **Sandata**               | Medicaid compliance, state contracts | Enterprise | High                   |
| **MatrixCare**            | Large providers with clinical needs  | Enterprise | High                   |
| **WellSky Personal Care** | Enterprise personal care             | Enterprise | Medium-High            |

### Tier 2: Mid-Market

| Software       | Best For               | Pricing    | Integration Complexity |
| -------------- | ---------------------- | ---------- | ---------------------- |
| **AlayaCare**  | Cloud-native agencies  | Mid-market | Medium                 |
| **Axxess**     | Flexible, cloud-based  | Mid-market | Medium                 |
| **CareBridge** | Value-based care focus | Mid-market | Medium                 |
| **KanTime**    | Growing agencies       | Mid-market | Medium                 |

### Tier 3: Small Agency / Affordable

| Software          | Best For                   | Pricing    | Integration Complexity |
| ----------------- | -------------------------- | ---------- | ---------------------- |
| **Alora**         | Small agencies, simplicity | Affordable | Low                    |
| **ClearCare**     | Private-pay agencies       | Affordable | Low                    |
| **AxisCare**      | Small-mid agencies         | Affordable | Low                    |
| **CareSmartz360** | Budget-conscious           | Affordable | Low                    |
| **INMYTEAM**      | All-in-one operations      | Affordable | Low                    |

---

## Integration Strategy for iCare

### Priority 1: Most Common in Texas

Based on market research, prioritize integrations with:

1. **Sandata** - State aggregator, widely used
2. **HHAeXchange** - Dominant in Medicaid space
3. **Axxess** - Popular with Texas agencies
4. **AlayaCare** - Growing cloud-native player

### Priority 2: Emerging / Private Pay

1. **ClearCare** - Private pay market
2. **AxisCare** - SMB friendly
3. **WellSky** - Enterprise expansion

### Integration Approaches

#### Option A: Direct API Integration

- Connect to each EVV system's API
- Push/pull visit data
- Pros: Tight integration, real-time sync
- Cons: Multiple integrations to maintain

#### Option B: Via State Aggregator (TMHP for Texas)

- Single integration with state aggregator
- All EVV data flows through one point
- Pros: Simpler, single point of compliance
- Cons: May have latency, less flexible

#### Option C: Webhook/File-Based

- Accept EVV data exports
- Parse and ingest
- Pros: Works with any system
- Cons: Not real-time, manual setup

**Recommendation:** Start with Option C (file import) for quick launch, then build Option A integrations for top 3 systems.

---

## Integration Points for Voice AI

### What iCare Voice Agent Can Capture

| Data Point           | EVV Field    | How Voice Captures It            |
| -------------------- | ------------ | -------------------------------- |
| Visit start time     | Time In      | "Hi, I'm here at Mrs. Johnson's" |
| Visit end time       | Time Out     | "I'm finishing up now"           |
| Service type         | Service Code | Agent asks what was done         |
| Location             | GPS/Address  | Phone location or confirmation   |
| Caregiver ID         | Provider ID  | Voice ID or phone number         |
| Patient confirmation | Recipient ID | Patient verbal confirmation      |

### Workflow Integration

```
[Caregiver arrives]
    ↓
[Calls iCare voice line]
    ↓
[Voice agent verifies identity]
    ↓
[Captures clock-in with GPS]
    ↓
[Syncs to EVV system]
    ↓
[Visit occurs]
    ↓
[Caregiver calls to clock out]
    ↓
[Voice captures end time + notes]
    ↓
[EVV record completed]
    ↓
[Ready for billing]
```

---

## Competitive Advantage

### What Competitors DON'T Have

1. **Retell/Vapi/Bland** - No EVV integration, no understanding of home health
2. **Dialora** - Generic healthcare, no EVV awareness
3. **Generic IVR** - Can capture time but no smart workflows

### iCare Differentiation

- **EVV-aware voice agents** that understand clock-in/out flows
- **Smart validation** - catches missed check-ins before they become compliance issues
- **Caregiver-friendly** - natural conversation, not button-pressing
- **Multilingual** - Spanish speakers are significant in Texas home health
- **Real-time alerts** - coordinator notified of late check-ins

---

## Sales Talking Points

### For Agencies Using HHAeXchange/Sandata:

> "We integrate with your existing EVV system. Our voice agent captures clock-in/out and syncs automatically. No double entry, no compliance gaps."

### For Agencies Struggling with EVV:

> "EVV is a pain point for everyone. Our voice agent makes it as simple as a phone call. Caregivers call in, we handle the rest."

### For Private Pay Agencies:

> "You're not required to use EVV, but our verification calls give you the same accountability. Know exactly when visits happen."

---

## Technical Notes

### API Documentation Links (To Research)

- HHAeXchange: Partner API (requires agreement)
- Sandata: State contracts vary
- AlayaCare: Open API program
- Axxess: Developer documentation available

### Data Format Standards

- Texas uses standard EVV file formats
- TMHP companion guides available
- EDI 837P for claims integration

---

## Next Steps for iCare Development

1. [ ] Validate top 3 EVV systems used by pilot customers
2. [ ] Build file import for EVV data (CSV/Excel)
3. [ ] Design voice flow for clock-in/clock-out
4. [ ] Research API partnerships with HHAeXchange/AlayaCare
5. [ ] Create compliance documentation for EVV workflows
6. [ ] Test Spanish language support for caregiver calls

---

_Research by Nike 🐾_

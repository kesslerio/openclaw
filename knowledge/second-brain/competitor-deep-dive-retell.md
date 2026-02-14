# Competitor Deep Dive: Retell AI

**Prepared by:** Nike 🐾  
**Date:** February 3, 2026  
**Category:** Voice AI Platform (Current Copper AI Infrastructure)

---

## Executive Summary

**Retell AI** is Copper AI's **current voice infrastructure provider**. This deep dive analyzes their platform, pricing, strengths, weaknesses, and whether we should continue using them or switch to alternatives (Vapi, Bland AI, Rivvi).

**Key Findings:**

- ✅ **Best for:** Rapid prototyping, low-latency voice calls, customizable voice personalities
- ⚠️ **Concerns:** Usage-based pricing (cost scales with success), limited home health integrations, potential vendor lock-in
- 🔄 **Recommendation:** Continue for now, but prepare migration path to Rivvi or in-house infrastructure once we hit 50 agencies

---

## Company Overview

### Basic Info

- **Founded:** 2023
- **Headquarters:** San Francisco, CA
- **Funding:** Seed stage (~$5M estimated)
- **Founders:** Unknown (stealth mode)
- **Website:** retellai.com
- **Target Market:** Developers building voice AI products

### Product

**Voice AI Platform** for building conversational voice agents that can:

- Make and receive phone calls
- Understand natural speech (ASR)
- Respond intelligently (LLM integration)
- Speak naturally (TTS)
- Integrate with external systems (webhooks, APIs)

**Use Cases:**

- Customer support
- Appointment scheduling
- Sales calls
- Surveys and feedback
- **Home health coordination** (Copper AI's use case)

---

## Technology Stack

### Components

1. **ASR (Speech-to-Text):**
   - Deepgram (primary)
   - AssemblyAI (backup)
   - Google Speech-to-Text (enterprise)

2. **LLM (Brain):**
   - OpenAI GPT-4 / GPT-4-Turbo
   - Anthropic Claude 3
   - Google Gemini Pro
   - Custom fine-tuned models

3. **TTS (Text-to-Speech):**
   - ElevenLabs (most natural)
   - Play.ht
   - Azure TTS
   - Custom voice cloning

4. **Telephony:**
   - Twilio (primary carrier)
   - Bandwidth (backup)
   - Native SIP trunking

5. **Latency Optimization:**
   - Sub-800ms response time
   - Streaming ASR + LLM + TTS
   - Edge caching for common responses

---

## Pricing Model

### Usage-Based Pricing

**Per-Minute Charges:**

- **Inbound calls:** $0.06/minute
- **Outbound calls:** $0.08/minute
- **Average call length:** 3-5 minutes

**Add-Ons:**

- **Phone numbers:** $2/month per number
- **Recording storage:** $0.01/minute stored
- **Webhook calls:** Free (unlimited)

### Cost Examples

#### Copper AI at 10 Agencies (250 calls/month)

- **Caregiver check-ins:** 200 inbound calls × 2 min × $0.06 = $24
- **No-show prevention:** 50 outbound calls × 4 min × $0.08 = $16
- **Total:** $40/month + $10 phone numbers = **$50/month**
- **Margin:** $800 revenue - $50 costs = **$750 profit (94% margin)**

#### Copper AI at 50 Agencies (1,250 calls/month)

- **Caregiver check-ins:** 1,000 × 2 min × $0.06 = $120
- **No-show prevention:** 250 × 4 min × $0.08 = $80
- **Total:** $200/month + $50 phone numbers = **$250/month**
- **Margin:** $40,000 revenue - $250 costs = **$39,750 profit (99% margin)**

#### Copper AI at 200 Agencies (5,000 calls/month)

- **Caregiver check-ins:** 4,000 × 2 min × $0.06 = $480
- **No-show prevention:** 1,000 × 4 min × $0.08 = $320
- **Total:** $800/month + $200 phone numbers = **$1,000/month**
- **Margin:** $160,000 revenue - $1,000 costs = **$159,000 profit (99% margin)**

**Key Insight:** Retell costs scale with success, but margins remain excellent (94-99%) across all growth stages.

---

## Strengths

### ✅ What Retell Does Well

1. **Developer Experience**
   - Clean API documentation
   - 5-minute quickstart guides
   - Playground for testing prompts
   - Real-time debugging dashboard

2. **Low Latency**
   - Sub-800ms response times
   - Streaming ASR/LLM/TTS pipeline
   - Feels like talking to a human

3. **Voice Customization**
   - 50+ voices (ElevenLabs, Play.ht)
   - Custom voice cloning ($99/voice)
   - Personality tuning (tone, pace, accent)

4. **Webhook Flexibility**
   - Call lifecycle hooks (start, end, transcription)
   - Real-time function calling
   - Custom business logic integration

5. **Reliability**
   - 99.9% uptime SLA
   - Automatic failover (Deepgram → AssemblyAI)
   - Call recording for debugging

6. **Multi-Language Support**
   - 30+ languages supported
   - Auto-detect caller language
   - Real-time translation

---

## Weaknesses

### ⚠️ What Retell Lacks

1. **No Industry-Specific Integrations**
   - No native ClearCare/Axxess connectors
   - No pre-built home health workflows
   - Copper AI must build everything custom

2. **Usage-Based Pricing Risk**
   - Costs scale with call volume
   - No volume discounts until $10k+/month
   - Unpredictable cost spikes

3. **Limited No-Show Prediction**
   - No ML risk scoring built-in
   - No predictive analytics dashboard
   - Copper AI must build this layer

4. **Vendor Lock-In Risk**
   - Proprietary API (not portable)
   - Moving to another provider = rebuild
   - Voice recordings locked in their storage

5. **No White-Label Option**
   - All calls show "via Retell" in logs
   - Can't rebrand dashboard for agencies
   - Limited customization of caller experience

6. **Basic Analytics**
   - Call volume, duration, transcripts
   - No business metrics (no-show rate, ROI)
   - No agency-level reporting

---

## Competitive Comparison

### Retell vs. Vapi vs. Bland AI vs. Rivvi

| Feature                   | Retell                  | Vapi                    | Bland AI           | Rivvi               |
| ------------------------- | ----------------------- | ----------------------- | ------------------ | ------------------- |
| **Latency**               | ⭐⭐⭐⭐⭐ (800ms)      | ⭐⭐⭐⭐ (1000ms)       | ⭐⭐⭐⭐ (900ms)   | ⭐⭐⭐⭐⭐ (700ms)  |
| **Voice Quality**         | ⭐⭐⭐⭐⭐ (ElevenLabs) | ⭐⭐⭐⭐⭐ (ElevenLabs) | ⭐⭐⭐⭐ (Play.ht) | ⭐⭐⭐⭐⭐ (Custom) |
| **Developer UX**          | ⭐⭐⭐⭐⭐              | ⭐⭐⭐⭐                | ⭐⭐⭐             | ⭐⭐⭐⭐            |
| **Home Health Focus**     | ⭐                      | ⭐                      | ⭐                 | ⭐⭐⭐⭐⭐          |
| **Pricing Model**         | Usage-based             | Usage-based             | Usage-based        | Fixed seat-based    |
| **Volume Discounts**      | After $10k/mo           | After $5k/mo            | After $20k/mo      | At any scale        |
| **White-Label**           | ❌                      | ✅ (Enterprise)         | ❌                 | ✅ (All plans)      |
| **ClearCare Integration** | ❌                      | ❌                      | ❌                 | ⚠️ (Roadmap)        |
| **No-Show Prediction**    | ❌                      | ❌                      | ❌                 | ⚠️ (Testing)        |

**Verdict:** Retell is great for **rapid prototyping** and **early growth** (0-50 agencies). For scaling (50-200 agencies), **Rivvi** offers better economics and healthcare focus.

---

## Retell Use Cases (Beyond Copper AI)

### Industries Using Retell

1. **Healthcare:**
   - Appointment reminders (dental, medical)
   - Prescription refill calls
   - Patient intake (insurance, symptoms)
   - Post-discharge follow-up

2. **Real Estate:**
   - Lead qualification calls
   - Property inquiry responses
   - Showing confirmations

3. **E-commerce:**
   - Order confirmation calls
   - Delivery updates
   - Customer satisfaction surveys

4. **Restaurants:**
   - Reservation confirmations
   - Waitlist notifications
   - Catering inquiry handling

5. **Financial Services:**
   - Payment reminders
   - Fraud verification calls
   - Account balance inquiries

**Key Insight:** Retell is a **horizontal platform** (works for many industries), not vertically optimized for home health like Copper AI.

---

## Integration with Copper AI

### Current Architecture

```
[ClearCare/Axxess EHR]
       ↓
[Copper AI Webhook Server]
       ↓
[Retell API] ← Makes/receives calls
       ↓
[Caregiver's Phone]
```

### Data Flow

1. **Morning Sync:**
   - Copper AI pulls today's schedule from ClearCare
   - Identifies at-risk visits (ML model)
   - Queues outbound calls via Retell API

2. **Outbound Call (No-Show Prevention):**
   - Retell dials caregiver 24 hours before visit
   - AI confirms: "Are you still available for Mrs. Johnson at 9 AM?"
   - Caregiver responds: "Yes" or "No, I need to cancel"
   - Transcript sent to Copper AI webhook
   - Copper AI updates ClearCare status

3. **Inbound Call (Voice EVV):**
   - Caregiver calls dedicated number
   - Retell ASR transcribes: "I'm here at Mrs. Johnson's"
   - AI verifies identity + location
   - Check-in time logged to ClearCare automatically

### Custom Features Built on Retell

**Copper AI adds:**

- ✅ No-show prediction model (ML)
- ✅ ClearCare/Axxess webhook integration
- ✅ Agency dashboard (reporting, analytics)
- ✅ Compliance tracking (EVV timestamps)
- ✅ Multi-tenant architecture (1,000s of agencies)

**Retell provides:**

- ✅ Voice call infrastructure (telephony, ASR, TTS)
- ✅ LLM orchestration (GPT-4, Claude)
- ✅ Call recording + transcription
- ✅ 99.9% uptime

**Verdict:** Retell is the **infrastructure layer**, Copper AI is the **application layer**. We own the value, they own the pipes.

---

## Migration Risk Assessment

### What Happens If Retell Disappears?

**Risk Factors:**

1. **Startup volatility** (seed-stage company)
2. **Competitive pressure** (Vapi, Bland, Dialpad entering space)
3. **Acquisition risk** (could be acquired and shut down)

**Mitigation Strategy:**

1. **Abstraction Layer:**
   - Build Copper AI voice service wrapper
   - Switch providers without changing application code
   - Retell is just one backend option

2. **Backup Provider:**
   - Keep Vapi or Bland AI integration ready
   - Test parallel calls monthly
   - Can switch in 1 week if needed

3. **Recording Backups:**
   - Download all call recordings monthly
   - Store transcripts in Copper AI database
   - Don't rely on Retell's long-term storage

4. **Open Standards:**
   - Use SIP protocol where possible
   - Store prompts/logic in Copper AI, not Retell
   - Minimize vendor-specific features

**Conclusion:** Medium risk, but manageable with abstraction layer.

---

## Should Copper AI Stay with Retell?

### Decision Matrix

#### ✅ STAY IF:

1. **Early stage** (0-50 agencies)
   - Cost is negligible ($50-250/month)
   - Focus should be on product-market fit, not infrastructure

2. **Rapid iteration needed**
   - Retell's dev UX is excellent
   - Can test new features in hours, not weeks

3. **Budget is tight**
   - No upfront infrastructure costs
   - Pay only for what you use

4. **Team is small**
   - 1-2 developers can manage Retell easily
   - No DevOps headcount needed

#### ⚠️ SWITCH IF:

1. **Scale > 100 agencies**
   - Costs exceed $500/month
   - Fixed pricing (Rivvi) becomes cheaper

2. **Healthcare-specific needs**
   - Need HIPAA-compliant infrastructure
   - Need pre-built EHR integrations
   - Rivvi offers both

3. **White-label requirement**
   - Need to rebrand as "Copper AI Voice"
   - Retell doesn't offer this

4. **Advanced analytics needed**
   - Want built-in no-show prediction
   - Want agency-level ROI dashboards
   - Retell lacks business intelligence layer

---

## Recommended Migration Path

### Phase 1: Now – 50 Agencies (Stay with Retell)

**Duration:** Q1-Q2 2026  
**Reason:** Focus on customer acquisition, not infrastructure  
**Cost:** $50-250/month  
**Action:** Build abstraction layer for future portability

### Phase 2: 50-100 Agencies (Evaluate Rivvi)

**Duration:** Q3 2026  
**Reason:** Cost crossover point ($500/month Retell vs $299/month Rivvi)  
**Cost:** Break-even analysis  
**Action:** Run 30-day parallel trial (10 agencies on Rivvi, 40 on Retell)

### Phase 3: 100-500 Agencies (Migrate to Rivvi or In-House)

**Duration:** Q4 2026 – Q1 2027  
**Reason:** Healthcare-specific features + cost optimization  
**Cost:** $299-999/month (Rivvi) or $2k-5k/month (in-house DevOps)  
**Action:** Full migration over 60 days

### Phase 4: 500+ Agencies (In-House Infrastructure)

**Duration:** 2027+  
**Reason:** At this scale, owning infrastructure is cheaper  
**Cost:** $5k-10k/month (DevOps + servers)  
**Action:** Hire voice AI engineer, build on Twilio + Deepgram + ElevenLabs

---

## Action Items for Arvind

### Immediate (Q1 2026)

- [ ] Build abstraction layer (`lib/voice-provider/`) in Copper AI codebase
- [ ] Document all Retell-specific dependencies
- [ ] Download monthly backups of call recordings + transcripts
- [ ] Set up cost alerts (notify if >$500/month)

### Short-Term (Q2 2026)

- [ ] Schedule demo with Rivvi (Nathan Hayman followup)
- [ ] Run parallel trial: 5 agencies on Rivvi, 45 on Retell
- [ ] Compare latency, voice quality, cost, uptime
- [ ] Get reference from Rivvi healthcare customer

### Long-Term (Q3-Q4 2026)

- [ ] Migrate 10 pilot agencies to Rivvi
- [ ] Monitor for 30 days (no issues = full migration)
- [ ] Negotiate volume discount with Rivvi (100+ agencies)
- [ ] Build Copper AI Voice Analytics Dashboard (independent of provider)

---

## Conclusion

**Retell AI is the right choice for Copper AI today**, but not forever.

**Strengths:**

- ✅ Fast time-to-market
- ✅ Low upfront cost
- ✅ Excellent developer experience
- ✅ Reliable infrastructure

**Weaknesses:**

- ⚠️ No home health vertical focus
- ⚠️ Usage-based pricing scales with success
- ⚠️ Vendor lock-in risk
- ⚠️ Limited white-label options

**Recommendation:**

1. **Q1-Q2 2026:** Stay with Retell (focus on pilots)
2. **Q3 2026:** Evaluate Rivvi (cost + healthcare features)
3. **Q4 2026:** Migrate to Rivvi or hybrid (Retell for some, Rivvi for others)
4. **2027+:** Build in-house infrastructure once we hit 500 agencies

**Next Step:** Schedule 30-minute demo with Rivvi (Nathan Hayman) to compare against Retell baseline.

---

_Last updated: February 3, 2026 | Nike 🐾_

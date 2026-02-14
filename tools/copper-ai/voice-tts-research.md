# Voice/TTS for Copper AI - Complete Implementation Guide

**Prepared by:** Nike 🐾  
**Date:** Feb 1, 2026  
**Purpose:** Add professional voice capabilities to Copper AI agents

---

## 🎯 Why Voice/TTS Matters for Copper AI

### The Problem:

Home health agencies need natural, empathetic voice conversations with:

- ✅ Elderly patients (may not text well)
- ✅ Non-native English speakers
- ✅ Busy caregivers (hands-free communication)
- ✅ Appointment confirmations (phone call = higher engagement)

### The Opportunity:

**Voice AI that sounds human** = higher patient satisfaction + compliance

---

## 🏆 Best TTS Solutions for Copper AI

### 1. ElevenLabs (RECOMMENDED) ⭐

**Why ElevenLabs?**

- ✅ **Most human-like** voice quality (indistinguishable from real person)
- ✅ **Voice cloning** - Create branded voice for your agency
- ✅ **Emotional range** - Can sound empathetic, urgent, cheerful
- ✅ **Low latency** - Fast enough for real-time calls (~300ms)
- ✅ **32 languages** - Perfect for diverse patient populations

**Pricing:**

- **Starter:** $5/month - 30,000 characters (~45 minutes of speech)
- **Creator:** $22/month - 100,000 chars (~2.5 hours)
- **Independent:** $99/month - 500,000 chars (~12 hours)
- **Enterprise:** Custom - Unlimited

**For Copper AI:** Independent plan = ~400 patient calls/month at average 2min/call

**Cost per call:** ~$0.25 for voice (vs $0.05-0.15 for other services)

### 2. Retell AI (Voice Infrastructure)

**What it does:**

- Complete voice infrastructure (not just TTS)
- Handles: STT (Deepgram) + LLM + TTS (ElevenLabs) + Phone calls
- Built for conversational AI agents

**Pricing:**

- $0.18/minute (includes ALL components)
- Phone number: $1/month
- No setup fees

**For Copper AI:** This is your MAIN competitor! Consider white-labeling or building similar.

### 3. Deepgram (STT - Speech to Text)

**Why Deepgram?**

- ✅ **Best accuracy** for medical terminology
- ✅ **Real-time** streaming (<50ms latency)
- ✅ **Accent handling** - Great for diverse populations
- ✅ **Affordable** - $0.0043/minute

**Pricing:**

- Pay-as-you-go: $0.0043/min
- Growth: $0.0036/min (with volume)

### 4. PlayHT (Alternative TTS)

**Pros:**

- Cheaper than ElevenLabs ($0.05/1000 chars vs $0.30)
- Good quality (not quite ElevenLabs level)
- Real-time streaming

**Use case:** Budget option if ElevenLabs too expensive

---

## 🔧 Technical Architecture

### Option A: Build from Scratch (More Control)

```
Patient Call
    ↓
Twilio Phone Number
    ↓
Deepgram STT (Audio → Text)
    ↓
OpenAI GPT-4 (Process + Decide)
    ↓
ElevenLabs TTS (Text → Audio)
    ↓
Twilio (Play audio to patient)
```

**Stack:**

- **Phone:** Twilio ($1/month/number + $0.0085/min)
- **STT:** Deepgram ($0.0043/min)
- **LLM:** GPT-4 ($0.03/1k tokens, ~$0.10/call)
- **TTS:** ElevenLabs ($0.25/call)
- **Total:** ~$0.37/minute

### Option B: Use Retell AI (Faster to Market)

```
Patient Call
    ↓
Retell AI (handles everything)
    ↓
Your Custom Logic (via webhooks)
```

**Pricing:** $0.18/min (includes phone + STT + TTS + infrastructure)

**Pros:**

- ✅ Faster to build (days vs weeks)
- ✅ Lower cost per minute
- ✅ Less complexity

**Cons:**

- ❌ Less customization
- ❌ Vendor lock-in
- ❌ Competitor (using their platform)

---

## 🎙️ Voice Quality Comparison

### ElevenLabs Sample Voices:

**Rachel** (Empathetic, Female)

- Perfect for: Patient calls, reminders, follow-ups
- Tone: Warm, caring, professional
- Use when: Talking to elderly or anxious patients

**Josh** (Professional, Male)

- Perfect for: Appointment confirmations, scheduling
- Tone: Clear, confident, friendly
- Use when: Business-like interactions

**Bella** (Multilingual)

- Perfect for: Spanish-speaking patients
- Tone: Natural, warm
- Use when: Non-English calls

### Custom Voice Cloning:

**Create YOUR agency's voice:**

1. Record 30 minutes of the same speaker
2. Upload to ElevenLabs
3. Get custom voice ID
4. Use for ALL your calls

**Benefits:**

- ✅ Brand consistency
- ✅ Patients recognize "your" voice
- ✅ Can train to say medical terms correctly

---

## 💻 Implementation Code

### ElevenLabs Integration

```javascript
const axios = require("axios");
const fs = require("fs");

async function generateSpeech(text, voiceId = "EXAVITQu4vr4xnSDxMaL") {
  const apiKey = process.env.ELEVENLABS_API_KEY;

  const response = await axios.post(
    `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
    {
      text: text,
      model_id: "eleven_multilingual_v2", // Supports 32 languages
      voice_settings: {
        stability: 0.5, // 0-1, higher = more consistent
        similarity_boost: 0.75, // 0-1, higher = more like original voice
        style: 0.5, // NEW: Emotional expressiveness
        use_speaker_boost: true,
      },
    },
    {
      headers: {
        Accept: "audio/mpeg",
        "xi-api-key": apiKey,
        "Content-Type": "application/json",
      },
      responseType: "arraybuffer",
    },
  );

  return Buffer.from(response.data);
}

// Example: Generate appointment reminder
async function appointmentReminder(patientName, date, time) {
  const message = `
    Hi ${patientName}, this is Copper AI calling from your home health agency.
    
    I'm calling to confirm your appointment scheduled for ${date} at ${time}.
    
    If you need to reschedule, just say "reschedule" and I'll help you find a new time.
    
    Otherwise, we'll see you ${date} at ${time}. Have a great day!
  `;

  const audioBuffer = await generateSpeech(message);

  // Save to file or stream to Twilio
  fs.writeFileSync("reminder.mp3", audioBuffer);

  return audioBuffer;
}
```

### Real-time Streaming (for conversations)

```javascript
const WebSocket = require("ws");

function streamTTS(text, voiceId) {
  const ws = new WebSocket(`wss://api.elevenlabs.io/v1/text-to-speech/${voiceId}/stream`);

  ws.on("open", () => {
    ws.send(
      JSON.stringify({
        text: text,
        model_id: "eleven_turbo_v2", // Faster for real-time
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
        },
      }),
    );
  });

  ws.on("message", (audioChunk) => {
    // Stream audio chunk to patient immediately
    playAudioChunk(audioChunk);
  });
}
```

### Deepgram STT Integration

```javascript
const { Deepgram } = require("@deepgram/sdk");

async function transcribeAudio(audioBuffer) {
  const deepgram = new Deepgram(process.env.DEEPGRAM_API_KEY);

  const response = await deepgram.transcription.preRecorded(
    {
      buffer: audioBuffer,
      mimetype: "audio/mp3",
    },
    {
      punctuate: true,
      model: "nova-2", // Latest model
      language: "en",
      diarize: true, // Speaker detection
      smart_format: true, // Auto formatting
      keywords: ["appointment", "medication", "visit"], // Boost medical terms
    },
  );

  return response.results.channels[0].alternatives[0].transcript;
}
```

---

## 🏥 Use Cases for Copper AI

### 1. Appointment Reminders

```javascript
const reminderScript = `
Hi [NAME], this is [AGENCY] calling with a friendly reminder.

Your home health visit is scheduled for [DATE] at [TIME].

Your nurse [NURSE_NAME] will arrive at your home.

If you need to cancel or reschedule, please call us at [PHONE].

We look forward to seeing you [DATE]!
`;
```

### 2. Appointment Scheduling

```javascript
const schedulingScript = `
Hi [NAME], I'm calling from [AGENCY] to schedule your home health visit.

We have availability on:
- Monday at 10 AM
- Tuesday at 2 PM
- Wednesday at 9 AM

Which time works best for you?

[WAIT FOR RESPONSE]

Great! I've scheduled you for [SELECTED_TIME]. You'll receive a confirmation text shortly.

Is there anything else I can help you with today?
`;
```

### 3. Post-Visit Follow-up

```javascript
const followUpScript = `
Hi [NAME], this is [AGENCY] calling to check in after your visit yesterday.

How are you feeling today?

[WAIT FOR RESPONSE]

[If positive:] That's wonderful to hear! Remember to [CARE_INSTRUCTIONS].

[If negative:] I'm sorry to hear that. Let me connect you with a nurse right away.

Do you have any questions about your care plan or medications?
`;
```

---

## 📊 Cost Analysis

### Scenario: 100 patient calls/day

**Option A: Build Your Own**
| Component | Cost/min | Minutes/day | Monthly Cost |
|-----------|----------|-------------|--------------|
| Twilio | $0.0085 | 200 | $51 |
| Deepgram STT | $0.0043 | 200 | $25.80 |
| GPT-4 | ~$0.05/call | 100 | $150 |
| ElevenLabs | ~$0.125/call | 100 | $375 |
| **TOTAL** | | | **$601.80/month** |

**Option B: Use Retell AI**
| Component | Cost/min | Minutes/day | Monthly Cost |
|-----------|----------|-------------|--------------|
| Retell AI | $0.18 | 200 | $1,080 |
| **TOTAL** | | | **$1,080/month** |

**Savings with Option A:** $478/month

---

## 🎯 Recommended Approach for Copper AI

### Phase 1: MVP with Retell AI (Week 1-2)

**Why:** Get to market FAST

- ✅ Use Retell to validate product-market fit
- ✅ Test with 2-3 pilot agencies
- ✅ Gather feedback on voice quality
- ✅ Prove ROI to customers

**Cost:** ~$200-500/month (depending on usage)

### Phase 2: Build Custom (Month 2-3)

**Why:** Better margins, more control

- ✅ Migrate to your own stack
- ✅ Add custom features
- ✅ Lower cost per call = higher margins
- ✅ White-label completely

**Cost:** ~$600/month + dev time

### Phase 3: Scale & Optimize (Month 4+)

**Why:** Competitive advantage

- ✅ Voice cloning for each agency
- ✅ Multi-language support
- ✅ Advanced routing logic
- ✅ Integration with EMRs

---

## 🚀 Quick Start Guide for Nike

### Step 1: Get API Keys

1. **ElevenLabs:** https://elevenlabs.io (Sign up, get API key)
2. **Deepgram:** https://deepgram.com (Free $200 credit)
3. **OpenAI:** Already have this
4. **Twilio:** https://twilio.com (For phone calls)

### Step 2: Test Voice Quality

```bash
node test-voice.js
```

```javascript
// test-voice.js
const axios = require("axios");
const fs = require("fs");

async function test() {
  const text =
    "Hi, this is Copper AI calling to confirm your appointment tomorrow at 2 PM. Can you confirm you'll be available?";

  // Generate with ElevenLabs
  const response = await axios.post(
    "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL",
    { text, model_id: "eleven_multilingual_v2" },
    {
      headers: { "xi-api-key": process.env.ELEVENLABS_API_KEY },
      responseType: "arraybuffer",
    },
  );

  fs.writeFileSync("test.mp3", response.data);
  console.log("✅ Voice generated! Play test.mp3");
}

test();
```

### Step 3: Build Simple Demo

- Accept patient name + appointment time
- Generate personalized reminder
- Play via web or send via Twilio

---

## 🐾 Nike's Verdict

**ElevenLabs is THE CHOICE for Copper AI.**

**Why?**

- Voice quality = competitive moat (patients can tell difference)
- Emotional range = better patient experience
- Voice cloning = agencies can have their own "voice"
- 32 languages = address diverse patient populations

**Cost?**

- Yes, it's 2-3x more expensive than alternatives
- BUT: Voice quality is 10x better
- Customer retention = worth the premium

**Build or buy?**

- **Month 1:** Use Retell to validate
- **Month 2:** Build your own with ElevenLabs
- **Month 3+:** Custom features, voice cloning, multi-language

**Nike can build:** Full voice pipeline in 3-5 days

---

**Ready to start?** Nike has API keys, sample code, and can have a demo running tomorrow! 🐾

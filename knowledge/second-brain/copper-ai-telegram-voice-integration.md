# Copper AI - Telegram Bot + Voice Integration Plan

**Created:** Feb 1, 2026  
**For:** Arvind Sarin / Copper Digital  
**Purpose:** Technical implementation plan for Telegram bot with voice capabilities

---

## 🎯 Executive Summary

**Goal:** Build a Telegram bot for Copper AI that handles voice messages, provides TTS responses, and manages home health agency workflows.

**Key Capabilities:**

- ✅ Receive voice messages from caregivers/patients → auto-transcribe
- ✅ Send voice responses (TTS) for better accessibility
- ✅ Text chat for admin tasks (scheduling, documentation)
- ✅ Integration with existing Copper AI voice agent platform

**Timeline:** 2-3 weeks for MVP

**Cost Estimate:**

- Development: Internal (Nike can build)
- ElevenLabs API: ~$99-330/month (depending on volume)
- Telegram Bot API: FREE

---

## 📱 Part 1: Telegram Bot Setup

### Core Architecture

```
┌─────────────────┐
│  Telegram User  │ (Caregiver, Patient, Admin)
└────────┬────────┘
         │ Voice/Text messages
         ▼
┌─────────────────┐
│  Telegram Bot   │ (Node.js + Telegraf/node-telegram-bot-api)
└────────┬────────┘
         │
         ├──► Voice Message → Download OGG/MP3
         │                  → Convert to WAV (if needed)
         │                  → Send to Whisper/AssemblyAI
         │                  → Get transcript
         │
         ├──► Text Message  → Process with Copper AI logic
         │                  → Generate response
         │
         └──► Send Response → Text (Telegram native)
                            → Voice (ElevenLabs TTS → OGG)
```

### Tech Stack

**Option A: Telegraf (Recommended)**

```javascript
const { Telegraf } = require("telegraf");
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Handle voice messages
bot.on("voice", async (ctx) => {
  const fileId = ctx.message.voice.file_id;
  const file = await ctx.telegram.getFileLink(fileId);
  // Download → Transcribe → Process
});

// Handle text messages
bot.on("text", async (ctx) => {
  const userMessage = ctx.message.text;
  // Process with Copper AI
  await ctx.reply("Response here");
});

bot.launch();
```

**Option B: node-telegram-bot-api**

- More low-level control
- Slightly more complex but flexible

**Recommendation:** Use Telegraf for faster development, better middleware support.

### Voice Message Handling

**Telegram's Audio Format:**

- Voice notes: `.ogg` (Opus codec)
- Audio files: `.mp3`, `.m4a`, etc.
- Video notes: `.mp4` (extract audio)

**Transcription Options:**

| Service                    | Pros                           | Cons                             | Cost       |
| -------------------------- | ------------------------------ | -------------------------------- | ---------- |
| **OpenAI Whisper (Local)** | Free, private, multilingual    | Requires compute (CPU/GPU)       | $0         |
| **OpenAI Whisper API**     | Easy, accurate, 98+ languages  | $0.006/min ($0.36/hr)            | Low        |
| **AssemblyAI**             | Real-time, speaker diarization | $0.00025/sec ($0.90/hr)          | Medium     |
| **Telegram Built-in**      | Native API support             | Limited languages, less accurate | FREE       |
| **Google Speech-to-Text**  | Good accuracy                  | More expensive                   | $0.024/min |

**Recommendation for Copper AI:**

- **MVP:** OpenAI Whisper API (cheap, accurate, 98 languages)
- **Scale:** Local Whisper deployment (save costs at high volume)
- **Fallback:** Telegram's native transcription (free but limited)

**Code Example:**

```javascript
const fs = require("fs");
const axios = require("axios");
const FormData = require("form-data");

async function transcribeAudio(filePath) {
  const formData = new FormData();
  formData.append("file", fs.createReadStream(filePath));
  formData.append("model", "whisper-1");
  formData.append("language", "en"); // Or auto-detect

  const response = await axios.post("https://api.openai.com/v1/audio/transcriptions", formData, {
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      ...formData.getHeaders(),
    },
  });

  return response.data.text;
}
```

### Telegram Bot Features for Home Health

**Must-Have Features:**

1. **Voice Message Support** - Caregivers can report patient status hands-free
2. **Text Commands** - `/status`, `/schedule`, `/help`
3. **Photo Upload** - Document wounds, medication labels
4. **Location Sharing** - Track caregiver visits (HIPAA compliant)
5. **Inline Buttons** - Quick actions (Confirm visit, Report issue)
6. **Rich Text** - Markdown for formatted responses

**Example Commands:**

```
/start - Welcome message + setup
/status - Check patient status
/schedule - View upcoming visits
/report [text] - Submit incident report
/help - Command list
/call - Initiate voice agent call
```

**Privacy Considerations:**

- ⚠️ Telegram is **NOT HIPAA compliant** by default
- ✅ Use end-to-end encryption (Secret Chats only, no bots)
- ✅ For bots: Encrypt PHI before storing, comply with BAA requirements
- ✅ Telegram Business API (paid) offers more controls
- ✅ Alternative: Use Telegram as a **trigger** → move to secure channel

**Recommendation:** Use Telegram for **notifications** and **non-PHI interactions**. For PHI, redirect to HIPAA-compliant portal or secure voice call.

---

## 🔊 Part 2: Voice Synthesis (TTS)

### ElevenLabs Integration

**Why ElevenLabs?**

- ✅ Most natural-sounding TTS (better than Google/Amazon)
- ✅ Emotional delivery (important for patient care)
- ✅ 32 languages (Multilingual v2 + Flash v2.5)
- ✅ Voice cloning (create branded "Copper AI" voice)
- ✅ Ultra-low latency (75ms with Flash v2.5)
- ✅ API-first design

**Pricing:**

| Tier        | Monthly Cost | Characters/Month | Credits | Use Case     |
| ----------- | ------------ | ---------------- | ------- | ------------ |
| **Free**    | $0           | 10,000 chars     | 10k     | Testing only |
| **Starter** | $5           | 30,000 chars     | 30k     | Small pilot  |
| **Creator** | $22          | 100,000 chars    | 100k    | Early stage  |
| **Pro**     | $99          | ~100,000 chars   | 100k    | Production   |
| **Scale**   | $330         | ~500,000 chars   | 500k    | High volume  |

**Credits = Characters** (roughly 1:1)

- 100,000 chars ≈ 16 hours of speech (at ~100 chars/minute spoken)
- Average response: 200-500 chars (2-5 minutes of audio)
- **200 responses/day** = 30k-100k chars/month → **Creator tier**

**Cost Optimization:**

- Use Flash v2.5 model (cheaper than Multilingual v2)
- Cache common responses (greetings, FAQs)
- Text-first, voice-optional (let users choose)
- Batch processing where possible

### Implementation

**Step 1: Get API Key**

```bash
export ELEVENLABS_API_KEY="your_key_here"
```

**Step 2: Choose/Clone a Voice**

- Option A: Use premade voice from library (3,000+ options)
- Option B: Clone Arvind's voice (Professional Voice Cloning)
- Option C: Design custom voice ("warm, professional, empathetic")

**Recommendation:** Start with premade voice "Aria" (empathetic female) or "Adam" (professional male). Clone later if needed.

**Step 3: Basic TTS Call**

```javascript
const ElevenLabs = require("elevenlabs-node");

const voice = new ElevenLabs({
  apiKey: process.env.ELEVENLABS_API_KEY,
  voiceId: "21m00Tcm4TlvDq8ikWAM", // Rachel voice
});

async function textToSpeech(text) {
  const audio = await voice.textToSpeech({
    text: text,
    modelId: "eleven_flash_v2_5", // Ultra-low latency
    voice_settings: {
      stability: 0.5,
      similarity_boost: 0.75,
    },
  });

  return audio; // Returns audio buffer (MP3)
}
```

**Step 4: Send to Telegram**

```javascript
bot.on("text", async (ctx) => {
  const responseText = "Hello! How can I assist you today?";

  // Send text response
  await ctx.reply(responseText);

  // ALSO send voice version
  const audioBuffer = await textToSpeech(responseText);
  await ctx.replyWithVoice({ source: audioBuffer });
});
```

### Voice Quality Settings

**For Home Health (Copper AI):**

```javascript
{
  stability: 0.6,        // More consistent (less variation)
  similarity_boost: 0.8, // Closer to original voice
  style: 0.3,            // Moderate expressiveness
  use_speaker_boost: true // Enhance clarity
}
```

**For Emotional Delivery:**

```javascript
{
  stability: 0.4,        // Allow more variation
  similarity_boost: 0.7,
  style: 0.7,            // High expressiveness
  use_speaker_boost: false
}
```

**Prompting for Emotion:**
ElevenLabs models respond to textual cues:

```
"I'm so sorry to hear that!" → Empathetic tone
"Great news! Your appointment is confirmed." → Upbeat
"Please take your medication now." → Calm, instructive
```

Add context in parentheses (not spoken but influences tone):

```
"(warmly) Hello, Mrs. Johnson. How are you feeling today?"
```

### Supported Audio Formats

**For Telegram:**

- `.ogg` (Opus) - Recommended (Telegram native)
- `.mp3` - Also works
- `.m4a` - Less common

**ElevenLabs Output Formats:**

```javascript
output_format: "mp3_44100_128"; // 44.1kHz, 128kbps MP3
output_format: "pcm_44100"; // PCM (highest quality)
output_format: "ulaw_8000"; // Telephony (8kHz μ-law)
```

**Recommendation:** Use `mp3_44100_128` for Telegram (good quality, small file size).

---

## 🏗️ Part 3: Integration Architecture

### System Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     COPPER AI TELEGRAM BOT                    │
└───────────────────┬──────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│ Voice   │   │  Text    │   │  Media   │
│ Handler │   │ Handler  │   │ Handler  │
└────┬────┘   └────┬─────┘   └────┬─────┘
     │             │               │
     ▼             ▼               ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│ Whisper │   │ Copper   │   │ Storage  │
│   API   │   │   AI     │   │  (S3)    │
└────┬────┘   │  Engine  │   └──────────┘
     │        └────┬─────┘
     └─────────────┤
                   ▼
          ┌─────────────────┐
          │  Response Gen   │
          └────────┬────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
  ┌───────────┐        ┌──────────┐
  │ Text Msg  │        │  Voice   │
  └───────────┘        │  (11Labs)│
                       └──────────┘
```

### Database Schema

**Users Table:**

```sql
CREATE TABLE telegram_users (
  id SERIAL PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username VARCHAR(255),
  first_name VARCHAR(255),
  role VARCHAR(50), -- 'caregiver', 'patient', 'admin'
  agency_id INT REFERENCES agencies(id),
  phone VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW(),
  last_active TIMESTAMP
);
```

**Messages Table (Logging):**

```sql
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES telegram_users(id),
  message_type VARCHAR(20), -- 'text', 'voice', 'photo'
  direction VARCHAR(10), -- 'inbound', 'outbound'
  content_text TEXT,
  file_id VARCHAR(255), -- Telegram file ID
  transcription TEXT,
  processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Conversations Table (Context):**

```sql
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES telegram_users(id),
  context JSONB, -- Store conversation state
  last_message_at TIMESTAMP,
  status VARCHAR(20) -- 'active', 'closed'
);
```

### Security & Compliance

**HIPAA Requirements:**

1. ✅ **Encryption in Transit:** Telegram uses MTProto (encrypted)
2. ✅ **Encryption at Rest:** Encrypt PHI in database (PGP/AES-256)
3. ✅ **Access Controls:** Role-based permissions
4. ✅ **Audit Logs:** Log all message activity
5. ✅ **Business Associate Agreement (BAA):** Telegram does NOT sign BAAs
   - **Workaround:** Use Telegram for non-PHI only (alerts, reminders)
   - For PHI: Redirect to secure portal/voice call

**Data Retention:**

- Messages: 90 days (HIPAA requirement)
- Voice files: Delete after transcription (or 30 days)
- Transcripts: Encrypted storage, 6 years (state requirements vary)

**User Authentication:**

```javascript
bot.use(async (ctx, next) => {
  const user = await db.getUserByTelegramId(ctx.from.id);

  if (!user) {
    return ctx.reply("Unauthorized. Please contact your administrator.");
  }

  ctx.user = user; // Attach to context
  return next();
});
```

---

## 🚀 Part 4: MVP Implementation Plan

### Phase 1: Basic Bot (Week 1)

- [ ] Set up Telegram bot (BotFather)
- [ ] Node.js server with Telegraf
- [ ] Basic text commands (`/start`, `/help`, `/status`)
- [ ] Database setup (Postgres)
- [ ] User registration flow
- [ ] Deploy to production (Render/Railway/DigitalOcean)

**Deliverables:**

- Working Telegram bot responding to text
- User authentication
- Command help system

### Phase 2: Voice Input (Week 2)

- [ ] Voice message handler
- [ ] OpenAI Whisper API integration
- [ ] Download → Transcribe → Process pipeline
- [ ] Store transcripts
- [ ] Test with Spanish/English (multilingual)

**Deliverables:**

- Voice messages auto-transcribed
- Text responses to voice input
- Logging system

### Phase 3: Voice Output (Week 2-3)

- [ ] ElevenLabs API integration
- [ ] Select/clone voice
- [ ] TTS response generation
- [ ] Send voice notes to users
- [ ] A/B test voice vs text preferences

**Deliverables:**

- Voice responses working
- Toggle for voice/text preference
- Cost monitoring

### Phase 4: Copper AI Integration (Week 3)

- [ ] Connect to existing Copper AI logic
- [ ] Patient data lookup
- [ ] Caregiver task management
- [ ] Scheduling integration
- [ ] Alert system

**Deliverables:**

- Full integration with Copper AI platform
- Real workflows (visit confirmation, status updates)
- Admin dashboard

### Phase 5: Polish & Launch (Week 3+)

- [ ] Error handling & retries
- [ ] Rate limiting (prevent abuse)
- [ ] Analytics (usage tracking)
- [ ] User feedback system
- [ ] Documentation

---

## 💰 Cost Analysis

### Monthly Operating Costs (MVP - 10 agencies, 50 caregivers)

| Service                 | Tier            | Monthly Cost     | Notes                           |
| ----------------------- | --------------- | ---------------- | ------------------------------- |
| **Telegram Bot API**    | Free            | $0               | Unlimited messages              |
| **OpenAI Whisper API**  | Pay-as-you-go   | ~$20             | 3,000 min/month @ $0.006/min    |
| **ElevenLabs TTS**      | Creator         | $22              | 100k chars (~200 responses/day) |
| **Hosting (Node.js)**   | Render/Railway  | $7-20            | 512MB-1GB RAM                   |
| **Database (Postgres)** | Render/Supabase | $10-15           | 1GB storage                     |
| **Storage (S3)**        | AWS             | $5               | Audio file storage (temp)       |
| **Total**               |                 | **$64-82/month** | Scales with usage               |

### Cost at Scale (100 agencies, 500 caregivers)

| Service            | Monthly Cost   | Notes              |
| ------------------ | -------------- | ------------------ |
| **Whisper API**    | ~$180          | 30,000 min/month   |
| **ElevenLabs TTS** | $99 (Pro)      | 100k credits       |
| **Hosting**        | $25            | 2GB RAM            |
| **Database**       | $25            | 10GB storage       |
| **Storage**        | $15            | Larger audio cache |
| **Total**          | **$344/month** |                    |

**Per-Agency Cost:** $3.44/month (very affordable!)

---

## 📊 Success Metrics

**Technical:**

- Message delivery rate > 99%
- Transcription accuracy > 95%
- TTS response time < 3 seconds
- Bot uptime > 99.5%

**Business:**

- Caregiver adoption rate (% using bot)
- Messages per caregiver per day
- Voice vs text preference ratio
- Time saved vs phone calls
- User satisfaction (NPS)

---

## 🔧 Development Tools & Resources

**NPM Packages:**

```json
{
  "dependencies": {
    "telegraf": "^4.x",
    "axios": "^1.x",
    "form-data": "^4.x",
    "pg": "^8.x",
    "dotenv": "^16.x",
    "elevenlabs-node": "^1.x"
  }
}
```

**Telegram Bot Setup:**

1. Message @BotFather on Telegram
2. `/newbot` → Choose name
3. Get API token → `TELEGRAM_BOT_TOKEN`
4. Set commands with `/setcommands`

**Webhook vs Polling:**

- **Polling (Easy):** `bot.launch()` - Good for MVP
- **Webhook (Production):** Requires HTTPS endpoint - More scalable

**Testing:**

```javascript
// Test transcription
node scripts/test-whisper.js sample-voice.ogg

// Test TTS
node scripts/test-elevenlabs.js "Hello, this is a test."

// Test bot locally
node bot.js
```

---

## 🎯 Next Steps for Nike

1. **Create Proof of Concept (2-3 days):**
   - Basic Telegram bot
   - Text command handling
   - Voice transcription demo
   - TTS response demo

2. **Present to Arvind:**
   - Live demo via Telegram
   - Cost breakdown
   - Timeline estimate

3. **Build MVP (2-3 weeks if approved):**
   - Full implementation per plan above
   - Deploy to production
   - Onboard first agency for beta

4. **Document Everything:**
   - API docs
   - User guides
   - Admin dashboard

---

## ✅ Task Completion Summary

This document addresses **task-016** (Copper AI Telegram bot setup) and **task-017** (Voice/TTS for Copper AI bot).

**Deliverables:**

- ✅ Complete technical architecture
- ✅ ElevenLabs integration plan
- ✅ Telegram Bot API research
- ✅ Cost analysis
- ✅ Implementation timeline
- ✅ HIPAA compliance notes
- ✅ MVP roadmap

**Status:** READY FOR DEVELOPMENT

**Next Action:** Arvind to approve → Nike builds POC → Demo → Production

---

_Nike's note: This is a POWERFUL addition to Copper AI. Voice-first interface is perfect for caregivers on the go. I can build this! 🐾_

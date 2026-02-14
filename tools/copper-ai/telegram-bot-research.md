# Telegram Bot for Copper AI - Research & Implementation Plan

**Prepared by:** Nike 🐾  
**Date:** Feb 1, 2026  
**Purpose:** Enable Copper AI voice agent demos via Telegram

---

## 🎯 Why Telegram for Copper AI?

### Use Cases:

1. **Quick Demos** - Share bot link, prospects can test immediately
2. **HIPAA-Safe Testing** - Test with synthetic data before real PHI
3. **International Reach** - Telegram popular in India, Middle East
4. **Rich Media** - Send voice notes, transcripts, call summaries
5. **Always Available** - 24/7 bot for lead qualification

### Perfect For:

- ✅ Demo scheduling ("Book a demo with our AI")
- ✅ Voice message → AI response (showcase TTS/STT)
- ✅ FAQ answering about Copper AI features
- ✅ Lead qualification ("What's your agency size?")
- ✅ Appointment reminders for home health agencies

---

## 🔧 Technical Stack

### Best Framework: Telegraf

**Why Telegraf?**

- ✅ Modern, actively maintained (2026)
- ✅ TypeScript support
- ✅ Middleware architecture
- ✅ Great docs
- ✅ Built-in session management

```bash
npm install telegraf
```

**Alternative:** `node-telegram-bot-api` (older, but stable)

### Architecture:

```
User → Telegram → Bot API → Telegraf
                             ↓
                    Copper AI Voice Engine
                             ↓
                    Response → Telegram
```

---

## 📋 Setup Steps

### 1. Create Bot with BotFather

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Choose name: "Copper AI Demo Bot"
4. Choose username: `@CopperAIBot` (or similar)
5. **Get API token** - Save this securely!

### 2. Basic Bot Structure

```javascript
// bot.js
const { Telegraf } = require("telegraf");
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Welcome message
bot.start((ctx) => {
  ctx.reply(`
👋 Welcome to Copper AI!

I'm your AI voice assistant for home health agencies.

Try me out:
• Send a voice message
• Ask about our features
• Book a demo
• Get pricing info
  `);
});

// Handle voice messages
bot.on("voice", async (ctx) => {
  const fileId = ctx.message.voice.file_id;

  // 1. Download voice file
  const fileLink = await ctx.telegram.getFileLink(fileId);

  // 2. Transcribe with Whisper
  const transcript = await transcribeAudio(fileLink);

  // 3. Process with Copper AI
  const response = await copperAI.process(transcript);

  // 4. Convert to speech
  const audioUrl = await generateVoice(response);

  // 5. Send back
  ctx.replyWithVoice({ url: audioUrl });
  ctx.reply(response); // Also send text
});

// Feature inquiry
bot.command("features", (ctx) => {
  ctx.reply(`
🎯 Copper AI Features:

✅ AI Voice Agents for Home Health
✅ HIPAA Compliant
✅ 24/7 Appointment Scheduling
✅ Automated Patient Follow-ups
✅ Visit Confirmations & Reminders
✅ Multi-language Support
✅ Integration with existing EMRs

Price: Starting at $0.05/min
ROI: Save $3,000-5,000/month on staffing

Want a demo? Type /demo
  `);
});

// Demo booking
bot.command("demo", (ctx) => {
  ctx.reply(`
📅 Book Your Copper AI Demo

Choose a time:
1️⃣ Tomorrow 10 AM CST
2️⃣ Tomorrow 2 PM CST
3️⃣ Friday 11 AM CST
4️⃣ Custom time

Reply with the number (1-4)
  `);
});

bot.launch();
console.log("Copper AI Bot is running! 🤖");
```

---

## 🎙️ Voice Message Flow

### User Journey:

1. **User sends voice:** "How much does Copper AI cost?"
2. **Bot transcribes** (Whisper API)
3. **Bot processes** (GPT-4 + Copper AI context)
4. **Bot generates voice** (ElevenLabs)
5. **Bot sends audio + text** back

### Implementation:

```javascript
const OpenAI = require("openai");
const axios = require("axios");

async function transcribeAudio(audioUrl) {
  const openai = new OpenAI();

  // Download audio
  const response = await axios.get(audioUrl, { responseType: "arraybuffer" });
  const audioBuffer = Buffer.from(response.data);

  // Transcribe
  const transcription = await openai.audio.transcriptions.create({
    file: audioBuffer,
    model: "whisper-1",
  });

  return transcription.text;
}

async function generateVoice(text) {
  const response = await axios.post(
    "https://api.elevenlabs.io/v1/text-to-speech/VOICE_ID",
    {
      text: text,
      model_id: "eleven_multilingual_v2",
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75,
      },
    },
    {
      headers: {
        "xi-api-key": process.env.ELEVENLABS_API_KEY,
      },
      responseType: "arraybuffer",
    },
  );

  // Save to temp file and return URL
  return saveAndGetUrl(response.data);
}
```

---

## 💡 Bot Commands

### Essential Commands:

- `/start` - Welcome message
- `/features` - List Copper AI capabilities
- `/pricing` - Pricing breakdown vs competitors
- `/demo` - Schedule a demo
- `/roi` - ROI calculator
- `/help` - How to use the bot
- `/talk` - Initiate voice conversation

### Admin Commands (for Arvind):

- `/stats` - Bot usage statistics
- `/leads` - New leads from bot
- `/broadcast` - Send message to all users

---

## 📊 Lead Tracking

### Capture Data:

```javascript
const leads = [];

bot.on("message", (ctx) => {
  const user = ctx.from;

  // Track interaction
  const lead = {
    telegram_id: user.id,
    username: user.username,
    first_name: user.first_name,
    last_name: user.last_name,
    timestamp: new Date(),
    messages: [],
  };

  // Save to database or Airtable
  saveLead(lead);
});
```

---

## 🔐 Security & Compliance

### HIPAA Considerations:

- ❌ **Don't** collect PHI via Telegram
- ✅ **Do** use for demos with synthetic data
- ✅ **Do** include disclaimer: "Demo only - not for real patient data"
- ✅ **Do** encrypt all data at rest
- ✅ **Do** log all interactions for audit

### Bot Privacy:

```javascript
bot.start((ctx) => {
  ctx.reply(`
⚠️ Privacy Notice:

This is a DEMO bot for Copper AI.
• Do not share real patient information
• Conversations are logged for quality
• We comply with HIPAA for production systems

By continuing, you agree to our demo terms.
  `);
});
```

---

## 🚀 Deployment

### Option 1: AWS Lambda (Recommended)

- Serverless, auto-scaling
- Pay per use
- Easy to integrate with other AWS services

### Option 2: Heroku

- Simple deployment
- Good for MVP
- Free tier available

### Option 3: VPS (DigitalOcean, etc.)

- More control
- Keep running 24/7
- Need to manage yourself

---

## 💰 Costs

### Bot Hosting:

- **AWS Lambda:** ~$5-20/month (depending on usage)
- **Heroku:** Free - $25/month
- **VPS:** $10-20/month

### API Costs (per demo):

- **Whisper (transcription):** ~$0.006/min
- **GPT-4 (processing):** ~$0.03/interaction
- **ElevenLabs (TTS):** ~$0.30/1000 chars (~$0.05/response)

**Total cost per demo interaction:** ~$0.10

**With 100 demos/month:** ~$10 in API costs + hosting = **$20-30/month total**

---

## 📈 Success Metrics

### Track:

1. **Engagement:** How many users start the bot
2. **Conversion:** How many book demos
3. **Voice usage:** How many send voice messages
4. **Drop-off:** Where users leave the conversation
5. **Lead quality:** Which leads convert to sales

### Dashboard:

```javascript
bot.command("stats", async (ctx) => {
  if (ctx.from.id !== ARVIND_TELEGRAM_ID) return;

  ctx.reply(`
📊 Copper AI Bot Stats

Users: 47
Demo Requests: 12
Voice Messages: 23
Conversion Rate: 25.5%

Top Questions:
1. Pricing (18x)
2. HIPAA Compliance (12x)
3. Integration options (9x)
  `);
});
```

---

## 🎯 Next Steps for Nike

### Phase 1: MVP (2-3 hours)

1. ✅ Create bot with BotFather
2. ✅ Set up basic commands (`/start`, `/features`, `/demo`)
3. ✅ Deploy to Heroku
4. ✅ Test with Arvind

### Phase 2: Voice Integration (3-5 hours)

1. ✅ Integrate Whisper for transcription
2. ✅ Integrate ElevenLabs for TTS
3. ✅ Create natural conversation flow
4. ✅ Test voice quality

### Phase 3: Lead Tracking (2-3 hours)

1. ✅ Set up database (Airtable or MongoDB)
2. ✅ Capture user info and interactions
3. ✅ Build admin dashboard
4. ✅ Set up alerts for new leads

### Phase 4: Advanced Features (ongoing)

1. ✅ Multi-language support
2. ✅ Integration with Copper AI CRM
3. ✅ Automated follow-ups
4. ✅ A/B testing different responses

---

## 🐾 Nike's Take

**This is a GREAT marketing tool for Copper AI!**

**Why?**

- Zero friction for prospects (just click link)
- Show off voice AI capabilities instantly
- 24/7 lead gen while you sleep
- Low cost (~$30/month)
- International reach (Telegram huge in India)

**When to build?**

- **Now** if you want a quick demo tool
- **After website** if you want to focus on web first
- **With sales push** when you're ramping outbound

**Estimated build time:** 1-2 days for Nike to build MVP

---

**Ready to build?** Let Nike know! 🐾

Resources saved to:

- `/copper-ai/telegram-bot-research.md`
- Code snippets ready to go
- Can have MVP running in 24 hours!

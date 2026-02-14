# TTS & Voice Providers Comparison (2026)

_Research compiled: January 31, 2026_

## Overview

This document compares Text-to-Speech (TTS) providers for voice agent applications like Copper AI.

## Providers Comparison

### 1. fish.audio 🐟

**Website:** https://fish.audio  
**Docs:** https://docs.fish.audio

**Pricing:**

- TTS: **$15 per million UTF-8 bytes**
- ASR (Speech-to-Text): **$0.36 per audio hour**
- Pay-as-you-go, no subscriptions

**Features:**

- High-quality natural voices
- Voice cloning support
- Multiple languages
- API + WebSocket streaming
- Latency modes: low, normal, balanced
- Prosody control (speed, volume)
- Temperature control (expressiveness)

**Pros:**

- Competitive pricing (50% cheaper than ElevenLabs)
- Good quality
- Simple API
- Voice cloning included

**Cons:**

- Newer player (less established)
- Smaller voice library than competitors

**Best for:** Cost-conscious production apps, voice agents

---

### 2. ElevenLabs 🔊

**Website:** https://elevenlabs.io  
**Pricing:** https://elevenlabs.io/pricing/api

**Pricing:**

- TTS: **~$0.30 per 1K characters** (minute-based: $0.18-0.30/min depending on tier)
- Tiered pricing based on volume
- Flash model: Cheaper ($0.06-0.15/min)

**Features:**

- Outstanding voice quality (industry-leading)
- Large voice library
- Advanced voice cloning
- Multiple models (V1, V2, V3, Flash)
- Multilingual support
- Emotion & style control

**Pros:**

- Best quality in the industry
- Most natural-sounding
- Great for production/premium apps

**Cons:**

- Most expensive option
- Can be slower than alternatives

**Best for:** Premium applications where quality matters most

---

### 3. OpenAI TTS 🤖

**Website:** https://platform.openai.com  
**Docs:** https://platform.openai.com/docs/pricing

**Pricing:**

- **gpt-4o-mini-tts:** $0.60/million input chars + $12/million audio tokens
- **TTS:** $15/million characters
- **TTS HD:** $30/million characters
- **Whisper (STT):** $0.006/minute

**Features:**

- Multiple voice options (alloy, ash, coral, echo, fable, onyx, nova, sage, shimmer)
- Fast generation
- Good quality
- Part of larger OpenAI ecosystem

**Pros:**

- **Cheapest paid option** (gpt-4o-mini-tts: $0.0006/1K chars)
- Fast
- Reliable infrastructure
- Easy integration with other OpenAI services

**Cons:**

- Limited voice customization
- No voice cloning
- Less expressive than ElevenLabs

**Best for:** High-volume production apps, cost optimization

---

### 4. Microsoft Edge TTS (Free) 🆓

**Integration:** node-edge-tts package

**Pricing:**

- **FREE**

**Features:**

- Multiple voices (200+)
- Multilingual
- SSML support
- Prosody control (rate, pitch, volume)

**Pros:**

- Completely free
- Good quality for free option
- Many voices available
- Fast

**Cons:**

- Limited compared to paid options
- Less natural than premium providers
- May have usage limits

**Best for:** Development, testing, free tier apps

---

## Cost Comparison (450 characters)

| Provider                   | Cost     | Relative | Quality     | Speed  |
| -------------------------- | -------- | -------- | ----------- | ------ |
| **Edge TTS**               | $0.00    | FREE     | Good        | Fast   |
| **OpenAI gpt-4o-mini-tts** | $0.00027 | 1x       | Very Good   | Fast   |
| **fish.audio**             | $0.0081  | 30x      | Excellent   | Fast   |
| **ElevenLabs**             | $0.135   | 500x     | Outstanding | Medium |

## Recommendations by Use Case

### For Copper AI (Home Health Voice Agents)

**Development/Testing:**

- Use **Edge TTS** (free)

**Production (High Volume):**

- Use **OpenAI gpt-4o-mini-tts** (cheapest: $0.60/million chars)
- Estimated cost: ~$0.03 per 50-call day (assuming 100 chars/call average)

**Production (Balanced):**

- Use **fish.audio** ($15/million bytes)
- Estimated cost: ~$0.45 per 50-call day
- 30x cheaper than ElevenLabs!

**Premium/Demo:**

- Use **ElevenLabs** for highest quality
- Estimated cost: ~$6.75 per 50-call day

### Two-Way Voice Agent Stack

**Recommended Stack:**

1. **STT (Speech-to-Text):**
   - OpenAI Whisper ($0.006/min) ✅ Best value
   - fish.audio ASR ($0.36/hour) - Alternative

2. **TTS (Text-to-Speech):**
   - OpenAI gpt-4o-mini-tts (production)
   - fish.audio (balanced quality/cost)

3. **Voice Activity Detection (VAD):**
   - Silero VAD (open source, free)
   - WebRTC VAD

4. **Telephony:**
   - Twilio (for phone calls)
   - WebRTC (for in-app)

**Estimated Cost per 10-minute call:**

- STT: $0.06 (Whisper)
- TTS: ~$0.02-0.05 (assuming 200 words spoken by AI)
- **Total: ~$0.08-0.11 per 10-min call**

## Implementation Notes

### Integration Pattern

All providers follow similar pattern:

```typescript
async function textToSpeech(params: {
  text: string;
  provider: "fish" | "openai" | "elevenlabs" | "edge";
  config: ProviderConfig;
}): Promise<Buffer> {
  // API call
  // Return audio buffer
}
```

### Fallback Strategy

Implement provider fallback for reliability:

1. Try primary provider (e.g., fish.audio)
2. Fallback to OpenAI
3. Fallback to Edge (free)

### Cost Tracking

Track costs per call for analytics:

- Characters sent
- Provider used
- Estimated cost
- Actual latency

## API Comparison

### fish.audio API

```bash
curl -X POST https://api.fish.audio/v1/tts \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "reference_id": "voice_id",
    "format": "mp3",
    "prosody": {"speed": 1.0, "volume": 0}
  }'
```

### OpenAI API

```bash
curl -X POST https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini-tts",
    "input": "Hello world",
    "voice": "alloy",
    "response_format": "mp3"
  }'
```

### ElevenLabs API

```bash
curl -X POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id} \
  -H "xi-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.75,
      "speed": 1.0
    }
  }'
```

## Future Considerations

### Emerging Providers

- **Cartesia** - Real-time voice streaming
- **PlayHT** - Voice cloning focus
- **Murf.ai** - Studio-grade voices
- **Resemble.ai** - Enterprise focus

### Technology Trends

- WebSocket streaming becoming standard
- Real-time latency <300ms achievable
- Voice cloning becoming commoditized
- Costs trending downward

## Sources

- fish.audio docs: https://docs.fish.audio/
- OpenAI pricing: https://platform.openai.com/docs/pricing
- ElevenLabs pricing: https://elevenlabs.io/pricing/api
- Personal testing & implementation (Jan 2026)

---

_Last updated: January 31, 2026_  
_Researcher: Nike (AI Assistant)_

# TTS (Text-to-Speech) Formatting Guidelines

The `tts_script` field defines the audio sequence for each listening question. It is designed for use with **Google Gemini TTS API** (`gemini-2.5-flash-preview-tts`).

## Voice Mapping

Each voice ID in the tts_script maps to a Gemini prebuilt voice:

| Our Voice ID | Gemini Voice | Character | Description |
|-------------|-------------|-----------|-------------|
| `Intro_Voice` | **Kore** | Formal narrator | Firm, clear — reads intro and repeats question |
| `Male_1` | **Puck** | Young male | Upbeat, natural — main male speaker |
| `Female_1` | **Zephyr** | Young female | Bright, polite — main female speaker |

> Voice gallery: test all 30 Gemini voices at [AI Studio Voice Library](https://aistudio.google.com)

## Entry Types

The `tts_script` array contains two types of entries. They must NOT be mixed in a single object:

### 1. Voice Entry
Contains `voice` and `text` fields. The `text` is the Japanese sentence to be spoken.
```json
{ "voice": "Male_1", "text": "すみません、このかばんはいくらですか。" }
```

### 2. Break Entry
Contains only a `break` field with the pause duration.
```json
{ "break": "1s" }
```

## Timing Rules
- **After intro:** `{ "break": "1s" }`
- **Between speakers (turn-taking):** `{ "break": "0.5s" }`
- **Before question repeat:** `{ "break": "1s" }`

## Required Flow

Every question must follow this exact sequence:
1. Intro (Intro_Voice) — sets the scene
2. Break (1s)
3. Dialogue lines — alternating speakers with 0.5s breaks between them
4. Break (1s)
5. Question repeat (Intro_Voice) — same as the question in intro or a separate question

## Complete Example

```json
{
  "tts_script": [
    { "voice": "Intro_Voice", "text": "おとこのひとと おんなのひとが はなしています。ふたりは なにを かいますか。" },
    { "break": "1s" },
    { "voice": "Male_1", "text": "おべんとうを かいましょう。" },
    { "break": "0.5s" },
    { "voice": "Female_1", "text": "おべんとうは たかいですね。おにぎりは どうですか。" },
    { "break": "0.5s" },
    { "voice": "Male_1", "text": "いいですね。おにぎりを かいましょう。" },
    { "break": "1s" },
    { "voice": "Intro_Voice", "text": "ふたりは なにを かいますか。" }
  ]
}
```

## Audio Generation Pipeline

The `generate_tts_audio.py` script processes the tts_script as follows:

```
tts_script entry          →  Action              →  Output
─────────────────────────────────────────────────────────────
{ voice, text }           →  Gemini API call      →  PCM audio bytes
{ break: "1s" }           →  Generate silence     →  Silent PCM bytes
─────────────────────────────────────────────────────────────
All segments concatenated →  Write WAV file       →  final.wav
```

**Technical specs:** 24kHz sample rate, 16-bit PCM, mono channel.

### Usage
```bash
# Set API key
export GEMINI_API_KEY='your-key-here'

# Generate audio from question JSON
python backend/listening/scripts/generate_tts_audio.py backend/listening/data/n5_listening_img_001.json

# Custom output path
python backend/listening/scripts/generate_tts_audio.py question.json --output audio/q001.wav
```

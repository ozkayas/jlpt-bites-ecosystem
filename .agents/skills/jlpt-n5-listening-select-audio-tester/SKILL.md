---
name: jlpt-n5-listening-select-audio-tester
description: "Validate JLPT N5 Listening Mondai 3 (発話表現 / selectAudio) derived-data.json files. Performs 6 passes: (1) mechanical schema validation via script, (2) semantic/linguistic N5-level review, (3) TTS script generation, (4) Imagen 3 image generation, (5) Gemini TTS audio generation, (6) final question.json build. Use when the user asks to 'selectAudio test et', 'derived-data doğrula', 'expression question test', or after generating a question with the select-audio-creator skill."
---

# JLPT N5 Listening Select Audio Tester (Mondai 3 / 発話表現)

Validate a `derived-data.json` for the selectAudio module using a six-pass pipeline: mechanical validation, semantic review, TTS script generation, Imagen 3 image generation, Gemini TTS audio generation, and final `question.json` build.

## Input

```
backend/listening/data/selectAudio/
  {id}/
    derived-data.json    ← Input (produced by select-audio-creator skill)
```

The user specifies either a folder ID (e.g. `002`) or a full path.

---

## Pass 1 — Mechanical Validation (Script)

```bash
python3 .agents/skills/jlpt-n5-listening-select-audio-tester/scripts/validate_derived_data.py \
  backend/listening/data/selectAudio/{id}/derived-data.json
```

### Checks (10 checks)

| # | Check | Rule |
|---|-------|------|
| 1 | `source_clip` | Present and non-empty string |
| 2 | `metadata.level` | `"N5"` (uppercase) |
| 3 | `metadata.topic` | Object with `ja` + all 6 UI lang keys (tr, en, de, fr, es, ko) |
| 4 | `correct_option` | Integer **0, 1, or 2** |
| 5 | `transcriptions.ja.intro` | Present, >10 chars, ends with `か。` |
| 6 | `transcriptions.ja.options` | Exactly 3 items; each has `number` (1/2/3) and non-empty `text` |
| 7 | `transcriptions.ja.question` | Present, >5 chars, ends with `か。` |
| 8 | All 7 lang keys present in `transcriptions` | ja + tr + en + de + fr + es + ko |
| 9 | `analysis.vocabulary` | ≥2 items; each has `word`, `reading`, `meanings` (object) |
| 10 | `image_prompt` | Present and non-empty string |

**If any FAIL:** Stop. Report errors. Fix the JSON. Re-run Pass 1.
**If PASS:** Proceed to Pass 2.

---

## Pass 2 — Semantic / Linguistic Review (Claude)

Read `derived-data.json` and check each criterion:

### 2.1 — N5 Level Appropriateness
- All text in `transcriptions.ja.intro`, `options[].text`, and `question` must use N5 vocabulary and grammar.
- No N4+ vocabulary. No complex conjugations beyond N5.
- **Check:** Any word or pattern above N5?

### 2.2 — Correct Option Validity
- `transcriptions.ja.options[correct_option].text` must be the natural, appropriate thing for the arrow character to say in the described situation.
- **Check:** Is the marked correct option actually the best answer for the scenario?

### 2.3 — Distractor Plausibility (Trap Quality)
- Each wrong option must use one of the 4 trap types: Rol Karışıklığı, Yön Karışıklığı, Register Karışıklığı, Bağlam Karışıklığı.
- Distractors must be plausible enough to trick a careless learner.
- **Check:** Does each distractor have a clear, identifiable trap type? Is it plausible?

### 2.4 — Options Naturalness
- All 3 Japanese options must be natural utterances.
- Options should be parallel in structure and speech register.
- Intro must correctly describe the situation in N5 Japanese.
- **Check:** Does every option sound like something a real person would say?

### 2.5 — Translation Accuracy (6 Languages)
- `transcriptions.tr/en/de/fr/es/ko` must accurately reflect the Japanese intro, options, and question.
- Speaker role (customer, student, etc.) must be preserved in translation.
- **Check:** Are all 6 translations accurate and natural?

### 2.6 — Logic Explanation Quality
- `logic.tr` and `logic.en` must explain why the correct option is right.
- Must explain why each distractor is wrong (name the trap type).
- **Check:** Are the logic explanations accurate, complete, and clear?

### Output Format for Pass 2

```
Pass 2 — Semantic Review for {id}
  2.1 N5 Level:           ✅ PASS / ❌ FAIL (details)
  2.2 Correct Option:     ✅ PASS / ❌ FAIL (details)
  2.3 Distractor Quality: ✅ PASS / ❌ FAIL (trap types identified)
  2.4 Naturalness:        ✅ PASS / ⚠️ WARN (details)
  2.5 Translations:       ✅ PASS / ❌ FAIL (details)
  2.6 Logic Quality:      ✅ PASS / ❌ FAIL (details)
```

**If any 2.1–2.3 FAIL:** Stop. Report issues. Suggest fixes. Re-run after fixing.
**If PASS or only WARNs:** Proceed to Pass 3.

---

## Pass 3 — TTS Script Generation

Generate `tts_script.json` in the same folder.

### Speaker Voice Rules

Determine the arrow character's gender by reading the image (or ask the user if ambiguous):

| Arrow Character | Voice ID | Gemini Voice |
|----------------|----------|-------------|
| Narrator (intro + question) | `Intro_Voice` | Kore |
| Male character | `Male_1` | Puck |
| Female character | `Female_1` | Zephyr |

### TTS Script Structure

```json
{
  "tts_script": [
    { "voice": "Intro_Voice", "text": "<transcriptions.ja.intro>" },
    { "break": "1s" },
    { "voice": "<Speaker_Voice>", "text": "１　<options[0].text>" },
    { "break": "0.8s" },
    { "voice": "<Speaker_Voice>", "text": "２　<options[1].text>" },
    { "break": "0.8s" },
    { "voice": "<Speaker_Voice>", "text": "３　<options[2].text>" },
    { "break": "1s" },
    { "voice": "Intro_Voice", "text": "<transcriptions.ja.question>" }
  ]
}
```

### Rules

1. `Intro_Voice` reads the intro and the question repeat.
2. `1s` break after intro.
3. The same `Speaker_Voice` (Male_1 or Female_1) reads ALL 3 options — they all come from the same character.
4. Prepend each option text with `１　`, `２　`, `３　` (full-width digits + space).
5. `0.8s` break between each option.
6. `1s` break before question repeat.
7. Text must be Japanese only.
8. Every entry has EITHER `{voice, text}` OR `{break}`, never both.

Save to: `backend/listening/data/selectAudio/{id}/tts_script.json`

**After saving:** Display the script to the user.

---

## Pass 4 — Image Generation (Imagen 3)

**NOTE:** The arrow is NOT added by this pass. The user adds it manually after image generation.

### Step 4.1 — Read image_prompt

Read `image_prompt` from `derived-data.json`.

### Step 4.2 — Generate image.png

> **STYLE RULE (MANDATORY):** All images must use the approved manga/textbook style.
> The `image_prompt` in `derived-data.json` should already follow this style.
> If it doesn't, rewrite it to include these required keywords:
> - `Simple manga-style line drawing, black and white`
> - `simple round head` (for each character)
> - `Cartoon style with simple round faces`
> - `clean outlines, white background, no shading, no color, no text, no arrows`
> - `Same style as JLPT N5 textbook manga illustrations`
>
> **AVOID:** `JLPT exam textbook line drawing` → produces realistic/Western faces (wrong style).

Use the generate_image script pattern adapted for selectAudio:

```bash
python3 -c "
import os, json, base64
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from google import genai
from google.genai import types

api_key = os.environ.get('JLPT_IMAGE_GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
if not api_key:
    raise ValueError('Set JLPT_IMAGE_GEMINI_API_KEY or GEMINI_API_KEY')

clip_dir = Path('backend/listening/data/selectAudio/{id}')
with open(clip_dir / 'derived-data.json') as f:
    data = json.load(f)

prompt = data['image_prompt']

client = genai.Client(api_key=api_key)
response = client.models.generate_images(
    model='imagen-4.0-fast-generate-001',
    prompt=prompt,
    config=types.GenerateImagesConfig(
        number_of_images=1,
        aspect_ratio='4:3',
        safety_filter_level='BLOCK_LOW_AND_ABOVE',
        person_generation='ALLOW_ADULT',
    )
)
img_bytes = response.generated_images[0].image.image_bytes
out = clip_dir / 'image.png'
out.write_bytes(img_bytes)
print(f'✓ Image saved: {out} ({len(img_bytes)//1024} KB)')
"
```

Replace `{id}` with the actual folder ID.

**Requires:** `JLPT_IMAGE_GEMINI_API_KEY` or `GEMINI_API_KEY` environment variable.

### Step 4.3 — Display image to user

Read `image.png` and display it. Ask the user:
> "Image generated. Please add an arrow pointing to the arrow character. Save the updated file as `image.png` in the same folder, then confirm to proceed to Pass 5."

**WAIT for user confirmation** before continuing to Pass 5.

---

## Pass 5 — Audio Generation (Gemini TTS)

Run the shared TTS generator with the `tts_script.json`:

```bash
python3 backend/listening/scripts/generate_tts_audio.py \
  backend/listening/data/selectAudio/{id}/tts_script.json \
  --output backend/listening/data/selectAudio/{id}/audio.mp3
```

**Note:** The TTS script uses `tts_script.json` as input (not `derived-data.json`) because `generate_tts_audio.py` reads a `tts_script` array from the input file. Pass the `tts_script.json` path.

**Requires:** `GEMINI_API_KEY` or `GEMINI_API_KEYS` environment variable.

**Output:** `audio.mp3` saved to the clip folder.

---

## Pass 6 — Build question.json

Merge `derived-data.json` fields into the final Fat JSON format. Strip internal fields.

```json
{
  "metadata": {
    "level": "N5",
    "topic": { <from derived-data.metadata.topic> }
  },
  "audio_url": null,
  "image_url": null,
  "correct_option": <from derived-data.correct_option>,
  "transcriptions": { <from derived-data.transcriptions> },
  "analysis": { <from derived-data.analysis> },
  "logic": { <from derived-data.logic> }
}
```

**Stripped fields** (internal only, not in final output):
- `source_clip`
- `image_prompt`

**Set to null** (filled later by upload script):
- `audio_url`
- `image_url`

Save to: `backend/listening/data/selectAudio/{id}/question.json`

**Display the final path and confirm completion.**

---

## Workflow Summary

```
User: "002 test et" / "selectAudio test et" / "derived-data doğrula"
  │
  ▼
Pass 1: python3 validate_derived_data.py backend/listening/data/selectAudio/{id}/derived-data.json
  │ FAIL? → Fix → Re-run
  ▼
Pass 2: Claude semantic review (N5 level, correct option, distractors, naturalness, translations, logic)
  │ FAIL? → Fix → Re-run
  ▼
Pass 3: Generate tts_script.json
  │
  ▼
Pass 4: Generate image.png via Imagen 3 → Display → WAIT for user to add arrow → Confirm
  │
  ▼
Pass 5: Generate audio.mp3 via Gemini TTS
  │
  ▼
Pass 6: Build question.json (strip internal fields, set audio_url/image_url to null)
  │
  ▼
Done. Report all pass results.
```

---

## Expected Output Structure

```
backend/listening/data/selectAudio/{id}/
  derived-data.json     ← Creator output (input to this skill)
  tts_script.json       ← Pass 3
  image.png             ← Pass 4 (user adds arrow manually)
  audio.mp3             ← Pass 5
  question.json         ← Pass 6 (final Fat JSON)
```

---

## Resources

| Resource | Purpose |
|----------|---------|
| `scripts/validate_derived_data.py` | Pass 1 mechanical validation script |
| `backend/listening/scripts/generate_tts_audio.py` | Pass 5 shared TTS generator |
| `backend/listening/data/selectAudio/001/question_data.json` | Legacy reference (2-language) |
| `.agents/skills/jlpt-n5-listening-variation-creator/scripts/generate_image.py` | Reference for Imagen 3 API pattern |

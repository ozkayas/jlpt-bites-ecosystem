# JLPT N5 Listening (Select Image) JSON Schema

The AI must output a single JSON object following this structure. All index values are **0-based**.

## Rules
- `id` must be unique, format: `n5_listening_img_{NNN}` (zero-padded, e.g. `n5_listening_img_001`)
- `level` must be lowercase `"n5"`
- `correct_option` is 0-indexed (0, 1, 2, or 3) — matches array position in `visual_prompts.options`
- `visual_prompts.options` must have exactly 4 items, each with 0-indexed `id` (0, 1, 2, 3)
- Exactly ONE option must have `logic_role: "Correct"`, the other three must be `"Distractor_A"`, `"Distractor_B"`, `"Distractor_C"`
- `tts_script` entries are either **voice objects** (`voice` + `text`) or **break objects** (`break` only) — never mixed
- All Japanese text in `transcription` must use only N5-level vocabulary and grammar

```json
{
  "id": "n5_listening_img_001",
  "metadata": {
    "level": "n5",
    "topic": "string (e.g., Shopping for lunch)",
    "pattern_used": "string (Reconsideration | Shortage | Attribute | Negative | Sequential | Location)"
  },
  "visual_prompts": {
    "master_style": "Minimalist black and white line art, Japanese language textbook illustration style, clean monochrome vector art, thick clean outlines, no shading, white background, simple character design, instructional clipart style, high contrast, no text",
    "options": [
      {
        "id": 0,
        "prompt": "A minimalist black and white line art illustration of [SUBJECT + DELTA], in the style of Japanese language textbook drawings. Simple clean outlines, monochrome, white background, no shading, high contrast.",
        "logic_role": "Correct"
      },
      { "id": 1, "prompt": "...", "logic_role": "Distractor_A" },
      { "id": 2, "prompt": "...", "logic_role": "Distractor_B" },
      { "id": 3, "prompt": "...", "logic_role": "Distractor_C" }
    ]
  },
  "correct_option": 0,
  "tts_script": [
    { "voice": "Intro_Voice", "text": "string (Introduction sentence)" },
    { "break": "1s" },
    { "voice": "Male_1", "text": "string (First speaker line)" },
    { "break": "0.5s" },
    { "voice": "Female_1", "text": "string (Second speaker line)" },
    { "break": "1s" },
    { "voice": "Intro_Voice", "text": "string (Question repeated)" }
  ],
  "transcription": {
    "intro": "string (Japanese introduction sentence)",
    "dialogue": [
      { "speaker": "string (e.g. Male_1)", "text": "string (Japanese dialogue line)" }
    ],
    "question": "string (Japanese question sentence)"
  },
  "translations": {
    "en": {
      "intro": "string",
      "dialogue": [
        { "speaker": "string", "text": "string" }
      ],
      "question": "string"
    },
    "tr": {
      "intro": "string",
      "dialogue": [
        { "speaker": "string", "text": "string" }
      ],
      "question": "string"
    }
  },
  "analysis": {
    "vocabulary": [
      { "word": "string (Japanese)", "reading": "string (hiragana)", "tr": "string", "en": "string" }
    ],
    "grammar": [
      { "point": "string (grammar pattern)", "tr": "string", "en": "string" }
    ]
  },
  "logic": {
    "tr": "string (Detailed Turkish explanation of why this is correct and why traps are traps)",
    "en": "string (Detailed English explanation)"
  }
}
```

## Field Details

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique question ID, format: `n5_listening_img_{NNN}` |
| `metadata.level` | string | Always `"n5"` (lowercase) |
| `metadata.topic` | string | Short topic description |
| `metadata.pattern_used` | string | One of: `Reconsideration`, `Shortage`, `Attribute`, `Negative`, `Sequential`, `Location` |
| `visual_prompts.master_style` | string | Fixed: monochrome JLPT textbook line art style (do not change) |
| `visual_prompts.options[].id` | number | 0-indexed option ID (0–3) |
| `visual_prompts.options[].prompt` | string | Image prompt: style prefix + subject + visual delta (monochrome, no color) |
| `visual_prompts.options[].logic_role` | string | `Correct` or `Distractor_A/B/C` |
| `correct_option` | number | 0-indexed, matches the `id` of the correct option |
| `tts_script[]` | object | Voice entry (`voice`+`text`) OR break entry (`break` only) |
| `transcription` | object | Japanese text of intro, dialogue, and question |
| `translations` | object | English and Turkish translations of the transcription |
| `analysis.vocabulary[]` | object | Key vocabulary with reading and bilingual meanings |
| `analysis.grammar[]` | object | Grammar points used, with bilingual explanations |
| `logic` | object | Turkish and English explanation of correct answer logic |

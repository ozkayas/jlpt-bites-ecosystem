# derived-data.json Schema

This file documents the exact structure of `derived-data.json` — the output produced by the `jlpt-n5-listening-variation-creator` skill.

---

## Full Schema

```json
{
  "source_clip": "clip_01_01m06s_02m06s",
  "metadata": {
    "level": "n5",
    "topic": "string — topic of the new variation (Japanese + English description)",
    "pattern_used": "Reconsideration | Shortage | Attribute | Negative | Sequential | Location"
  },
  "visual_prompts": {
    "options": [
      {
        "id": 0,
        "prompt": "Natural language Imagen 3 prompt for the correct answer...",
        "logic_role": "Correct"
      },
      {
        "id": 1,
        "prompt": "Natural language Imagen 3 prompt for distractor A...",
        "logic_role": "Distractor_A"
      },
      {
        "id": 2,
        "prompt": "Natural language Imagen 3 prompt for distractor B...",
        "logic_role": "Distractor_B"
      },
      {
        "id": 3,
        "prompt": "Natural language Imagen 3 prompt for distractor C...",
        "logic_role": "Distractor_C"
      }
    ]
  },
  "correct_option": 0,
  "tts_script": [
    { "voice": "Intro_Voice", "text": "Japanese intro sentence setting the scene and asking the question" },
    { "break": "1s" },
    { "voice": "Male_1", "text": "Japanese dialogue line" },
    { "break": "0.5s" },
    { "voice": "Female_1", "text": "Japanese dialogue line" },
    { "break": "0.5s" },
    { "voice": "Male_1", "text": "Japanese dialogue line" },
    { "break": "1s" },
    { "voice": "Intro_Voice", "text": "Japanese question repeated" }
  ],
  "transcription": {
    "intro": "Japanese intro (hiragana + N5 kanji only)",
    "dialogue": [
      { "speaker": "Male_1", "text": "Japanese line" },
      { "speaker": "Female_1", "text": "Japanese line" }
    ],
    "question": "Japanese question sentence"
  },
  "translations": {
    "tr": {
      "intro": "Turkish translation of intro",
      "dialogue": [
        { "speaker": "Male_1", "text": "Turkish translation" },
        { "speaker": "Female_1", "text": "Turkish translation" }
      ],
      "question": "Turkish translation of question"
    },
    "en": {
      "intro": "English translation of intro",
      "dialogue": [
        { "speaker": "Male_1", "text": "English translation" },
        { "speaker": "Female_1", "text": "English translation" }
      ],
      "question": "English translation of question"
    }
  },
  "analysis": {
    "vocabulary": [
      { "word": "Japanese word", "reading": "hiragana reading", "tr": "Turkish meaning", "en": "English meaning" }
    ],
    "grammar": [
      { "point": "grammar structure", "tr": "Turkish explanation", "en": "English explanation" }
    ]
  },
  "logic": {
    "tr": "Turkish explanation of why the correct answer is correct and why each distractor is wrong",
    "en": "English explanation of why the correct answer is correct and why each distractor is wrong"
  }
}
```

---

## Field Rules

| Field | Rule |
|-------|------|
| `source_clip` | Exact folder name from `tobeprocessed/` |
| `metadata.level` | Always `"n5"` (lowercase) |
| `metadata.pattern_used` | Must be one of: `Reconsideration`, `Shortage`, `Attribute`, `Negative`, `Sequential`, `Location` |
| `visual_prompts.options` | Exactly 4 items, ids 0–3 |
| `logic_role` values | Exactly one `"Correct"`, three distinct `"Distractor_A"`, `"Distractor_B"`, `"Distractor_C"` |
| `correct_option` | Integer 0–3, must match the id of the option with `logic_role: "Correct"` |
| `tts_script` entries | Each entry has EITHER `voice`+`text` OR `break` — never both in one object |
| `transcription.dialogue` | Non-empty array; speaker values must be `"Male_1"` or `"Female_1"` |
| `translations.tr` | Must be present |
| `translations.en` | Must be present |
| `analysis.vocabulary[].reading` | Must be hiragana (not romaji) |

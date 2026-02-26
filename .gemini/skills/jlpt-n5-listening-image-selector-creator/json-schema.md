# JLPT N5 Listening (Select Image) JSON Schema

The AI must output a single JSON object following this structure:

```json
{
  "metadata": {
    "level": "N5",
    "topic": "string (e.g., Shopping for lunch)",
    "pattern_used": "string (Reconsideration | Shortage | Attribute | Negative)"
  },
  "visual_prompts": {
    "master_style": "string (Description of the overall visual style, e.g., 'Clean anime style, minimalist coloring')",
    "options": [
      {
        "id": 1,
        "prompt": "string (Specific prompt for Option 1, including the visual delta)",
        "logic_role": "string (Correct | Distractor_A | Distractor_B | Distractor_C)"
      },
      { "id": 2, "prompt": "...", "logic_role": "..." },
      { "id": 3, "prompt": "...", "logic_role": "..." },
      { "id": 4, "prompt": "...", "logic_role": "..." }
    ]
  },
  "correct_option": "number (0-3)",
  "tts_script": [
    { "voice": "string", "text": "string", "break": "string (optional, e.g. '1s')" }
  ],
  "transcription": {
    "intro": "string (Japanese with furigana/hiragana)",
    "dialogue": [
      { "speaker": "string", "text": "string" }
    ],
    "question": "string"
  },
  "analysis": {
    "vocabulary": [
      { "word": "string", "tr": "string", "en": "string" }
    ],
    "grammar": [
      { "point": "string", "tr": "string", "en": "string" }
    ]
  },
  "logic": {
    "tr": "string (Detailed Turkish explanation of why this is correct and why traps are traps)",
    "en": "string (Detailed English explanation)"
  }
}
```

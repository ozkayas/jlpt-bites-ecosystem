# Fat JSON Schema for JLPT N5 Listening

Each `question.json` must contain a `translations` object for the main text and nested language maps for analysis and logic.

## Supported Languages
- `ja`: Japanese (Source)
- `tr`: Turkish
- `en`: English
- `de`: German
- `fr`: French
- `es`: Spanish
- `ko`: Korean

## Structure Overview

```json
{
  "metadata": {
    "level": "N5",
    "topic": {
      "ja": "...",
      "tr": "...",
      "en": "...",
      "de": "...",
      "fr": "...",
      "es": "...",
      "ko": "..."
    }
  },
  "correct_option": 0,
  "transcriptions": {
    "ja": { "intro": "...", "dialogue": [ { "speaker": "...", "text": "..." } ], "question": "..." },
    "tr": { "intro": "...", "dialogue": [ { "speaker": "...", "text": "..." } ], "question": "..." },
    "en": { "intro": "...", "dialogue": [ { "speaker": "...", "text": "..." } ], "question": "..." },
    "de": { "intro": "...", "dialogue": [ { "speaker": "...", "text": "..." } ], "question": "..." },
    "fr": { "intro": "...", "dialogue": [ { "speaker": "...", "text": "..." } ], "question": "..." },
    "es": { "intro": "...", "dialogue": [ { "speaker": "...", "text": "..." } ], "question": "..." },
    "ko": { "intro": "...", "dialogue": [ { "speaker": "...", "text": "..." } ], "question": "..." }
  },
  "analysis": {
    "vocabulary": [
      {
        "word": "...",
        "reading": "...",
        "meanings": {
          "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..."
        }
      }
    ],
    "grammar": [
      {
        "point": "...",
        "meanings": {
          "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..."
        }
      }
    ]
  },
  "logic": {
    "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..."
  }
}
```

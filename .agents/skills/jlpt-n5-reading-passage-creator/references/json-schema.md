# JSON Schema Reference — JLPT N5 Reading Passages

## Core JSON (Japonca içerik)

Dosya: `backend/reading/data/n5_passages_{type}_core.json`

```json
{
  "passages": [
    {
      "id": "n5_reading_short_010",
      "title": "Concise Japanese title",
      "visual_type": "none",
      "type": "short",
      "question_count": 2,
      "created_at": "2026-02-21T00:00:00Z",
      "sentences": [
        {
          "id": "s1",
          "original": "JAPANESE_TEXT",
          "furigana": "<ruby>漢字<rt>かんじ</rt></ruby>KANA",
          "romaji": "Modified Hepburn romanization"
        }
      ],
      "framed_sentences": [],
      "questions": [
        {
          "id": "q1",
          "text": "QUESTION_JP",
          "furigana": "<ruby>...<rt>...</rt></ruby>",
          "romaji": "...",
          "options": [
            { "id": "opt1", "text": "...", "furigana": "...", "is_correct": false, "romaji": "..." },
            { "id": "opt2", "text": "...", "furigana": "...", "is_correct": true,  "romaji": "..." },
            { "id": "opt3", "text": "...", "furigana": "...", "is_correct": false, "romaji": "..." },
            { "id": "opt4", "text": "...", "furigana": "...", "is_correct": false, "romaji": "..." }
          ]
        }
      ]
    }
  ]
}
```

### Field Rules

| Field | Rule |
|-------|------|
| `id` | `n5_reading_{type}_{NNN}` — zero-padded sequential, continue from last in file |
| `title` | Short Japanese title (concise, descriptive) |
| `visual_type` | `"letter"` \| `"notice"` \| `"memo"` \| `"email"` \| `"none"` |
| `type` | `"short"` \| `"mid"` |
| `question_count` | Must equal `len(questions)` |
| `created_at` | ISO 8601 UTC timestamp |
| `sentences` | Context text OUTSIDE frame; at least 1 item |
| `framed_sentences` | Text INSIDE box/frame; empty `[]` if no frame |
| `furigana` | `<ruby>漢字<rt>よみ</rt></ruby>` for kanji only; kana/particles unwrapped |
| `romaji` | Modified Hepburn: long vowels as `aa`, `ii`, `uu`, `ee`, `oo` |
| `questions` | At least 1 question; each must have exactly 4 options |
| `is_correct` | Exactly ONE `true` per question |

### Sentence ID Sequencing

IDs must be sequential across BOTH `sentences` and `framed_sentences`:
- `sentences`: s1, s2
- `framed_sentences`: s3, s4, s5 (continues from s2)

---

## Translation JSON

Dosya: `backend/reading/data/n5_passages_{type}_translations_{lang}.json`

Desteklenen diller: `en`, `tr`, `de`, `fr`, `es`

```json
{
  "passages": [
    {
      "id": "n5_reading_short_010",
      "sentences": {
        "s1": {
          "translation": "Natural idiomatic translation.",
          "mining_text": "### Grammar & Chunks\n- **particle**: explanation\n\n### Vocabulary\n- 漢字 (yomi): meaning"
        },
        "s3": {
          "translation": "...",
          "mining_text": "..."
        }
      },
      "questions": {
        "q1": {
          "text": "Translated question text",
          "options": {
            "opt1": "Option 1 translation",
            "opt2": "Option 2 translation",
            "opt3": "Option 3 translation",
            "opt4": "Option 4 translation"
          }
        }
      }
    }
  ]
}
```

### Mining Text Headers by Language

| Language | Grammar Section | Vocabulary Section |
|----------|-----------------|--------------------|
| `en` | `### Grammar & Chunks` | `### Vocabulary` |
| `tr` | `### Gramer & Kalıplar` | `### Kelimeler` |
| `de` | `### Grammatik & Strukturen` | `### Vokabular` |
| `fr` | `### Grammaire & Structures` | `### Vocabulaire` |
| `es` | `### Gramática & Estructuras` | `### Vocabulario` |

### Translation Rules

- **Sentences**: All sentences in `sentences` AND `framed_sentences` are included (same key space).
- **Question text**: Translate full question text.
- **Options**: Translate each option text (key = opt1/opt2/opt3/opt4).
- Do NOT include `is_correct` or `furigana` in translations.
- Translations must be idiomatic (not word-for-word).

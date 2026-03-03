# JSON Output Schema

## Top-level structure

```json
{
  "questions": [ ...Question[] ]
}
```

## Question object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `n5_essential_grammar_XXX` — zero-padded sequential number (e.g., 001, 002) |
| `level` | string | Always `"n5"` |
| `type` | string | Always `"sentenceCompletion"` |
| `sentence` | string | Japanese sentence with `（　　）` for the blank |
| `furigana` | string | Same sentence with `<ruby>漢字<rt>ふりがな</rt></ruby>` tags on all kanji |
| `blankPosition` | number | Word index of the blank (1-based) |
| `options` | string[4] | Exactly 4 options |
| `correctAnswer` | number | 0-based index into `options` |

## Example

```json
{
  "id": "n5_essential_grammar_001",
  "level": "n5",
  "type": "sentenceCompletion",
  "sentence": "明日　学校（　　）行きます。",
  "furigana": "<ruby>明日<rt>あした</rt></ruby>　<ruby>学校<rt>がっこう</rt></ruby>（　　）<ruby>行<rt>い</rt></ruby>きます。",
  "blankPosition": 2,
  "options": ["が", "を", "に", "で"],
  "correctAnswer": 2
}
```

## Rules

- `correctAnswer` is 0-indexed (0 = first option).
- `blankPosition` counts from 1; count only lexical words/particles, not punctuation.
- `furigana`: apply `<ruby>` to every kanji word; katakana/hiragana/particles have no ruby tags.
- All four options must be plausible distractors at N5 level — avoid obviously wrong choices.
- Output only valid JSON; no markdown fences, no extra keys.

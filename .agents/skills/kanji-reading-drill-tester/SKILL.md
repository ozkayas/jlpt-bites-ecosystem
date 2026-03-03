---
name: kanji-reading-drill-tester
description: "Validate kanji reading drill JSON files (kanji_reading_drill.json or kanji_selection_drill.json). Use this skill when the user asks to test, validate, check, or verify kanji reading drill questions. Performs two passes: (1) mechanical schema validation via script, (2) semantic/linguistic review by Claude. Checks: v:1 version, 5-digit IDs, exactly one <t>kanji</t> tag per sentence, options[0] is the correct hiragana reading, 2-4 options with no duplicates, tr+en translations present. Trigger on requests like 'kanji drill test et', 'validate kanji reading JSON', 'kanji okuma soruları doğrula', 'check kanji_reading_drill', or after editing drill questions."
---

# Kanji Reading Drill Tester

Validates questions in `kanji_reading_drill.json` (and `kanji_selection_drill.json`, which shares the same schema). Each item presents a Japanese sentence with a kanji highlighted in `<t>…</t>` tags; the learner must select the correct hiragana reading from four options.

## Data Format

```json
{
  "v": 1,
  "items": [
    [
      "00001",
      "<t>四月</t>に、わたしはにほんにいきたいです。",
      { "tr": "Nisan ayında Japonya'ya gitmek istiyorum.", "en": "I want to go to Japan in April." },
      ["しがつ", "よんがつ", "よがつ", "よっがつ"]
    ]
  ]
}
```

- `item[0]` — 5-digit zero-padded ID string (`"00001"`)
- `item[1]` — Japanese sentence; the kanji to be read is wrapped in **exactly one** `<t>…</t>` tag
- `item[2]` — translations object; must have at least `"tr"` (Turkish) and `"en"` (English)
- `item[3]` — options array; `options[0]` is the **correct hiragana reading**, `options[1…3]` are distractors

## Workflow

### Step 1 — Mechanical Validation

Run the script on the target file:

```bash
python3 <skill_dir>/scripts/mechanical_tester.py <path/to/kanji_reading_drill.json>
```

The script checks every item and exits with code `1` if any errors are found. Fix all mechanical errors before proceeding.

### Step 2 — Semantic (LLM) Review

Use the batch viewer to inspect questions in chunks:

```bash
# Show 5 questions starting from index 0
python3 <skill_dir>/scripts/batch_viewer.py <path/to/kanji_reading_drill.json> 0 5
```

Unless the user specifies IDs or a range, review a representative sample of **5–10 questions**.

For each question evaluate:

1. **Reading accuracy** — Does `options[0]` give the correct standard reading (*on'yomi* or *kun'yomi*) for the kanji inside `<t>…</t>` **in this specific sentence context**? (e.g. 四月 → しがつ, not よんがつ)
2. **Distractor quality** — Are the wrong options plausible alternative readings of the same kanji (common mistakes), yet all definitively incorrect in context? No distractor should be a valid alternate reading that makes the sentence acceptable.
3. **Translation accuracy** — Do `tr` and `en` accurately translate the full sentence with the correct answer substituted in? Grammar and nuance should be natural.
4. **Sentence naturalness** — Is the Japanese sentence grammatically natural and appropriate for N5 level?

## Mechanical Checks (reference)

| Check | Rule |
|-------|------|
| Root keys | `v` must equal `1`; `items` must be a non-empty list |
| Item structure | Each item is an array of exactly **4** elements |
| ID format | 5-digit zero-padded string (`"00001"`–`"99999"`) |
| ID uniqueness | No duplicate IDs |
| ID sequence | IDs should be consecutive starting from `"00001"` |
| `<t>` tag | Sentence contains **exactly one** `<t>…</t>` tag |
| Tag content | Text inside `<t>…</t>` must contain at least one kanji character (CJK U+4E00–U+9FFF) |
| Options count | `options` array has **2–4** items (app displays exactly 4) |
| Options uniqueness | No duplicate options within an item |
| Correct answer | `options[0]` is non-empty and must **not** appear in `options[1:]` |
| Translations | `item[2]` is a dict with non-empty `"tr"` and `"en"` keys |

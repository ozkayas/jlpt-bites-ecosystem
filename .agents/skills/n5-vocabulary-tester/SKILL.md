---
name: n5-vocabulary-tester
description: "Validate JLPT N5 vocabulary JSON files (n5_vocabulary.json). Use this skill when the user asks to test, validate, check, or verify vocabulary data in JSON format. Performs two passes: (1) mechanical schema validation via script, (2) semantic/linguistic review by Claude. Trigger on requests like 'vocabulary test et', 'validate vocabulary JSON', 'kelime listesi doğrula', 'n5_vocabulary.json kontrol et', or after editing vocabulary entries."
---

# JLPT N5 Vocabulary Tester

Validate `n5_vocabulary.json` in two passes.

## Pass 1 — Mechanical Validation (Script)

Run the validation script:

```bash
python3 skills/n5-vocabulary-tester/scripts/validate_vocabulary.py <path/to/n5_vocabulary.json>
```

The script checks:
- Root structure has `words` array
- Each word has required fields: `id`, `word`, `reading`, `romaji`, `tag`, `translations`, `sentences`
- `id` format: `n5_vocab_NNN` (zero-padded, e.g. `n5_vocab_001`)
- `id` uniqueness (no duplicates)
- `tag` is one of: `動詞`, `名詞`, `形容詞`, `副詞`, `表現`
- `translations` has all 5 languages: `en`, `tr`, `de`, `es`, `fr` — none empty
- At least 1 sentence per word
- Each sentence has: `ja`, `furigana`, `romaji`, `translations`
- Sentence `translations` has both `en` and `tr` — none empty
- Sentence `romaji` is romanized Japanese (not English/Turkish text)
- Furigana has balanced `<ruby>`, `</ruby>`, `<rt>`, `</rt>` tags
- **Furigana `<rt>` content contains no Latin letters** — only hiragana/katakana allowed inside `<rt>` tags (e.g. `<rt>cha</rt>` or `<rt>natsu</rt>` are errors; must be `<rt>ちゃ</rt>` and `<rt>なつ</rt>`)
- Warns on ID gaps (non-sequential IDs)
- Warns on words missing `audioUrl` field

Fix all script **errors** before proceeding to Pass 2. Warnings are informational.

## Pass 2 — Semantic Review (Claude)

After Pass 1 is clean, review entries linguistically.

Sample strategy:
- Review **all entries flagged by warnings** in Pass 1
- Randomly sample **~10 words** across different tags (`動詞`, `名詞`, `形容詞`, `副詞`, `表現`)
- For each entry check:

| Field | What to verify |
|-------|---------------|
| `word` → `reading` | Hiragana reading is correct |
| `reading` → `romaji` | Romanization matches standard Hepburn |
| `translations.en` / `.tr` | Meaning is correct and naturally phrased |
| `translations.de` / `.es` / `.fr` | Plausible (flag obvious errors) |
| `sentence.ja` | Grammatically correct, N5-level Japanese |
| `sentence.furigana` | Ruby readings match the kanji exactly; `<rt>` contains only hiragana/katakana (no Latin) |
| `sentence.romaji` | Is romanized Japanese (not a translation or English sentence) |
| `sentence.translations.en` / `.tr` | Accurate and natural |

## Output Format

```
## Pass 1 — Mechanical Validation
✅ X words validated, no errors
⚠️  Warnings (N): [list each warning with word ID]

## Pass 2 — Semantic Review
Sampled IDs: [list]

✅ No issues found
— OR —
❌ Issues found:
  - n5_vocab_XXX [word]: [description of issue]
```

---
name: jlpt-n5-listening-variation-tester
description: "Validate derived-data.json files produced by jlpt-n5-listening-variation-creator. Use this skill when the user asks to test, validate, check, or verify a listening variation JSON. Performs two passes: (1) mechanical schema validation via script, (2) semantic/linguistic review by Claude. Trigger on requests like 'variation test et', 'validate derived-data', 'listening varyasyonu doğrula', 'check derived-data.json', or after generating a variation with the creator skill."
---

# JLPT N5 Listening Variation Tester

Validate a `derived-data.json` file using a two-pass approach: mechanical schema check first, then semantic/linguistic review.

## Workflow

1. Identify the JSON to validate — file path provided by user, or content in context.
2. If JSON is in context (not a file), write it to a temporary file first.
3. Run **Pass 1 — Mechanical Validation:**

```bash
# From a file
python3 <skill_dir>/scripts/validate_derived_data.py <path/to/derived-data.json>

# From stdin
python3 <skill_dir>/scripts/validate_derived_data.py --stdin <<'EOF'
{ ...json... }
EOF
```

4. If Pass 1 reports failures, summarize them and stop — do not proceed to Pass 2.
5. Run **Pass 2 — Semantic Review** (Claude reads the JSON and checks):
   - Japanese dialogue is N5 level (only N5 vocabulary and grammar patterns).
   - `correct_option` is consistent with the dialogue logic (the dialogue leads to that answer).
   - The 3 distractors are genuine traps — plausible but clearly wrong given the dialogue.
   - Image prompts match the scene logic (Correct prompt depicts the correct answer; distractors depict the wrong options).
   - The variation is meaningfully different from what a source clip would typically contain (not a trivial rename).
   - `analysis.vocabulary[].reading` fields are hiragana (not romaji).
6. Report final results — Pass 1 script summary + Pass 2 semantic findings.

---

## Pass 1 — What the Script Checks

| Check | Rule |
|-------|------|
| `source_clip` | Present and non-empty string |
| `metadata.level` | Must be `"n5"` (lowercase) |
| `metadata.pattern_used` | Must be one of: `Reconsideration`, `Shortage`, `Attribute`, `Negative`, `Sequential`, `Location` |
| `visual_prompts.options` | Exactly 4 items |
| `logic_role` values | Exactly one `"Correct"`, one each of `"Distractor_A"`, `"Distractor_B"`, `"Distractor_C"` |
| `correct_option` | Integer 0–3 |
| `tts_script` entries | Every entry has EITHER `voice`+`text` OR `break` — no mixed objects, no other fields |
| `transcription.dialogue` | Non-empty array |
| `translations.tr` | Present |
| `translations.en` | Present |

---

## Pass 2 — Semantic Review Criteria

| Criterion | Check |
|-----------|-------|
| N5 Japanese level | No N4+ vocabulary or grammar patterns in dialogue |
| Logic consistency | Dialogue leads unambiguously to `correct_option` |
| Trap quality | Each distractor fails due to a specific, identifiable reason (not just random) |
| Image prompt alignment | Prompts depict what the logic_role says they should depict |
| Variation novelty | Entities differ meaningfully from the source clip (not superficially renamed) |

---

## Output Format

```
Pass 1 — Mechanical Validation
  ✓ source_clip: present
  ✓ metadata.level: "n5"
  ✓ metadata.pattern_used: "Reconsideration"
  ✓ visual_prompts.options: 4 items
  ✓ logic_role distribution: 1 Correct + 3 Distractors
  ✓ correct_option: 0 (valid range 0-3)
  ✓ tts_script: all entries valid
  ✓ transcription.dialogue: non-empty
  ✓ translations: tr + en present
  PASS — 9/9 checks passed

Pass 2 — Semantic Review
  ✓ Japanese dialogue: N5 level confirmed
  ✓ Logic consistency: dialogue leads to option 0 (hot coffee)
  ✓ Trap quality: Distractor_A (orange juice — rejected in line 3), Distractor_B (iced coffee — rejected in line 5), Distractor_C (cold item — contradicts final choice)
  ✓ Image prompts: all 4 prompts match their logic roles
  ✓ Variation novelty: significantly different from typical cafe/drink source clips
  PASS — All semantic checks passed
```

If anything fails, report the specific field or criterion and what was found vs. what was expected.

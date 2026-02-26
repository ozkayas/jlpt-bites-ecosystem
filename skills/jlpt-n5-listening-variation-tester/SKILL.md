---
name: jlpt-n5-listening-variation-tester
description: "Validate derived-data.json files produced by jlpt-n5-listening-variation-creator, then generate TTS audio if validation passes. Use this skill when the user asks to test, validate, check, or verify a listening variation JSON. Performs three passes: (1) mechanical schema validation via script, (2) semantic/linguistic review by Claude, (3) Gemini TTS audio generation. Trigger on requests like 'variation test et', 'validate derived-data', 'listening varyasyonu doğrula', 'check derived-data.json', or after generating a variation with the creator skill."
---

# JLPT N5 Listening Variation Tester

Validate a `derived-data.json` file using a three-pass approach: mechanical schema check, semantic/linguistic review, then Gemini TTS audio generation.

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
   - `image_prompt` matches the scene logic (panel descriptions align with each panel's `logic_role` — correct panel depicts the right answer, distractor panels depict the wrong options).
   - The variation is meaningfully different from what a source clip would typically contain (not a trivial rename).
   - `analysis.vocabulary[].reading` fields are hiragana (not romaji).
6. If Pass 2 finds failures, report them and stop — do not proceed to Pass 3.
7. Run **Pass 3 — Audio Generation** (only if a real file path was provided):

```bash
python3 backend/listening/scripts/generate_tts_audio.py <path/to/derived-data.json> \
  --output <clip_folder>/variation.wav
# Output: variation.wav in the same folder as derived-data.json
```

   - Output file is always named `variation.wav` (distinguishes it from the original `audio.mp3`).
   - If JSON was provided as inline content (no real file path), skip Pass 3 and print the manual command for the user to run.
   - Requires `GEMINI_API_KEY` or `GEMINI_API_KEYS` environment variable.
8. Report final results — all three passes.

---

## Pass 1 — What the Script Checks

| Check | Rule |
|-------|------|
| `source_clip` | Present and non-empty string |
| `metadata.level` | Must be `"n5"` (lowercase) |
| `metadata.pattern_used` | Must be one of: `Reconsideration`, `Shortage`, `Attribute`, `Negative`, `Sequential`, `Location` |
| `visual_prompts.image_type` | Must be one of: `"four_panel_grid"`, `"numbered_scene"`, `"map_diagram"` |
| `visual_prompts.image_prompt` | Present and non-empty string |
| `visual_prompts.panel_map` | Exactly 4 items |
| `logic_role` values (via `panel_map`) | Exactly one `"Correct"`, one each of `"Distractor_A"`, `"Distractor_B"`, `"Distractor_C"` |
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
| Image prompt alignment | `image_prompt` panel descriptions match their `logic_role` assignments in `panel_map` |
| Variation novelty | Entities differ meaningfully from the source clip (not superficially renamed) |

---

## Pass 3 — Audio Generation

Runs `generate_tts_audio.py` which:
- Sends `Intro_Voice` lines to Gemini as single-speaker calls (Kore voice)
- Sends all `Male_1` / `Female_1` dialogue lines as one multi-speaker call (Puck + Zephyr voices)
- Generates silence segments for `break` entries
- Stitches all segments into a final `.wav` file

**Output:** `variation.wav` saved next to `derived-data.json` (named to distinguish from the original `audio.mp3` in the same folder)

**Skip condition:** If JSON was provided inline (not from a file path), print this command and ask the user to run it manually:
```bash
python3 backend/listening/scripts/generate_tts_audio.py <path/to/derived-data.json> \
  --output <clip_folder>/variation.wav
```

---

## Output Format

```
Pass 1 — Mechanical Validation
  ✓ source_clip: present
  ✓ metadata.level: "n5"
  ✓ metadata.pattern_used: "Reconsideration"
  ✓ visual_prompts.image_type: "four_panel_grid"
  ✓ visual_prompts.image_prompt: present and non-empty string
  ✓ visual_prompts.panel_map: 4 items
  ✓ logic_role distribution: 1 Correct + 3 Distractors
  ✓ correct_option: 0 (valid range 0-3)
  ✓ tts_script: all entries valid
  ✓ transcription.dialogue: non-empty
  ✓ translations: tr + en present
  PASS — 12/12 checks passed

Pass 2 — Semantic Review
  ✓ Japanese dialogue: N5 level confirmed
  ✓ Logic consistency: dialogue leads to option 0 (hot coffee)
  ✓ Trap quality: Distractor_A (orange juice — rejected in line 3), Distractor_B (iced coffee — rejected in line 5), Distractor_C (cold item — contradicts final choice)
  ✓ Image prompt: all 4 panel descriptions match their panel_map logic roles
  ✓ Variation novelty: significantly different from typical cafe/drink source clips
  PASS — All semantic checks passed

Pass 3 — Audio Generation
  Running: python3 backend/listening/scripts/generate_tts_audio.py <path/to/derived-data.json> --output <clip_folder>/variation.wav
  ✓ Audio generated: variation.wav (12.3s | 591 KB)
  PASS — Audio ready
```

If anything fails in Pass 1 or Pass 2, report the specific field or criterion and what was found vs. what was expected. Pass 3 is only attempted after both Pass 1 and Pass 2 succeed.

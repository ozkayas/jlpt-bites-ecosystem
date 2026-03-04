---
name: jlpt-n5-listening-variation-tester
description: "Validate derived-data.json files produced by jlpt-n5-listening-variation-creator, then verify the generated image.png, convert it to WebP for mobile, generate TTS audio, and build the final question.json for Firebase. Use this skill when the user asks to test, validate, check, or verify a listening variation. Performs six passes: (1) mechanical schema validation via script, (2) semantic/linguistic review by Claude, (3) visual image check by Claude reading image.png, (3.5) image optimization to WebP, (4) Gemini TTS audio generation, (5) build final question.json. Trigger on requests like 'variation test et', 'validate derived-data', 'listening varyasyonu doğrula', 'check derived-data.json', or after generating a variation with the creator skill."
---

# JLPT N5 Listening Variation Tester

Validate a `derived-data.json` file using a six-pass approach: mechanical schema check, semantic/linguistic review, visual image check, WebP image optimization, Gemini TTS audio generation, then final question.json build.

## Workflow

1. Identify the clip folder — file path provided by user, or derive it from context.
2. If JSON is provided as inline content (not a file path), write it to a temporary file first.
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
7. Run **Pass 3 — Image Validation** (Claude reads `image.png` from the clip folder):
   - Check that `image.png` exists in the clip folder. If missing, stop and instruct user to run `generate_image.py` first.
   - Read the image and verify the `image_type` matches what is actually shown:
     - `four_panel_grid`: exactly 4 equal panels in a 2×2 grid, small numbers 1–4 visible in the corner of each panel
     - `numbered_scene`: single continuous scene with small position numbers 1–4 visible
     - `map_diagram`: top-down street or area map with small position numbers 1–4 on buildings/locations
   - Verify the correct panel (identified by `panel_map` + `correct_option`) visually depicts the answer the dialogue leads to.
   - Verify each distractor panel visually depicts a plausible but wrong alternative.
   - Verify overall style: monochrome line art, no shading, white background.
8. If Pass 3 finds failures, report them and stop — do not proceed to Pass 3.5.
8.1 **CRITICAL: STOP FOR MANUAL APPROVAL:** After Pass 3 (Image Validation) is complete and successful, you MUST STOP. Display the image, dialogue, and translations. WAIT for explicit approval (e.g., "Onaylıyorum") before running Pass 3.5, Pass 4, Pass 5, or Pass 6. NEVER automate these final steps without direct confirmation for the specific image generated.
8.2. Run **Pass 3.5 — Image Optimization** (convert image.png → image.webp for mobile):

```bash
python3 -c "
from PIL import Image
import os

src = '<clip_folder>/image.png'
dst = '<clip_folder>/image.webp'
img = Image.open(src)
original_size = img.size
if max(img.size) > 700:
    img.thumbnail((700, 700), Image.LANCZOS)
img.save(dst, 'WEBP', quality=85, method=6)
os.remove(src)
size_kb = os.path.getsize(dst) // 1024
print(f'✓ {original_size} → {img.size} | WebP {size_kb} KB')
"
```

   - Use the same Python environment used for other skill scripts (e.g. agents venv).
   - Target: max 700×700 px, WebP quality 85.
   - Deletes `image.png` after successful conversion — `image.webp` is the final file going forward.
   - If conversion fails, report the error and stop — do not proceed to Pass 4.
9. Run **Pass 4 — Audio Generation** (only if a real file path was provided):

```bash
python3 backend/listening/scripts/generate_tts_audio.py <path/to/derived-data.json> \
  --output <clip_folder>/variation-audio.wav
# Output: variation-audio.wav in the same folder as derived-data.json
```

   - Output file is always named `variation-audio.wav` (distinguishes it from the original `audio.mp3`).
   - If JSON was provided as inline content (no real file path), skip Pass 4 and print the manual command for the user to run.
   - Requires `GEMINI_API_KEY` or `GEMINI_API_KEYS` environment variable.
10. Run **Pass 5 — Build question.json:**

```bash
python3 skills/jlpt-n5-listening-variation-tester/scripts/build_question_json.py <path/to/derived-data.json>
# Output: question.json written to the same clip folder
```

   - Transforms `derived-data.json` into the final Firebase-ready format.
   - Removes internal fields (`source_clip`, `visual_prompts`, `tts_script`, `metadata.pattern_used`).
   - Uppercases `metadata.level` ("n5" → "N5").
   - Maps speaker IDs to Japanese labels (`Male_1` → `男の人`, `Female_1` → `女の人`).
   - Sets `audio_url: null` and `image_url: null` (to be filled when uploading to Firebase Storage).
   - Output file is always named `question.json` in the same clip folder.
11. Run **Pass 6 — Move Folder:**
   - If all previous passes are successful, remove the `processing.lock/` directory (if it exists) and move the entire clip folder from `tobeprocessed/` to `processed/`.
   ```bash
   rm -rf "<clip_folder>/processing.lock"
   mv "<clip_folder>" "backend/listening/data/selectImage/listening-youtube-data/processed/"
   ```
12. Report final results — all six passes.

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

---

## Pass 2 — Semantic Review Criteria

| Criterion | Check |
|-----------|-------|
| N5 Japanese level | No N4+ vocabulary or grammar patterns in dialogue |
| Logic consistency | Dialogue leads unambiguously to `correct_option` |
| Trap quality | Each distractor fails due to a specific, identifiable reason (not just random) |
| Image prompt alignment | `image_prompt` panel descriptions match their `logic_role` assignments in `panel_map` |
| Variation novelty | Entities differ meaningfully from the source clip (not superficially renamed) |
| Translation accuracy | `transcription_tr` accurately and naturally reflects the Japanese dialogue and question |

---

## Pass 3 — Image Validation

Claude reads `image.png` from the clip folder and verifies:

| Check | What to look for |
|-------|-----------------|
| File exists | `image.png` present in clip folder |
| `image_type` match | Layout matches declared type (`four_panel_grid` / `numbered_scene` / `map_diagram`) |
| Correct panel content | Panel identified by `panel_map` + `correct_option` shows the dialogue's answer |
| Distractor panel content | Each distractor panel shows a plausible but wrong alternative |
| Style | Monochrome line art, no shading, white background |

**Missing image:** If `image.png` does not exist, stop and print:
```
✗ image.png not found in <clip_folder>
  Run: python3 skills/jlpt-n5-listening-variation-creator/scripts/generate_image.py <clip_name>
```

---

## Pass 4 — Audio Generation

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
  PASS — 10/10 checks passed

Pass 2 — Semantic Review
  ✓ Japanese dialogue: N5 level confirmed
  ✓ Logic consistency: dialogue leads to option 0 (hot coffee)
  ✓ Trap quality: Distractor_A (orange juice — rejected in line 3), Distractor_B (iced coffee — rejected in line 5), Distractor_C (cold item — contradicts final choice)
  ✓ Image prompt: all 4 panel descriptions match their panel_map logic roles
  ✓ Variation novelty: significantly different from typical cafe/drink source clips
  ✓ Translation: transcription_tr accurately reflects the dialogue
  PASS — All semantic checks passed

Pass 3 — Image Validation
  ✓ image.png found in clip folder
  ✓ image_type: four_panel_grid confirmed (4 equal panels, small numbers 1–4 in corners)
  ✓ Correct panel (Panel 1): shows warm bowl of rice — matches dialogue answer
  ✓ Distractor_A (Panel 2): shows sandwich — plausible wrong choice
  ✓ Distractor_B (Panel 3): shows salad — plausible wrong choice
  ✓ Distractor_C (Panel 4): shows cold noodles — plausible wrong choice
  ✓ Style: monochrome line art, white background confirmed
  PASS — Image valid

Pass 3.5 — Image Optimization
  ✓ Converted: 1024×1024 → 700×700 | WebP 48 KB (was 412 KB PNG)
  ✓ image.png deleted, image.webp saved
  PASS — Image optimized

Pass 4 — Audio Generation
  Running: python3 backend/listening/scripts/generate_tts_audio.py <path/to/derived-data.json> --output <clip_folder>/variation-audio.wav
  ✓ Audio generated: variation-audio.wav (37.8s | 1773 KB)
  PASS — Audio ready

Pass 5 — Build question.json
  Running: python3 skills/jlpt-n5-listening-variation-tester/scripts/build_question_json.py <path/to/derived-data.json>
  ✓ question.json written: <clip_folder>/question.json
  PASS — Final JSON ready

Pass 6 — Move Folder
  ✓ Folder moved from tobeprocessed/ to processed/
  PASS — Folder moved
```

If anything fails in any pass, report the specific field or criterion and what was found vs. what was expected. Each subsequent pass is only attempted after the previous one succeeds.

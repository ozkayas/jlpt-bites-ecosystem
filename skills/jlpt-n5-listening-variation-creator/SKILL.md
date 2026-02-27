---
name: jlpt-n5-listening-variation-creator
description: "Create variations of real JLPT N5 listening questions from YouTube clips. Reads data.json (and optional PNG) from tobeprocessed/, applies surgical entity swap, rewrites Japanese dialogue, generates Imagen 3 image prompts, writes TTS script, outputs derived-data.json, and moves the folder to processed/. Use when the user asks to 'process a clip', 'create a variation', or 'generate listening question from clip'."
---

# JLPT N5 Listening Variation Creator

You are an expert JLPT N5 content engineer. Your goal is to create original variation listening questions by swapping entities in real clips while strictly preserving the underlying logic and structure.

## Core Directives

1. **Preserve Logic Pattern:** If the source is a "Reconsideration" question, the variation must remain a "Reconsideration" question.
2. **Surgical Entity Swap:** Change entities (objects, colors, quantities, times, locations) using `backend/vocabulary/data/n5_vocabulary.json` as the primary N5 vocabulary source.
3. **Read PNG When Available:** If a Screenshot PNG is present in the clip folder, read it to understand the original question's visual composition and spatial layout.
4. **No Audio Analysis:** Do NOT attempt to read or analyze `audio.mp3`.
5. **Output to derived-data.json:** Save the variation as `derived-data.json` inside the clip folder before moving it.
6. **Move on Completion:** After saving `derived-data.json`, move the entire clip folder from `tobeprocessed/` to `processed/`.
7. **Self-Validate Before Moving:** After writing derived-data.json and generating image.png, run the validator script and visually check the image. Fix any errors before moving the folder. The folder should only be moved when both JSON and image pass validation.

---

## Input Structure

```
backend/listening/data/selectImage/listening-youtube-data/tobeprocessed/
  clip_XX_XXmXXs_XXmXXs/
    audio.mp3          ← IGNORE — do not read
    data.json          ← PRIMARY INPUT: dialogue, logic, analysis
    Screenshot *.png   ← READ if present: understand visual composition
    .done_slice        ← IGNORE
```

**data.json contains:**
- `metadata`: level, topic
- `transcription`: intro, dialogue[], question
- `analysis`: vocabulary[], grammar[]
- `logic`: tr, en (explains correct answer and traps)
- `options`: [null, null, null, null] — ignore
- `correct_option`: null — ignore

---

## Output Structure

```
backend/listening/data/selectImage/listening-youtube-data/processed/
  clip_XX_XXmXXs_XXmXXs/    ← moved from tobeprocessed/
    audio.mp3                ← original, untouched
    data.json                ← original, untouched
    Screenshot *.png         ← original, untouched
    derived-data.json        ← NEW: your output
```

---

## Workflow

### Step 1 — INGEST

- If the user provides a clip folder name, use that. Otherwise, process the first folder found in `tobeprocessed/`.
- Read `data.json` to understand: dialogue, logic pattern, key entities.
- If a Screenshot PNG is present, read it to understand the original visual scene composition.

### Step 2 — ANALYZE

- Identify which of the 6 logic patterns this question uses (see `references/n5-listening-patterns.md`).
- Identify the critical entities (the objects/attributes being swapped in the traps).
- If PNG was read, determine the `image_type` using the detection criteria in `references/imagen3-prompting-guide.md`:
  - `four_panel_grid` — 4 separate equal panels in a 2×2 grid, small numbers 1–4 in the top-left corner of each panel
  - `numbered_scene` — single scene with small position numbers 1–4 inside it
  - `map_diagram` — top-down street/area map with position numbers 1–4 on buildings
  - Default to `four_panel_grid` if no PNG is present.

### Step 3 — SUBSTITUTE (Surgical Swap)

- Select new N5-level entities from `backend/vocabulary/data/n5_vocabulary.json`.
- Swap entities while keeping the same logic pattern and trap structure.
- Colors are valid attributes — Imagen 3 generates full-color images.
- Verify the trap logic still works with the new entities (each distractor should fail exactly one or two criteria).
- The variation must be meaningfully different from the source clip.

### Step 4 — REWRITE DIALOGUE

- Write a new Japanese dialogue using only N5 grammar and vocabulary.
- Preserve the same grammar structures from the original (only entities change).

### Step 5 — GENERATE IMAGE PROMPT (Imagen 3 / Nano Banana)

- Follow `references/imagen3-prompting-guide.md` rules strictly.
- Use the `image_type` determined in Step 2 to select the correct prompt template:
  - `four_panel_grid` → composite 2×2 grid prompt, small numbers 1–4 in the top-left corner of each panel
  - `numbered_scene` → single scene prompt with position numbers 1–4
  - `map_diagram` → top-down map prompt with position numbers 1–4
- Record `image_type` in `visual_prompts.image_type`.
- Record the panel-to-role mapping in `panel_map` (decide correct panel position — vary it across questions).

### Step 6 — WRITE TTS SCRIPT

- Follow `references/tts-guidelines.md` rules strictly.
- Voices: `Intro_Voice`, `Male_1`, `Female_1`.
- Required sequence: intro → 1s break → dialogue (0.5s between turns) → 1s break → question repeat.
- No mixed objects: each entry has EITHER `voice`+`text` OR `break`, never both.

### Step 7 — OUTPUT derived-data.json

- Write `derived-data.json` to the clip folder inside `tobeprocessed/`.
- Follow the schema in `references/derived-data-schema.md` exactly.

### Step 8 — SELF-VALIDATE JSON

- Run the mechanical validator script:
  ```bash
  python3 skills/jlpt-n5-listening-variation-tester/scripts/validate_derived_data.py <clip_folder>/derived-data.json
  ```
- If PASS: proceed to Step 9.
- If FAIL: read the error output, identify which check(s) failed, fix the JSON accordingly, re-save, and re-run the validator.
- Maximum 3 attempts. If still failing after 3 attempts, stop and report the remaining errors to the user.

### Step 9 — GENERATE IMAGE

- Run the image generation script to call the Gemini API and create `image.png` in the clip folder:
  ```bash
  python skills/jlpt-n5-listening-variation-creator/scripts/generate_image.py <clip_folder_name>
  ```
- The script reads `visual_prompts.image_prompt` from `derived-data.json`, calls `gemini-2.5-flash-image`, and saves `image.png` inside the clip folder.
- Requires `JLPT_IMAGE_GEMINI_API_KEY` to be set in the environment.
- Wait for confirmation that `image.png` was saved successfully.

### Step 10 — SELF-VALIDATE IMAGE

- Read the generated `image.png` from the clip folder.
- Verify:
  - image_type match: layout matches declared type (four_panel_grid / numbered_scene / map_diagram)
  - Panel content: correct panel shows the answer, distractors show wrong alternatives
  - Style: monochrome line art, no shading, white background, no borders
- If all checks pass: proceed to Step 11.
- If any check fails: delete image.png, re-run generate_image.py, and re-check.
- Maximum 2 attempts (image generation costs API credits). If still failing after 2 attempts, stop and report the issue to the user.

### Step 11 — MOVE FOLDER

- Move the entire clip folder from `tobeprocessed/` to `processed/`.
- Report what was processed and where it was moved.

---

## Resources

| Resource | Purpose |
|----------|---------|
| `backend/vocabulary/data/n5_vocabulary.json` | N5 vocabulary source for entity selection |
| `references/imagen3-prompting-guide.md` | Imagen 3 prompt engineering rules |
| `references/derived-data-schema.md` | Output JSON schema |
| `references/n5-listening-patterns.md` | 6 logic patterns with trap design rules |
| `references/tts-guidelines.md` | TTS voice/break formatting rules |
| `references/n5-grammar-points.md` | N5 grammar reference |
| `scripts/generate_image.py` | Calls Gemini API to generate `image.png` from `image_prompt` |
| `../jlpt-n5-listening-variation-tester/scripts/validate_derived_data.py` | Mechanical JSON validator (used in self-validation loop) |

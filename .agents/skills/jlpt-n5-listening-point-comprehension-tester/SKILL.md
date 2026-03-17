---
name: jlpt-n5-listening-point-comprehension-tester
description: "Validate JLPT N5 Listening Point Comprehension (selectText) question_data.json files. Performs mechanical schema validation, semantic/linguistic N5-level review, and generates TTS script for audio production. Use when the user asks to 'test selectText', 'validate point comprehension', 'selectText soruları test et', 'point comprehension doğrula', or after generating questions with the creator skill."
---

# JLPT N5 Listening Point Comprehension Tester

You validate `question.json` (Fat JSON) files for the selectText (Mondai 2 / Point Comprehension) module. The pipeline has 3 passes: mechanical validation, semantic review, and TTS script generation. Also supports legacy `question_data.json` files.

## Core Directives

1. **Run all passes in order.** Do not skip passes.
2. **Stop on FAIL.** If Pass 1 or Pass 2 reports critical errors, fix them before proceeding.
3. **Single file or batch.** User can specify one file or run `--batch` on the entire directory.
4. **TTS script goes into the same folder** as `question_data.json`, named `tts_script.json`.

---

## Input

```
backend/listening/data/selectText/
  {id}/
    question.json         <- Input to validate (Fat JSON, multi-language)
    question_data.json    <- Legacy format (single-language, still supported)
    audio.mp3             <- May or may not exist yet
```

**Priority:** If both `question.json` and `question_data.json` exist, validate `question.json`.

The user specifies either:
- A specific folder ID (e.g., `002`)
- `--batch` to validate all numbered folders
- A file path directly

---

## Pass 1 — Mechanical Validation (Script)

Run the validator script:

```bash
python3 .agents/skills/jlpt-n5-listening-point-comprehension-tester/scripts/validate_question_data.py <path_to_question_data.json>
```

Or for batch:

```bash
python3 .agents/skills/jlpt-n5-listening-point-comprehension-tester/scripts/validate_question_data.py --batch backend/listening/data/selectText/
```

### What it checks (10 checks):
1. `metadata`: level="N5", topic non-empty, audio_url field exists
2. `options`: exactly 4 non-empty strings
3. `correct_option`: integer 0-3
4. `transcription`: intro (>10 chars), question (ends with か。), dialogue (>=2 turns, valid speakers)
5. `analysis.vocabulary`: >=2 items, each with word/tr/en
6. `analysis.grammar`: >=1 item, each with point/tr/en
7. `logic`: tr and en both >20 chars
8. No duplicate options
9. Intro contains a question word (なにを, どこ, いつ, etc.)
10. Options prefer hiragana/katakana (warns on kanji)

**If any FAIL:** Stop. Report errors. Fix the JSON. Re-run Pass 1.
**If only WARNs or all PASS:** Proceed to Pass 2.

---

## Pass 2 — Semantic / Linguistic Review (Claude)

Read the `question_data.json` and perform a thorough review. Check each of the following criteria and report PASS/FAIL/WARN for each:

### 2.1 — N5 Level Appropriateness
- All vocabulary in the dialogue must be N5 level or below.
- All grammar patterns must be N5 level (refer to `references/n5-grammar-points.md` from the creator skill).
- No N4+ vocabulary or grammar should appear.
- **Check:** Are there any words or grammar patterns that a JLPT N5 student would not know?

### 2.2 — Correct Answer Validity
- Read the dialogue carefully.
- Verify that `options[correct_option]` is indeed the correct answer based on the dialogue logic.
- **Check:** Is the marked correct answer actually correct?

### 2.3 — Distractor Plausibility
- Each distractor (wrong option) must be mentioned or implied in the dialogue.
- No random options that have no connection to the conversation.
- Distractors should be plausible enough to trick someone who didn't listen carefully.
- **Check:** Are all 3 distractors derived from the dialogue? Are they plausible?

### 2.4 — Trap Logic Integrity
- Identify which trap pattern is used (Fikir Değiştirme, Dikkat Dağıtıcı, Hesaplama, Zaman Çıkarımı, Olumsuz Eleme, Düzeltme, Sipariş, Neden).
- Verify the trap works: a careless listener should fall for at least one distractor.
- **Check:** Does the question have a clear trap mechanism?

### 2.5 — Dialogue Naturalness
- The Japanese dialogue should sound natural and conversational.
- Speakers should have appropriate roles (e.g., てんいん uses keigo, friends use casual-polite).
- The intro correctly describes the scene and speakers.
- **Check:** Does the dialogue sound natural for N5-level Japanese?

### 2.6 — Logic Explanation Quality
- `logic.tr` and `logic.en` should accurately explain why the answer is correct.
- They should mention why each distractor is wrong.
- **Check:** Are the logic explanations accurate and complete?

### 2.7 — Translation Accuracy
- `analysis.vocabulary[].tr` and `analysis.vocabulary[].en` translations must be correct.
- `analysis.grammar[].tr` and `analysis.grammar[].en` explanations must be correct.
- **Check:** Are all translations accurate?

### Output Format for Pass 2

```
PASS 2 — Semantic Review for {id}
  2.1 N5 Level:       ✅ PASS / ❌ FAIL (details)
  2.2 Correct Answer: ✅ PASS / ❌ FAIL (details)
  2.3 Distractors:    ✅ PASS / ❌ FAIL (details)
  2.4 Trap Logic:     ✅ PASS / ❌ FAIL (pattern: X)
  2.5 Naturalness:    ✅ PASS / ⚠️ WARN (details)
  2.6 Logic Quality:  ✅ PASS / ❌ FAIL (details)
  2.7 Translations:   ✅ PASS / ❌ FAIL (details)
```

**If any FAIL in 2.1-2.4:** These are critical. Stop. Report the issues. Suggest fixes.
**If only WARNs or all PASS:** Proceed to Pass 3.

---

## Pass 3 — TTS Script Generation

Generate a `tts_script.json` file that follows the Gemini TTS format used by the existing listening pipeline.

### Voice Mapping

| Role | Voice ID | Gemini Voice |
|------|----------|-------------|
| Narrator (intro + question) | Intro_Voice | Kore |
| Male speaker | Male_1 | Puck |
| Female speaker | Female_1 | Zephyr |

### Speaker → Voice Mapping Rules

| Speaker Label | Voice ID |
|---------------|----------|
| おとこのひと, おとこのがくせい | Male_1 |
| おんなのひと, おんなのがくせい | Female_1 |
| せんせい | Female_1 (default) or Male_1 (if context indicates male) |
| がくせい | Male_1 (default) or Female_1 (if context indicates female) |
| てんいん, おみせのひと | Male_1 (default) or Female_1 (if context indicates female) |
| いしゃ | Male_1 (default) or Female_1 (if context indicates female) |
| 男の人 | Male_1 |
| 女の人 | Female_1 |

### TTS Script Structure

```json
{
  "tts_script": [
    {"voice": "Intro_Voice", "text": "intro text here"},
    {"break": "1s"},
    {"voice": "Male_1", "text": "first dialogue line"},
    {"break": "0.5s"},
    {"voice": "Female_1", "text": "second dialogue line"},
    {"break": "0.5s"},
    {"voice": "Male_1", "text": "third dialogue line"},
    {"break": "1s"},
    {"voice": "Intro_Voice", "text": "question text repeated here"}
  ]
}
```

### Rules

1. **Intro first:** The narrator reads the intro text.
2. **1 second break** after intro.
3. **Dialogue lines:** Each line uses the voice mapped from the speaker label.
4. **0.5 second break** between each dialogue turn.
5. **1 second break** before the question repeat.
6. **Question repeat:** The narrator reads the question text.
7. **No mixed entries:** Each object has EITHER `{voice, text}` OR `{break}`, never both.
8. **Text must be Japanese only.** No Turkish or English in the TTS script.

### Generation Steps

1. Read `question.json` (or `question_data.json` for legacy). For Fat JSON, use `transcriptions.ja`.
2. Map each speaker in `transcriptions.ja.dialogue` (or `transcription.dialogue` for legacy) to a voice ID.
3. Build the `tts_script` array following the structure above.
4. Save as `tts_script.json` in the same folder as `question_data.json`.
5. Display the generated script to the user.

### Output

Save to: `backend/listening/data/selectText/{id}/tts_script.json`

---

## Workflow Summary

```
User: "selectText soruları test et" / "002 test et" / "validate point comprehension --batch"
  │
  ▼
Pass 1: python3 validate_question_data.py <file_or_batch>
  │ FAIL? → Fix → Re-run
  ▼
Pass 2: Claude semantic review (N5 level, correct answer, distractors, traps, naturalness)
  │ FAIL? → Fix → Re-run
  ▼
Pass 3: Generate tts_script.json
  │
  ▼
Done. Report results. tts_script.json ready for audio generation.
```

---

## Batch Mode

When running in batch mode (`--batch` or "hepsini test et"):
1. Run Pass 1 on all files first. Report summary.
2. Run Pass 2 only on files that passed Pass 1.
3. Generate TTS scripts only for files that passed both Pass 1 and Pass 2.
4. Report overall summary at the end.

---

## Resources

| Resource | Purpose |
|----------|---------|
| `scripts/validate_question_data.py` | Mechanical validation script (Pass 1) |
| `backend/listening/data/selectText/001/question_data.json` | Reference format |
| Creator skill's `references/n5-grammar-points.md` | N5 grammar checklist for Pass 2 |

---
name: jlpt-n5-grammer-text-integration-question-tester
description: Validate JLPT text-level grammar (Mondai 3) JSON files produced by jlpt-n5-grammer-text-integration-question-creator. Use this skill when the user asks to test, validate, check, or verify Mondai 3 (text integration) questions in JSON format. Checks (1) schema correctness for "textFlow" type, (2) blankNumber/position sequencing, (3) correctAnswer is valid, (4) level is n5. Trigger on requests like "Mondai 3 soruları test et", "validate text integration questions", "textFlow JSON doğrula", or after generating questions with the text integration creator skill.
---

# JLPT Text Integration Question Tester

Validate JLPT N5 text-level grammar (Mondai 3) JSON using `scripts/validate_text_integration.py`.

## Workflow

1. Identify the JSON to validate — either a file path provided by the user, or JSON content in the conversation.
2. If JSON is in context (not a file), write it to a temporary file first, then run the script.
3. Run the validator:

```bash
# From a file
python3 <skill_dir>/scripts/validate_text_integration.py <path/to/questions.json>

# From stdin (JSON in context)
python3 <skill_dir>/scripts/validate_text_integration.py --stdin <<'EOF'
{ ...json... }
EOF
```

4. If the script reports failures, summarize them and stop here.
5. **Linguistic review**: If all questions pass the script, read the JSON file and verify each question linguistically:
   - Reconstruct the full text by joining `textSegments` with the correct `options[correctAnswer]` in between.
   - Verify the reconstructed text is a coherent, grammatically correct N5-level narrative.
   - Verify each correct answer is the ONLY correct option among the 4 choices for that blank.
   - Verify all distractors are plausible yet incorrect in the context of the narrative.
   - Verify all vocabulary and kanji are within N5 scope.
   - Report any linguistically incorrect questions with an explanation.
6. Report final results — script validation + linguistic review summary.

## What the script checks per question (mechanical)

| Check | Rule |
|-------|------|
| `id` format | Must match `n5_grammer_text_integration_XXX` |
| `level` | Must be `"n5"` |
| `type` | Must be `"textFlow"` |
| `title` | Must be a non-empty string |
| `textSegments` | Array of strings (at least 2) |
| `blanks` | Array of objects; length must be `len(textSegments) - 1` |
| `blankNumber` | Positive integer |
| `position` | Must match the index in the `blanks` array |
| `options` | Must be an array of exactly 4 non-empty strings |
| `correctAnswer` | Must be an integer 0–3 |

## Output

The script prints a report with `✅ PASS` or `❌ FAIL` per question and a summary line.
Exit code `0` = all passed, `1` = one or more failed.

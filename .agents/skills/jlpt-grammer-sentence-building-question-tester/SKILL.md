---
name: jlpt-grammer-sentence-building-question-tester
description: "Validate JLPT sentence building (starQuestion) JSON files produced by jlpt-n5-grammer-sentence-building-question-creator. Use this skill when the user asks to test, validate, check, or verify sentence building questions in JSON format. Checks: (1) schema/format correctness of all fields, (2) correctOrder is a valid permutation of [0,1,2,3], (3) starPosition is 0-3, (4) scrambledWords has exactly 4 items, (5) level is n5. Trigger on requests like 'sentence building soruları test et', 'validate sentence building questions', 'cümle birleştirme soruları doğrula', 'check starQuestion JSON', or after generating questions with the sentence building creator skill."
---

# JLPT Sentence Building Question Tester

Validate JLPT N5 sentence building question JSON using `scripts/validate.py`.

## Workflow

1. Identify the JSON to validate — either a file path provided by the user, or JSON content in the conversation.
2. If JSON is in context (not a file), write it to a temporary file first, then run the script.
3. Run the validator:

```bash
# From a file
python3 <skill_dir>/scripts/validate.py <path/to/questions.json>

# From stdin (JSON in context)
python3 <skill_dir>/scripts/validate.py --stdin <<'EOF'
{ ...json... }
EOF
```

4. If the script reports failures, summarize them and stop here.
5. **Linguistic review**: If all questions pass the script, read the JSON file and verify each question linguistically:
   - Reconstruct the full sentence: `sentencePrefix` + `scrambledWords` in `correctOrder` sequence + `sentenceSuffix`.
   - Verify the reconstructed sentence is grammatically correct and natural Japanese.
   - Verify only one valid word order exists (no ambiguous arrangements).
   - Verify `scrambledWords` are NOT already in the correct order (must be shuffled).
   - Verify the `starPosition` marks a meaningful grammar point for testing.
   - Verify all vocabulary is within N5 scope.
   - Report any linguistically incorrect questions with an explanation.
6. Report final results — script validation + linguistic review summary.

## What the script checks per question (mechanical)

| Check | Rule |
|-------|------|
| `id` format | Must match `n5_grammer_sentence_building_XXX` (zero-padded sequential number) |
| `level` | Must be `"n5"` |
| `type` | Must be `"starQuestion"` |
| `sentencePrefix` | Must be a non-empty string |
| `sentenceSuffix` | Must be a non-empty string |
| `scrambledWords` | Must be an array of exactly 4 non-empty strings |
| `starPosition` | Must be an integer 0–3 |
| `correctOrder` | Must be a permutation of [0, 1, 2, 3] |

## Output

The script prints a report with PASS or FAIL per question and a summary line.
Exit code `0` = all passed, `1` = one or more failed.

After running, if the script passes proceed to linguistic review. If it fails, summarize failures so the user knows what to fix.

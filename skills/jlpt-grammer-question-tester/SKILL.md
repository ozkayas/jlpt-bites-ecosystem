---
name: jlpt-grammer-question-tester
description: "Validate JLPT grammar question JSON files produced by jlpt-n5-grammer-essential-grammer-question-creator. Use this skill when the user asks to test, validate, check, or verify JLPT grammar questions in JSON format. Checks three things: (1) schema/format correctness of all fields, (2) correctAnswer is a valid 0-based index within options, (3) question level is n5. Trigger on requests like soruları test et, validate questions, JSON dogrula, check grammar questions, or after generating questions with the creator skill."
---

# JLPT Grammar Question Tester

Validate JLPT N5 grammar question JSON using `scripts/validate.py`.

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
   - Reconstruct the full sentence by placing `options[correctAnswer]` into the blank `（　　）`.
   - Verify the reconstructed sentence is grammatically correct Japanese.
   - Verify the correct answer is the ONLY correct option among the 4 choices.
   - Verify all 3 distractors are genuinely wrong in this context but plausible enough as N5-level options.
   - Verify all vocabulary and kanji are within N5 scope.
   - Verify the `furigana` field has correct readings for all kanji.
   - Report any linguistically incorrect questions with an explanation.
6. Report final results — script validation + linguistic review summary.

## What the script checks per question (mechanical)

| Check | Rule |
|-------|------|
| `id` format | Must match `n5_essential_grammar_XXX` (zero-padded sequential number) |
| `level` | Must be `"n5"` |
| `type` | Must be `"sentenceCompletion"` |
| `sentence` | Must contain blank marker `（　　）` |
| `furigana` | Must contain at least one `<ruby>…<rt>…</rt></ruby>` tag |
| `blankPosition` | Must be a positive integer (≥ 1) |
| `options` | Must be an array of exactly 4 non-empty strings |
| `correctAnswer` | Must be an integer 0–3 |

## Output

The script prints a report with `✅ PASS` or `❌ FAIL` per question and a summary line.
Exit code `0` = all passed, `1` = one or more failed.

After running, if the script passes proceed to linguistic review. If it fails, summarize failures so the user knows what to fix.

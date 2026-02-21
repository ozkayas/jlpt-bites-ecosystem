---
name: jlpt-reading-passage-tester
description: "Validate JLPT N5 reading passage JSON files produced by jlpt-n5-reading-passage-creator. Use this skill when the user asks to test, validate, check, or verify reading passages in JSON format. Performs two passes: (1) mechanical schema validation via script, (2) linguistic review by Claude. Checks: id format, type, visual_type, sentences/framed_sentences structure, furigana ruby tags, question count, 4 options per question, exactly one correct answer. Trigger on requests like 'reading passage test et', 'validate passage JSON', 'okuma metni doğrula', 'check passage', or after generating passages with the creator skill."
---

# JLPT Reading Passage Tester

Validate JLPT N5 reading passage JSON using `scripts/validate.py`, then perform linguistic review.

## Workflow

1. Identify the JSON to validate — file path provided by user, or content in context.
2. If JSON is in context (not a file), write it to a temporary file first.
3. Run the mechanical validator:

```bash
# From a file
python3 <skill_dir>/scripts/validate.py <path/to/passages.json>

# From stdin
python3 <skill_dir>/scripts/validate.py --stdin <<'EOF'
{ ...json... }
EOF
```

4. If the script reports failures, summarize them and stop here.
5. **Linguistic review**: If all passages pass the script, read the JSON and verify each passage:
   - Read the full passage (sentences + framed_sentences in order) and verify it is natural, grammatically correct N5 Japanese.
   - Verify all vocabulary and kanji are within N5 scope (no N4+ patterns).
   - Verify each question is answerable ONLY from the passage text (not from general knowledge).
   - Verify the correct answer is actually correct and clearly supported by the passage.
   - Verify the 3 distractors are genuinely wrong but plausible (drawn from passage vocabulary).
   - Verify furigana is applied to every kanji word (and no kana is wrapped).
   - Report any linguistically incorrect passages with a specific explanation.
6. Report final results — script validation + linguistic review summary.

## What the Script Checks per Passage

| Check | Rule |
|-------|------|
| `id` format | Must match `n5_reading_(short\|mid)_NNN` |
| `type` | Must be `"short"` or `"mid"` |
| `visual_type` | Must be one of `letter`, `notice`, `memo`, `email`, `none` |
| `title` | Must be a non-empty string |
| `sentences` | Must be a non-empty array; each item needs `id`, `original`, `furigana`, `romaji` |
| `framed_sentences` | Must be an array (can be empty); same field rules as sentences |
| `questions` | Must be a non-empty array |
| Each question | Needs `id`, `text`, `furigana`, array of exactly 4 options |
| Each option | Needs `id`, `text`, `is_correct` |
| Correct answers | Exactly 1 option with `is_correct: true` per question |
| `question_count` | Must equal the actual number of questions |

## Output

The script prints PASS or FAIL per passage and a summary line.
Exit code `0` = all passed, `1` = one or more failed.

After the script passes, proceed to linguistic review. If it fails, summarize failures so the user knows what to fix.

---
name: jlpt-n5-grammer-essential-grammer-question-creator
description: Generate JLPT N5 grammar questions in a specific JSON format. Use this skill when the user asks to create, generate, or produce N5 grammar questions, sentence-completion exercises, or particle-fill-in-the-blank questions. Output is a JSON object containing a "questions" array with sentenceCompletion type items, each including Japanese sentence, furigana markup, 4 options, and the correct answer index. Trigger on requests like "N5 gramer sorusu üret", "create N5 grammar questions", "generate particle questions", or "JLPT N5 soru oluştur".
---

# JLPT N5 Grammar Question Creator

Generate N5-level sentence-completion questions as JSON.

## References

- **Output format & field rules**: See [references/json-schema.md](references/json-schema.md)
- **N5 grammar points and distractor pairs**: See [references/n5-grammar-points.md](references/n5-grammar-points.md) — read when selecting grammar targets or building distractors

## Workflow

1. Determine the grammar target(s) — from user request or source documents in context.
2. Read `references/json-schema.md` for field specifications.
3. Read `references/n5-grammar-points.md` when selecting particles/patterns or building distractors.
4. Generate each question:
   - Write a natural N5-level sentence with a single blank `（　　）`.
   - Add `<ruby>` furigana to every kanji word.
   - Choose 4 options: 1 correct + 3 plausible N5 distractors (use common distractor pairs from n5-grammar-points.md).
   - Set `correctAnswer` as the 0-based index of the correct option.
   - Set `id` as `n5_essential_grammar_XXX` where XXX is a zero-padded sequential number (e.g., 001, 002). Continue from the last existing ID in the file.
5. Append generated questions to the existing questions array in `backend/grammar/data/n5_essential_grammar.json`. Read the file first, then add new questions to the end of the `questions` array.
6. **Validate**: After saving, run the `jlpt-grammer-question-tester` skill to validate the JSON file. If any questions fail, fix them and re-run the tester until all pass.
7. **Upload prompt**: After all questions pass validation, ask the user whether to upload the changes to Firebase. If yes, run: `python3 backend/grammar/scripts/upload_grammar_questions.py n5 --type essential-grammar`
8. Output a summary of what was generated, validated, and (optionally) uploaded.

## Quality rules

- All vocabulary and kanji must be within N5 scope.
- Sentences should reflect real daily-life contexts.
- Distractors must be grammatically plausible in the sentence (wrong meaning, not obviously ungrammatical).
- `furigana` field: wrap every kanji word with `<ruby>漢字<rt>reading</rt></ruby>`; leave hiragana/katakana/particles unwrapped.
- Default quantity: 5 questions unless user specifies otherwise.

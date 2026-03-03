---
name: jlpt-n5-grammer-sentence-building-question-creator
description: Generate JLPT N5 sentence building (starQuestion) questions in JSON format. Use this skill when the user asks to create, generate, or produce N5 sentence building questions, word-order exercises, or scrambled sentence questions. Output is a JSON object containing a "questions" array with starQuestion type items, each including sentencePrefix, sentenceSuffix, 4 scrambledWords, starPosition, and correctOrder. Trigger on requests like "N5 cümle birleştirme sorusu üret", "create N5 sentence building questions", "generate word order questions", "JLPT N5 mondai2 soru oluştur", or "scrambled sentence questions".
---

# JLPT N5 Sentence Building Question Creator

Generate N5-level sentence building (starQuestion) questions as JSON.

## References

- **Output format & field rules**: See [references/json-schema.md](references/json-schema.md)
- **N5 grammar points and word-order rules**: See [references/n5-grammar-points.md](references/n5-grammar-points.md)

## Workflow

1. Determine the grammar target(s) — from user request or source documents in context.
2. Read `references/json-schema.md` for field specifications.
3. Read `references/n5-grammar-points.md` for word-order rules and scramble patterns.
4. Generate each question:
   - Write a natural N5-level sentence split into: `sentencePrefix` + 4 words + `sentenceSuffix`.
   - The 4 words in `scrambledWords` must be in a shuffled order (not the correct order).
   - Set `correctOrder` as the array of indices mapping scrambled positions to the correct sequence.
   - Set `starPosition` (0–3) indicating which slot in the correct order is the marked answer.
   - Set `id` as `n5_grammer_sentence_building_XXX` where XXX is a zero-padded sequential number. Continue from the last existing ID in the file.
5. Append generated questions to the existing questions array in `backend/grammar/data/n5_sentence_building.json`. Read the file first, then add new questions to the end of the `questions` array.
6. **Validate**: After saving, run the `jlpt-grammer-sentence-building-question-tester` skill to validate the JSON file. If any questions fail, fix them and re-run the tester until all pass.
7. **Upload prompt**: After all questions pass validation, ask the user whether to upload to Firebase. If yes, run: `python3 backend/grammar/scripts/upload_grammar_questions.py n5 --type sentence-building`
8. Output a summary of what was generated, validated, and (optionally) uploaded.

## Quality rules

- All vocabulary must be within N5 scope.
- Sentences should reflect real daily-life contexts.
- `scrambledWords` must NOT be in the correct order — always shuffle.
- `correctOrder` must be a valid permutation of [0, 1, 2, 3].
- The reconstructed sentence (prefix + ordered words + suffix) must be grammatically correct and natural.
- Ensure only one valid word order exists for each question.
- Default quantity: 5 questions unless user specifies otherwise.

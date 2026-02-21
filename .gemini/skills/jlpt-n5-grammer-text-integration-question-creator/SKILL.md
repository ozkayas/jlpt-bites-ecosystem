---
name: jlpt-n5-grammer-text-integration-question-creator
description: Generate JLPT N5 text-level grammar (Mondai 3) questions in JSON format. Use this skill when the user asks to create, generate, or produce N5 text-level grammar questions, text integration exercises, or "metin tamamlama" questions. Output is a JSON object with a "textFlow" type, containing "title", "textSegments", and "blanks" array. Trigger on requests like "N5 Mondai 3 sorusu üret", "create N5 text integration questions", "generate text-level grammar", or "JLPT N5 metin bütünleme sorusu oluştur".
---

# JLPT N5 Text Integration Question Creator

Generate N5-level text-level grammar (Mondai 3) questions as JSON.

## References

- **Output format & field rules**: See [references/json-schema.md](references/json-schema.md)
- **N5 grammar points and connectors**: See [references/n5-grammar-points.md](references/n5-grammar-points.md)

## Workflow

1. Determine the theme for the short text (e.g., daily routine, email, announcement, short story) from user request or context.
2. Read `references/json-schema.md` for `textFlow` field specifications.
3. Read `references/n5-grammar-points.md` when selecting connectors (shikashi, soshite, etc.) or verb forms.
4. Generate the question:
   - Create a title for the text.
   - Write a natural N5-level short text (approx. 100-200 characters).
   - Identify 3 points in the text for blanks (usually connectors, particles, or verb/adjective endings).
   - Split the text into `textSegments` array. The number of segments will be `number of blanks + 1`.
   - For each blank:
     - Choose 4 options: 1 correct + 3 plausible N5 distractors.
     - Set `blankNumber` based on the sequence in the file (last `blankNumber` + 1).
     - Set `position` (0, 1, 2...).
   - Set `id` as `n5_grammar_mondai3_XXX` where XXX is a zero-padded sequential number. Continue from the last existing ID in the file.
5. Append the generated question to the `questions` array in `backend/grammar/data/n5_text_integration.json`. Read the file first, then add the new question to the end.
6. **Validate**: After saving, run the `jlpt-n5-grammer-text-integration-question-tester` skill to validate the JSON file. If any questions fail, fix them and re-run the tester until all pass.
7. **Upload prompt**: After all questions pass validation, ask the user whether to upload to Firebase. If yes, run: `python3 backend/grammar/scripts/upload_grammar_questions.py n5 --type text-integration`
8. Output a summary of the text created and the grammar points tested.

## Quality rules

- All vocabulary and kanji must be within N5 scope.
- Text must be a coherent narrative, not disconnected sentences.
- Connectors (but, then, therefore) are primary targets for Mondai 3.
- Ensure the logical flow only allows one correct option for each blank.
- Default: 1 text with 3 blanks per request unless user specifies otherwise.

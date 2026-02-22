---
name: jlpt-n5-reading-passage-creator
description: "Generate JLPT N5 reading passages (short or mid type) in JSON format. Use this skill when the user asks to create, generate, or produce N5 reading passages, comprehension texts, or reading questions. Handles the full pipeline: Japanese core content generation, 5-language translation, file saving, and optional Firebase upload. Trigger on requests like 'N5 okuma metni üret', 'create N5 reading passage', 'short passage oluştur', 'mid passage yaz', 'generate reading comprehension', 'JLPT N5 okuma sorusu oluştur'."
---

# JLPT N5 Reading Passage Creator

Generate N5-level reading passages (core Japanese + 5-language translations).

## References

- **JSON schemas and field rules**: See [references/json-schema.md](references/json-schema.md)
- **N5 scope and quality rules**: See [references/n5-reading-guidelines.md](references/n5-reading-guidelines.md)

## Workflow

1. Determine passage type from user request: `short` (80–150 words, 1–2 questions) or `mid` (200–350 words, 2 questions). Default: `short`.
2. Read `references/json-schema.md` for exact field specifications.
3. Read `references/n5-reading-guidelines.md` for N5 vocabulary, grammar scope, and quality rules.
4. Read `backend/reading/data/n5_passages_{type}_core.json` to find the last ID number. New passage ID = `n5_reading_{type}_{NNN}` (next sequential number, zero-padded).
5. Generate the passage:
   - Write natural N5-level Japanese prose.
   - Decide `visual_type` (`notice`, `memo`, `letter`, `email`, `none`).
   - If `visual_type ≠ none`: put context text in `sentences`, boxed content in `framed_sentences`. Otherwise: use only `sentences`.
   - Add `furigana`: `<ruby>漢字<rt>reading</rt></ruby>` for every kanji word only.
   - Add `romaji` in Modified Hepburn.
   - Write questions (1–2 for short, 2 for mid) with 4 options each; exactly 1 `is_correct: true` per question.
   - Sentence IDs: s1, s2… continuous across `sentences` + `framed_sentences`.
6. Append new passage to `backend/reading/data/n5_passages_{type}_core.json`.
7. **Validate**: Run `jlpt-reading-passage-tester` skill on the file. Fix any failures, re-run until all pass.
8. **Generate translations** for all 5 languages (en, tr, de, fr, es):
   - Translate every sentence (both `sentences` and `framed_sentences`) naturally and idiomatically.
   - Add `mining_text` per sentence: localized grammar/chunk explanation + vocabulary list (see mining text headers in json-schema.md).
   - Translate question text and all 4 option texts.
9. **Distribute translations**: Append each language's translation entry to `backend/reading/data/n5_passages_{type}_translations_{lang}.json`.
10. **Upload prompt**: Ask the user whether to upload to Firebase. If yes:
    ```bash
    python3 backend/reading/scripts/upload_passages_v2.py n5
    ```
    Note: This uploads all N5 passages (short + mid). Existing passages are safely overwritten (Firestore uses set()); the new passage is added alongside them.
11. Output a summary: passage ID, type, question count, languages translated, upload status.

## Quality Rules

- All vocabulary and kanji within N5 scope.
- Questions must be answerable ONLY from the passage text.
- Exactly 1 correct option per question; 3 plausible distractors using passage vocabulary.
- Default: 1 passage per run unless user specifies more.

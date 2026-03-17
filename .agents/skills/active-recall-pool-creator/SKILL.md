---
name: active-recall-pool-creator
description: "Generate and maintain active_recall_pool.json for the vocabulary SRS active recall system. Use when the user asks to create, extend, regenerate, or improve active recall checkpoints, sentences, hints, or translations. Trigger on requests like 'active recall oluştur', 'yeni checkpoint ekle', 'grammar hints düzelt', 'active recall pool genişlet', 'create active recall questions', 'add checkpoint for 60 words'. Also use when reviewing or fixing quality issues in existing active recall content (poor hints, missing checkpoints, translation errors)."
---

# Active Recall Pool Creator

Generate checkpoint-based translation exercises for the vocabulary SRS module. Users learn N5 vocabulary via flashcards; at milestones (every 5 words learned) the system presents Japanese sentence-construction challenges.

## Output Target

`assets/data/vocabulary/active_recall_pool.json` in the jlpt-bites app repo.

## Workflow

1. **Read references** — Load [references/json-schema.md](references/json-schema.md) for the exact output format and quality rules.
2. **Read vocabulary source** — Load `jlpt-bites-ecosystem/backend/n5_vocabulary/data/n5_vocabulary.json` to see which words exist at each milestone.
3. **Determine scope** — From user request, decide:
   - **New pool from scratch**: Generate all checkpoints from cp_5 to cp_N (where N = total words, step 5).
   - **Extend existing**: Read current `active_recall_pool.json`, find the last checkpoint, continue from there.
   - **Fix/improve existing**: Read current pool, identify and fix quality issues.
4. **Generate content** — For each checkpoint, create 2-3 sentences following the quality rules in json-schema.md. Every sentence must only use vocabulary from words 1..learned_word_count.
5. **Validate** — Run the validation script:
   ```bash
   python3 .agent/skills/active-recall-pool-creator/scripts/validate_pool.py assets/data/vocabulary/active_recall_pool.json --vocab-source <path/to/n5_vocabulary.json>
   ```
6. **Fix any errors** reported by the validator, then re-run until clean.
7. **Report** — Summarize what was generated: checkpoint count, sentence count, languages covered.

## Critical Quality Rules (summary)

These are the most commonly violated rules. Full details in [references/json-schema.md](references/json-schema.md).

### grammar_hints must be real hints

**WRONG** (category label, useless):
```json
"grammar_hints": { "tr": "Yer sorma.", "en": "Asking about a location." }
```

**RIGHT** (actionable clue that helps the user construct the sentence):
```json
"grammar_hints": {
  "tr": "'Burası' = ここ, 'neresi' = どこ. Soru kalıbı: [yer]は どこですか。",
  "en": "'Here' = ここ, 'where' = どこ. Question pattern: [place]は どこですか。"
}
```

A hint must give the user partial vocabulary mappings, grammar patterns, or structural clues — never just restate the category of the question.

### Vocabulary scope enforcement

Checkpoint cp_N (learned_word_count = N) may only reference vocabulary from `n5_vocab_001` through `n5_vocab_N` (the first N words in order). Do not use words the user hasn't learned yet.

### Checkpoint regularity

Checkpoints must exist at every multiple of 5 (5, 10, 15, 20, ...) with no gaps.

# Active Recall Pool — JSON Schema & Quality Rules

## File Structure

```json
{
  "checkpoints": [
    {
      "id": "cp_5",
      "learned_word_count": 5,
      "sentences": [ ... ]
    },
    {
      "id": "cp_10",
      "learned_word_count": 10,
      "sentences": [ ... ]
    }
  ]
}
```

## Checkpoint Object

| Field | Type | Rule |
|-------|------|------|
| `id` | string | Format: `cp_N` where N = learned_word_count. Example: `cp_25` |
| `learned_word_count` | int | Multiple of 5. Must be sequential with no gaps (5, 10, 15, ...) |
| `sentences` | array | 2-3 sentence objects per checkpoint. Minimum 2. |

## Sentence Object

| Field | Type | Rule |
|-------|------|------|
| `id` | string | Format: `cpN_sM` where N = checkpoint number, M = sentence index (1-based). Example: `cp25_s2` |
| `prompts` | object | Source sentences in 6 languages. Keys: `tr`, `en`, `de`, `es`, `fr`, `ko` |
| `japanese_target` | string | The expected Japanese answer. Must use only hiragana, katakana, kanji from learned vocabulary, and punctuation. |
| `grammar_hints` | object | Actionable hints in 6 languages. Keys: `tr`, `en`, `de`, `es`, `fr`, `ko` |

## Language Keys

All `prompts` and `grammar_hints` objects must have exactly these 6 keys:
- `tr` — Turkish
- `en` — English
- `de` — German
- `es` — Spanish
- `fr` — French
- `ko` — Korean

No key may be empty or missing.

## Prompt Quality Rules

1. **Natural and contextual**: Prompts should be natural sentences a real person would say, not artificial grammar drills.
2. **Difficulty progression**: Early checkpoints (cp_5–cp_15) use simple greetings and single-clause sentences. Later checkpoints introduce compound sentences and more complex grammar.
3. **All prompts for a sentence must convey the same meaning** across all 6 languages. Translations must be natural in each language, not word-for-word calques.

## grammar_hints Quality Rules — CRITICAL

This is the most important quality dimension. Hints must help the user construct the Japanese sentence.

### What a good hint contains

A good hint provides **2-3 of these elements**:

1. **Key vocabulary mappings**: Direct word-to-word translations for the critical words in the sentence.
   - Example: `"'today' = きょう, 'weather' = てんき"`
2. **Grammar pattern**: The structural template the sentence follows.
   - Example: `"Pattern: [topic]は [description]です。"`
3. **Particle usage**: Which particles to use and where.
   - Example: `"Use は after the topic, を after the object."`
4. **Conjugation hint**: If a verb needs conjugation, indicate the form.
   - Example: `"Use the て-form of 行く → 行って"`
5. **Partial sentence scaffold**: Give part of the answer with blanks.
   - Example: `"きょうは _____ です。"`

### What a hint must NEVER be

- A category label: ~~"Asking about a location."~~ ~~"Daily greeting."~~ ~~"Polite introduction."~~
- A repetition of the prompt in different words
- An empty or trivially obvious statement
- The complete answer

### Hint examples by checkpoint level

**cp_5 (very basic):**
```json
"grammar_hints": {
  "tr": "'Merhaba' Japonca'da こんにちは olarak söylenir. Tek kelimelik ifade.",
  "en": "'Hello' in Japanese is こんにちは. Single-word expression.",
  "de": "'Hallo' auf Japanisch ist こんにちは. Einzelner Ausdruck.",
  "es": "'Hola' en japonés es こんにちは. Expresión de una sola palabra.",
  "fr": "'Bonjour' en japonais se dit こんにちは. Expression simple.",
  "ko": "'안녕하세요'는 일본어로 こんにちは입니다. 단일 표현."
}
```

**cp_20 (intermediate):**
```json
"grammar_hints": {
  "tr": "'Burası' = ここ, 'neresi' = どこ. Soru kalıbı: [yer]は どこですか。",
  "en": "'Here' = ここ, 'where' = どこ. Pattern: [place]は どこですか。",
  "de": "'Hier' = ここ, 'wo' = どこ. Muster: [Ort]は どこですか。",
  "es": "'Aquí' = ここ, 'dónde' = どこ. Patrón: [lugar]は どこですか。",
  "fr": "'Ici' = ここ, 'où' = どこ. Modèle: [lieu]は どこですか。",
  "ko": "'여기' = ここ, '어디' = どこ. 패턴: [장소]は どこですか。"
}
```

**cp_40+ (advanced for N5):**
```json
"grammar_hints": {
  "tr": "'Her zaman' = いつも, 'birlikte' = いっしょ. Kalıp: [sıklık] + [durum]です。",
  "en": "'Always' = いつも, 'together' = いっしょ. Pattern: [frequency] + [state]です。",
  "de": "'Immer' = いつも, 'zusammen' = いっしょ. Muster: [Häufigkeit] + [Zustand]です。",
  "es": "'Siempre' = いつも, 'juntos' = いっしょ. Patrón: [frecuencia] + [estado]です。",
  "fr": "'Toujours' = いつも, 'ensemble' = いっしょ. Modèle: [fréquence] + [état]です。",
  "ko": "'언제나' = いつも, '함께' = いっしょ. 패턴: [빈도] + [상태]です。"
}
```

## Vocabulary Scope Enforcement

Each checkpoint `cp_N` may only use words from the first N entries in `n5_vocabulary.json` (ordered by ID: `n5_vocab_001` through `n5_vocab_N`).

To check vocabulary scope:
1. Read n5_vocabulary.json and extract the first N word entries.
2. For each sentence in cp_N, verify that every kanji/word in `japanese_target` can be found among those N words' `word` or `reading` fields.
3. Common particles (は, が, を, に, で, と, の, も, か, へ, よ, ね), punctuation (。、), and basic copula (です, ます) are always allowed.
4. Hiragana-only words that appear in the first N entries are allowed.

## Sentence Design Guidelines

1. **2-3 sentences per checkpoint** — ensures enough practice without overwhelming.
2. **Vary sentence types** within a checkpoint — don't repeat the same pattern twice.
3. **Build on previous checkpoints** — later checkpoints can revisit earlier vocabulary in new combinations.
4. **Prefer practical, everyday sentences** — greetings, self-introduction, asking directions, shopping, time expressions.
5. **japanese_target must be in hiragana/katakana for N5** unless the kanji is explicitly in the learned vocabulary's `word` field.

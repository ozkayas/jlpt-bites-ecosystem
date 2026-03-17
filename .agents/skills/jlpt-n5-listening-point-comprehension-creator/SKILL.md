---
name: jlpt-n5-listening-point-comprehension-creator
description: "Generate JLPT N5 Listening Point Comprehension (Mondai 2 / selectText) questions by creating variations of source questions from clip folders. Reads a source question, performs surgical entity swap, generates 4 text options (1 correct + 3 distractors), and outputs question_data.json. Use when the user asks to 'create a point comprehension question', 'selectText soru uret', 'mondai 2 sorusu olustur', or 'listening metin secme sorusu yap'."
---

# JLPT N5 Listening Point Comprehension Creator (Mondai 2 / selectText)

You are an expert JLPT N5 examiner specializing in **Listening Mondai 2 (Point Comprehension / selectText)** questions. Your goal is to generate high-quality JLPT N5 questions where the listener hears a dialogue and selects the correct **text answer** from 4 Japanese options.

## Core Directives

1. **N5 Level Strictness:** Use only N5-level vocabulary and grammar. Refer to `references/n5-grammar-points.md` for the allowed list. Do NOT use grammar or vocabulary above N5 level.
2. **Variation, Not Copy:** Each generated question is a variation of a source question. Change entities (people, places, items, numbers, times) while preserving the underlying logic pattern and trap structure.
3. **4 Text Options Required:** Every question must have exactly 4 Japanese text options (`options` array). One is correct (`correct_option`, 0-indexed). The other 3 are plausible distractors derived from the dialogue.
4. **Options are Japanese text only.** No images. Options should be short phrases (3-8 words each), written in hiragana/katakana with minimal kanji.
5. **STOP FOR APPROVAL:** After generating the question JSON, display it to the user and WAIT for approval before saving.

---

## Source Data Location

```
backend/listening/data/selectText/
  001/                         <- Finished example (reference format)
    question_data.json
    audio.mp3
  clip_XXXXX/                  <- Raw source questions (5-6 per clip)
    data.json                  <- Contains questions[] array
    audio.mp3                  <- IGNORE
```

## Output Location

```
backend/listening/data/selectText/
  {next_id}/                   <- Zero-padded 3 digits: 002, 003, ...
    question_data.json         <- Your output
```

---

## Logic Patterns (Trap Strategies)

Based on analysis of 30 real JLPT N5 Point Comprehension questions, these are the 8 trap patterns used. Every question MUST use at least one.

### Pattern 1: Fikir Degistirme (Change of Mind) — Most common (~30%)
A plan is proposed, then rejected or modified. The correct answer is always the **final decision**.
- Dialogue flow: Teklif A -> Itiraz/Ret -> Alternatif B -> Kabul
- Key markers: `じゃなくて`, `でも`, `そうしましょう`, `それにします`, `それがいいですね`
- Distractors: The initially proposed option, the rejected alternative, an unrelated option from dialogue

### Pattern 2: Dikkat Dagitici Bilgi (Distractor Info) — ~20%
Multiple people's plans/situations are mentioned. The question asks about only ONE specific person.
- Dialogue flow: A says their plan, B says their plan, C says their plan
- Distractors: Other people's plans/situations

### Pattern 3: Duzeltme (Correction) — ~10%
Speaker says something, then immediately corrects it.
- Dialogue flow: "X var... hayir, X yok, Y var"
- Distractors: The uncorrected (wrong) information

### Pattern 4: Hesaplama (Calculation) — ~15%
Numbers from the dialogue must be combined (add/subtract/multiply) to get the answer.
- Question types: いくら, なんにん, なんまい, なんじ
- Distractors: Partial calculations, raw numbers from dialogue

### Pattern 5: Zaman Cikarimi (Time Inference) — ~10%
A date/time is not stated directly but must be inferred from relative expressions.
- Key words: つぎのひ, ～まえ, おととい, ～ご, ～あと
- Distractors: The reference time, wrong calculations

### Pattern 6: Olumsuz Eleme (Negative Elimination) — ~10%
Items/things that are NOT available or NOT allowed are listed. What remains is the answer.
- Key markers: ありません, だめ, ないでください, てはいけません
- Distractors: The eliminated/forbidden items

### Pattern 7: Siparis/Secim (Order/Selection) — ~5%
Customer asks for options, rejects some, selects one.
- Dialogue flow: "X var mi?" -> "Yok" -> "Y olsun"
- Distractors: Rejected or unavailable items

### Pattern 8: Neden/Sebep (Reason) — ~5%
Question asks why something happened. Multiple possible reasons are mentioned.
- Key word: どうして
- Distractors: Suggested but incorrect reasons

---

## Question Data Schema — Fat JSON (question.json)

Output format follows the multi-language "Fat JSON" architecture used across the JLPT Bites ecosystem.

```json
{
  "metadata": {
    "level": "N5",
    "topic": {
      "ja": "Japanese topic in hiragana",
      "tr": "Turkish", "en": "English", "de": "German", "fr": "French", "es": "Spanish", "ko": "Korean"
    }
  },
  "audio_url": null,
  "options": [
    "Japanese option 1",
    "Japanese option 2",
    "Japanese option 3",
    "Japanese option 4"
  ],
  "correct_option": 0,
  "transcriptions": {
    "ja": {
      "intro": "Setting + question sentence in hiragana",
      "dialogue": [
        { "speaker": "おとこのひと", "text": "Japanese dialogue line" }
      ],
      "question": "Question sentence repeated"
    },
    "tr": {
      "intro": "Turkish intro",
      "dialogue": [
        { "speaker": "Erkek", "text": "Turkish dialogue line" }
      ],
      "question": "Turkish question"
    },
    "en": { "intro": "...", "dialogue": [...], "question": "..." },
    "de": { "intro": "...", "dialogue": [...], "question": "..." },
    "fr": { "intro": "...", "dialogue": [...], "question": "..." },
    "es": { "intro": "...", "dialogue": [...], "question": "..." },
    "ko": { "intro": "...", "dialogue": [...], "question": "..." }
  },
  "analysis": {
    "vocabulary": [
      { "word": "Japanese word", "reading": "hiragana reading", "meanings": { "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." } }
    ],
    "grammar": [
      { "point": "Grammar pattern", "meanings": { "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." } }
    ]
  },
  "logic": {
    "tr": "Turkish explanation",
    "en": "English explanation",
    "de": "German explanation",
    "fr": "French explanation",
    "es": "Spanish explanation",
    "ko": "Korean explanation"
  }
}
```

### Speaker Labels Per Language

| Japanese (ja) | Turkish (tr) | English (en) | German (de) | French (fr) | Spanish (es) | Korean (ko) |
|---------------|-------------|-------------|------------|------------|-------------|------------|
| おとこのひと | Erkek | Man | Mann | Homme | Hombre | 남자 |
| おんなのひと | Kadın | Woman | Frau | Femme | Mujer | 여자 |
| おとこのがくせい | Erkek Öğrenci | Male Student | Student | Étudiant | Estudiante | 남학생 |
| おんなのがくせい | Kız Öğrenci | Female Student | Studentin | Étudiante | Estudiante | 여학생 |
| せんせい | Öğretmen | Teacher | Lehrer/in | Professeur | Profesor/a | 선생님 |
| てんいん | Görevli | Staff | Angestellte/r | Employé/e | Empleado/a | 직원 |
| いしゃ | Doktor | Doctor | Arzt/Ärztin | Médecin | Médico/a | 의사 |

### Schema Rules

| Field | Rule |
|-------|------|
| `metadata.level` | Always `"N5"` |
| `metadata.topic` | Multi-language object with `ja` + 6 UI languages |
| `audio_url` | Top-level, always `null` (filled later by upload script) |
| `options` | Exactly 4 items, Japanese text, short phrases |
| `correct_option` | 0-based index (0=first, 1=second, 2=third, 3=fourth) |
| `transcriptions.ja.intro` | Sets the scene + states the question. Hiragana. |
| `transcriptions.ja.dialogue` | 4-7 turns. Speaker labels in hiragana. |
| `transcriptions.{lang}.dialogue` | Same turns, speaker labels translated per language |
| `transcriptions.ja.question` | Repeats the question from the intro |
| `analysis.vocabulary` | 3-7 key N5 words with `reading` + 6-lang `meanings` |
| `analysis.grammar` | 1-3 grammar points with 6-lang `meanings` |
| `logic` | 6 language keys, each 2-3 sentences |

---

## Distractor Design Rules

1. **Every distractor must come from the dialogue.** No random options. Each wrong answer should be a word/phrase that was actually mentioned or implied in the conversation.
2. **Distractor sources by pattern:**

| Pattern | Distractor 1 | Distractor 2 | Distractor 3 |
|---------|-------------|-------------|-------------|
| Fikir Degistirme | First proposal | Second rejected option | Activity/item mentioned but not chosen |
| Dikkat Dagitici | Person A's answer | Person B's answer | Mixed/unrelated info |
| Duzeltme | Uncorrected info | Related but wrong detail | Plausible alternative |
| Hesaplama | Raw number from dialogue | Partial calculation | Different calculation error |
| Zaman Cikarimi | Reference time/date | Wrong offset | Mentioned but unrelated time |
| Olumsuz Eleme | Forbidden item 1 | Forbidden item 2 | Another forbidden item |

3. **Vary correct_option position.** Do not always put the correct answer in the same slot. Distribute across 0, 1, 2, 3.

---

## Workflow

### Step 1 — SELECT SOURCE

- If the user specifies a clip folder + question number, use that as the source.
- If not specified, list available clips in `backend/listening/data/selectText/clip_*/` and let the user choose.
- Read the source question from the clip's `data.json`.

### Step 2 — ANALYZE SOURCE

- Identify the logic pattern (which of the 8 patterns above).
- Identify the critical entities being tested (objects, people, times, places, numbers).
- Note the dialogue structure (number of turns, speaker roles).

### Step 3 — ENTITY SWAP

- Select new N5-level entities for the swap. Keep the same domain/category:
  - Food -> different food
  - Place -> different place
  - Time -> different time
  - Person/role -> same role structure
- Ensure the trap logic still works with new entities.
- The variation must be meaningfully different from the source (not just one word changed).

### Step 4 — WRITE DIALOGUE

- Write a new Japanese dialogue using only N5 grammar and vocabulary.
- Preserve the same logic pattern and trap structure.
- Keep dialogue length at 4-7 turns.
- Use appropriate speaker labels based on the setting.

### Step 5 — GENERATE OPTIONS

- Write exactly 4 Japanese text options.
- One option is the correct answer.
- Three options are distractors following the distractor design rules above.
- Options should be short phrases (3-8 words), parallel in structure.
- Randomize the position of the correct answer (vary `correct_option`).

### Step 6 — WRITE ANALYSIS, LOGIC & TRANSLATIONS

- Select 3-7 key vocabulary words from the dialogue. Provide `reading` (hiragana) and `meanings` in all 6 languages (tr, en, de, fr, es, ko).
- Identify 1-3 grammar points used. Provide `meanings` in all 6 languages.
- Write a logic explanation in all 6 languages that:
  - States why the correct answer is correct
  - Explains why each distractor is wrong
  - References specific dialogue lines
- Translate the `topic`, `intro`, `dialogue`, and `question` into all 6 languages.
- Use the Speaker Labels Per Language table for dialogue speaker names.

### Step 7 — DETERMINE OUTPUT ID

- List existing folders in `backend/listening/data/selectText/` that match the pattern `[0-9][0-9][0-9]`.
- Find the highest number.
- The new folder is `{max + 1}`, zero-padded to 3 digits.

### Step 8 — DISPLAY & WAIT FOR APPROVAL

- Display the complete `question_data.json` to the user.
- Show a summary:
  - Source: clip folder + question number
  - Pattern: which logic pattern was used
  - Correct answer: option text + index
  - Distractors: brief explanation of each
- **WAIT** for user approval. Do NOT save until the user says "Onayla", "OK", "Tamam", "Approved", etc.

### Step 9 — SAVE

- Create the output folder: `backend/listening/data/selectText/{id}/`
- Write `question.json` (Fat JSON format) to the folder.
- Confirm the file path to the user.

---

## Settings & Mekan (Scene) Library

Use these settings for the intro line:

| Setting | Intro Template |
|---------|---------------|
| Casual conversation | おとこのひとと　おんなのひとが　はなしています。 |
| University/School | だいがくで　おとこのがくせいと　おんなのがくせいが　はなしています。 |
| Teacher + Student | がっこうで　せんせいが　がくせいに　はなしています。 |
| Restaurant/Cafe | れすとらんで　おんなのひとと　おみせのひとが　はなしています。 |
| Hospital | びょういんで　いしゃと　おんなのひとが　はなしています。 |
| Shop/Market | おみせで　おとこのひとと　おみせのひとが　はなしています。 |
| Department store | でぱーとで　おとこのひとと　おみせのひとが　はなしています。 |
| Party | ぱーてぃーで　おとこのひとと　おんなのひとが　はなしています。 |

## Question Word Library

| Question Word | What It Asks | Example Intro Ending |
|---------------|-------------|---------------------|
| なにを しますか | Action/Plan | おとこのひとは　なにを　しますか。 |
| なにを かいますか | Purchase | おんなのひとは　なにを　かいますか。 |
| なにを たべますか / のみますか | Food/Drink | おんなのひとは　なにを　のみますか。 |
| どこで / どこへ | Place | ふたりは　どこで　あいますか。 |
| いつ | When | ふたりは　いつ　えいがを　みますか。 |
| なんじに | What time | おとこのひとは　なんじに　きましたか。 |
| どうして | Why | がくせいは　どうして　おくれましたか。 |
| どうやって | How/Method | おとこのひとは　どうやって　きましたか。 |
| なんにん | How many people | せんせいは　なんにん　きますか。 |
| いくら | How much (price) | おとこのひとは　いくら　はらいますか。 |
| なにを もっていきますか | What to bring | がくせいは　なにを　もっていきますか。 |

---

## Resources

| Resource | Purpose |
|----------|---------|
| `references/n5-grammar-points.md` | Allowed N5 grammar checklist |
| `references/n5-point-comprehension-patterns.md` | Detailed pattern examples from real questions |
| `backend/listening/data/selectText/001/question_data.json` | Reference output format |
| `backend/listening/data/selectText/clip_*/data.json` | Source questions for variation |

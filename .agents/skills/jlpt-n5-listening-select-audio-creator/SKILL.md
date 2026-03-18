---
name: jlpt-n5-listening-select-audio-creator
description: "Generate JLPT N5 Listening Mondai 3 (発話表現 / selectAudio) questions by inspecting a sample clip image, writing an N5-level scenario, and producing a derived-data.json with 3 spoken options (1 correct + 2 distractors). Use when the user asks to 'selectAudio soru üret', 'hatsuwa sorusu oluştur', 'expression question yap', or 'Mondai 3 sorusu oluştur'."
---

# JLPT N5 Listening Select Audio Creator (Mondai 3 / 発話表現)

You are an expert JLPT N5 examiner specializing in **Listening Mondai 3 (発話表現 / Expression Questions)**. The user sees a scene image with an arrow pointing to a character, hears the narrator describe the situation, listens to 3 spoken options, and selects what the arrow character should say.

## Core Directives

1. **N5 Level Strictness:** Use only N5-level vocabulary and grammar. No N4+ patterns.
2. **3 Options, Same Speaker:** All 3 options come from the arrow character's mouth — not a dialogue. Each option is a short utterance (1–2 sentences max).
3. **Distractor Design:** Use the 4 trap types (Rol, Yön, Register, Bağlam) to make distractors plausible but wrong.
4. **Image Prompt Without Arrow:** `image_prompt` describes the scene for Imagen 3 generation. The arrow is added manually by the user afterward.
5. **Image Style (MANDATORY):** All image prompts MUST use the manga/textbook style defined below. Do NOT use realistic or photographic style.
5. **STOP FOR APPROVAL:** Show the complete `derived-data.json` and wait. Do NOT save until user confirms.

---

## Source Data Location

```
backend/listening/data/selectAudio/
  sample_clips/
    clip_0e0duD8_LFE_01_20m20s_23m13s/   ← 5 PNGs + audio.mp3
    clip_ewHktqEnxTQ_01_18m12s_21m18s/
    clip_YBAJDQ_zDJg_01_19m21s_22m32s/
    clip_f9xIi2z5RVk_01_20m50s_23m36s/
    clip_sY7L5cfCWno_01_21m56s_24m41s/
    clip_CQ82yk3BC6c_01_20m07s_22m51s/
    clip_TYn4OgknPDc_01_21m21s_24m40s/
  001/
    question_data.json   ← Legacy reference (2-language format)
```

Each clip folder contains `1.png` through `5.png` — screenshots from the source JLPT video. Each screenshot shows a different scene with an arrow pointing at a character.

## Output Location

```
backend/listening/data/selectAudio/
  {id}/                  ← Zero-padded 3 digits: 002, 003, …
    derived-data.json    ← Your output
```

---

## Distractor Trap Types (発話表現)

| Trap Type | Japanese Name | Description | Example |
|-----------|--------------|-------------|---------|
| **Rol Karışıklığı** | 役割の混同 | The option belongs to the *other* person's role | `いかがですか` (staff offers) vs `おねがいします` (customer requests) |
| **Yön Karışıklığı** | 方向の混同 | Offer vs. request confusion (`～ましょう` inclusive vs `～てください` request) | `いっしょに いきましょう` vs `いっしょに いってください` |
| **Register Karışıklığı** | 丁寧度の混同 | Wrong politeness level for context | `ごちそうさまでした` (after eating) vs `いただきます` (before eating) |
| **Bağlam Karışıklığı** | 文脈の混同 | Correct-sounding phrase but wrong situation | Greeting someone leaving vs. arriving |

---

## derived-data.json Schema

```json
{
  "source_clip": "clip_0e0duD8_LFE_01_20m20s_23m13s/1.png",
  "metadata": {
    "level": "N5",
    "topic": {
      "ja": "きっさてんで　ちゅうもん",
      "tr": "Kafede sipariş",
      "en": "Ordering at a café",
      "de": "Bestellen im Café",
      "fr": "Commander dans un café",
      "es": "Pedir en una cafetería",
      "ko": "카페에서 주문하기"
    }
  },
  "correct_option": 0,
  "transcriptions": {
    "ja": {
      "intro": "きっさてんで　コーヒーを　のみたいです。みせの　ひとに　なんといいますか。",
      "options": [
        { "number": 1, "text": "コーヒーを　おねがいします。" },
        { "number": 2, "text": "コーヒーは　いかがですか。" },
        { "number": 3, "text": "コーヒーを　のみましょう。" }
      ],
      "question": "みせの　ひとに　なんといいますか。"
    },
    "tr": {
      "intro": "Bir kafede kahve içmek istiyorsunuz. Görevliye ne söylersiniz?",
      "options": [
        { "number": 1, "text": "Bir kahve lütfen." },
        { "number": 2, "text": "Kahve ister misiniz?" },
        { "number": 3, "text": "Kahve içelim." }
      ],
      "question": "Görevliye ne söylersiniz?"
    },
    "en": {
      "intro": "You are at a café and want to drink coffee. What do you say to the staff?",
      "options": [
        { "number": 1, "text": "A coffee, please." },
        { "number": 2, "text": "Would you like coffee?" },
        { "number": 3, "text": "Let's drink coffee." }
      ],
      "question": "What do you say to the staff?"
    },
    "de": { "intro": "...", "options": [...], "question": "..." },
    "fr": { "intro": "...", "options": [...], "question": "..." },
    "es": { "intro": "...", "options": [...], "question": "..." },
    "ko": { "intro": "...", "options": [...], "question": "..." }
  },
  "analysis": {
    "vocabulary": [
      {
        "word": "おねがいします",
        "reading": "おねがいします",
        "meanings": {
          "tr": "lütfen / sipariş kalıbı",
          "en": "please / may I have",
          "de": "bitte",
          "fr": "s'il vous plaît",
          "es": "por favor",
          "ko": "부탁합니다"
        }
      }
    ],
    "grammar": [
      {
        "point": "～を おねがいします",
        "meanings": {
          "tr": "Bir şey sipariş ederken kullanılır.",
          "en": "Used when ordering or requesting something.",
          "de": "Verwendet beim Bestellen von etwas.",
          "fr": "Utilisé pour commander quelque chose.",
          "es": "Se usa al pedir algo.",
          "ko": "무언가를 주문할 때 사용합니다."
        }
      }
    ]
  },
  "logic": {
    "tr": "Ok karakteri müşteridir, dolayısıyla sipariş kalıbı 'おねがいします' doğrudur. Seçenek 2 garsonun teklif kalıbıdır (Rol Karışıklığı). Seçenek 3 'birlikte yapalım' anlamı taşır (Yön Karışıklığı).",
    "en": "The arrow character is the customer, so the order pattern 'おねがいします' is correct. Option 2 is the staff's offer pattern (Role Confusion). Option 3 implies a joint action (Direction Confusion).",
    "de": "...",
    "fr": "...",
    "es": "...",
    "ko": "..."
  },
  "image_prompt": "Simple monochrome line art scene inside a cozy Japanese café. A customer sits at a counter looking at the menu board. A café staff member stands behind the counter smiling. Coffee cups and a coffee machine are visible on the counter. White background, no shading, JLPT exam illustration style. Do NOT include any arrows or numbered labels."
}
```

### Schema Rules

| Field | Rule |
|-------|------|
| `source_clip` | `"clip_name/N.png"` — clip folder name + image filename |
| `metadata.level` | `"N5"` (uppercase) |
| `metadata.topic` | Object: `ja` + 6 UI languages (tr, en, de, fr, es, ko) |
| `correct_option` | Integer **0, 1, or 2** (0-indexed → option number 1, 2, or 3) |
| `transcriptions.ja.intro` | Sets the scene + asks `なんといいますか`. Hiragana preferred. Must end with `か。` |
| `transcriptions.ja.options` | Exactly **3 items**, each `{"number": N, "text": "..."}`. All from the arrow character. |
| `transcriptions.ja.question` | Repeats the question from intro. Ends with `か。` |
| `transcriptions.{lang}` | Same structure for all 7 languages |
| `analysis.vocabulary` | 3–5 key N5 words: `word`, `reading` (hiragana), `meanings` (6-lang object) |
| `analysis.grammar` | 1–2 grammar points: `point`, `meanings` (6-lang object) |
| `logic` | 6 lang keys (tr, en, de, fr, es, ko). Each 2–3 sentences explaining correct + distractors. |
| `image_prompt` | English. Describes the scene for Imagen 3 without arrows or option numbers. Must follow the **Manga Style Template** below. |

---

## Workflow

### Step 1 — SELECT SOURCE

- If the user specifies a clip + image number (e.g. `clip_0e0duD8_LFE_01_20m20s_23m13s/1.png`), use that.
- If not specified, show the available clips in `backend/listening/data/selectAudio/sample_clips/` and ask the user to choose, or pick the first one randomly and announce your choice.
- Read the specified PNG image to visually analyze the scene.

### Step 2 — ANALYZE IMAGE

Read the image and extract:
- **Who is in the scene?** (genders, approximate roles: student, staff, customer, teacher, etc.)
- **Where are they?** (café, school, station, home, shop, etc.)
- **Arrow target:** Which character does the arrow point to? What is their role?
- **Situation:** What is happening or about to happen?

### Step 3 — DETERMINE SCENARIO TYPE

Map the scene to one of these common 発話表現 scenarios:

| Scenario | Typical correct expression |
|----------|---------------------------|
| Ordering food/drink | `～を おねがいします` |
| Asking to do something together | `～ましょう` |
| Requesting someone else | `～てください` / `～ていただけますか` |
| Expressing gratitude | `ありがとうございます` |
| Greeting / Farewell | `おはようございます` / `いってきます` / `ただいま` |
| Asking for permission | `～てもいいですか` |
| Offering help | `～ましょうか` |
| Apologizing | `すみません` / `もうしわけありません` |

### Step 4 — GENERATE VARIATION

Produce:
1. **Intro** (Japanese): N5-level situation description + `なんといいますか`
2. **3 Options** (Japanese): 1 correct + 2 distractors
   - Use exactly one trap type per distractor. Label which trap you used (internally, not in output).
   - Options should be similar in length and grammatical structure (parallel form).
3. **Question** (Japanese): Repeat of the question in the intro
4. **Translations** for all 6 UI languages (tr, en, de, fr, es, ko)
5. **Vocabulary** (3–5 words): key words from the options/intro with readings + 6-lang meanings
6. **Grammar** (1–2 points): grammar patterns used in the correct option / key distractors
7. **Logic** (6 languages): explain why correct is correct and why each distractor fails
8. **Image Prompt**: English description of the scene for Imagen 3 (NO arrows, NO option numbers)

### Step 5 — DETERMINE OUTPUT ID

- List existing folders in `backend/listening/data/selectAudio/` matching `[0-9][0-9][0-9]`.
- Find the highest ID. New ID = max + 1, zero-padded to 3 digits.
- Example: if `001/` exists, new ID is `002`.

### Step 6 — DISPLAY & WAIT FOR APPROVAL

Show the user:
1. The complete `derived-data.json`
2. A summary block:
   - **Source:** clip + image
   - **Scenario:** scene description
   - **Arrow target:** role + gender of the arrow character
   - **Correct option:** option text + index (0-based)
   - **Distractor 1:** trap type + reason it fails
   - **Distractor 2:** trap type + reason it fails

**WAIT** for approval (`Onayla`, `OK`, `Tamam`, `Approved`, etc.). Do NOT save before approval.

### Step 7 — SAVE

- Create folder: `backend/listening/data/selectAudio/{id}/`
- Write `derived-data.json` to the folder.
- Confirm the output path to the user.

---

## Distractor Writing Rules

1. **Each distractor must be plausible** — a student who didn't study carefully should consider it.
2. **Each distractor fails for exactly one reason** — use the trap type table.
3. **Vary correct_option position.** Don't always put the correct answer at index 0.
4. **Options must be parallel** — all the same speech register and roughly the same length.

### Distractor Examples by Trap Type

| Trap | Correct | Wrong (distractor) | Why it fails |
|------|---------|---------------------|-------------|
| Rol | `おねがいします` (customer) | `いかがですか` (staff offer) | Staff's line, not customer's |
| Yön | `いっしょに いきましょう` (mutual) | `いっしょに いきませんか` (invitation) | Invitation form, not self-inclusion |
| Register | `ありがとうございます` (polite) | `ありがとう` (casual, wrong context) | Too casual for the formal scene |
| Bağlam | `いってきます` (leaving) | `ただいま` (returning) | Wrong direction of movement |

---

## Image Style Guide (MANDATORY)

All `image_prompt` fields MUST use this manga/textbook style. This is the **approved character style** for all selectAudio questions.

### Manga Style Template

```
Simple manga-style line drawing, black and white. [Scene description with LEFT/RIGHT positioning of characters.]
[Character descriptions using: "simple round head", short/long hair, relevant clothing/props.]
[Background elements appropriate to the scene.]
Cartoon style with simple round faces, clean outlines, white background, no shading, no color, no text, no arrows.
Same style as JLPT N5 textbook manga illustrations.
```

### Key Style Keywords (always include)
- `Simple manga-style line drawing, black and white`
- `simple round head` (for each character)
- `Cartoon style with simple round faces`
- `clean outlines, white background, no shading, no color, no text, no arrows`
- `Same style as JLPT N5 textbook manga illustrations`

### What to AVOID
- `JLPT exam textbook line drawing` → produces realistic/Western faces
- `photorealistic`, `detailed`, `portrait` → wrong style
- Omitting `simple round head` → characters become too realistic

### Example (approved)
```
Simple manga-style line drawing, black and white. Two young people standing outside a Japanese restaurant.
On the LEFT, a young woman with simple round head and short hair smiles facing right.
On the RIGHT, a young man with simple round head smiles looking at the restaurant.
Japanese restaurant facade with lantern behind them.
Cartoon style with simple round faces, clean outlines, white background, no shading, no color, no text, no arrows.
Same style as JLPT N5 textbook manga illustrations.
```

---

## Resources

| Resource | Purpose |
|----------|---------|
| `backend/listening/data/selectAudio/sample_clips/` | Source images for scene analysis |
| `backend/listening/data/selectAudio/001/question_data.json` | Legacy reference (2-language format, do not copy format) |
| `references/n5-grammar-points.md` (in creator skills) | N5 grammar checklist |

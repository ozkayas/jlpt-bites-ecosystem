# N5 Reading Passage Guidelines

## Passage Types

| Type | Length | Questions | Typical Topics |
|------|--------|-----------|----------------|
| `short` | 80–150 words | 1–2 | Daily life anecdotes, simple narratives, short announcements |
| `mid` | 200–350 words | 2 | Longer narratives, diary entries, personal stories |

### Visual Formats (`visual_type`)

Use `visual_type` when the passage is presented as a physical document:

| Value | Use When |
|-------|----------|
| `notice` | Board announcement, school/workplace notice |
| `memo` | Handwritten or internal workplace note |
| `letter` | Personal or formal letter |
| `email` | Email message |
| `none` | Plain narrative / diary / no frame |

When `visual_type` is not `none`:
- Use `sentences` for context text appearing OUTSIDE the frame (e.g., "（会社で）学生がこの紙を見ました。")
- Use `framed_sentences` for text INSIDE the box

---

## N5 Vocabulary Scope

Stick to ~800–1000 most common words. Typical N5 vocabulary:

**People & Daily Life:** 先生, 学生, 友達, 家族, 父, 母, 兄, 姉, 弟, 妹
**Places:** 学校, 会社, 家, 駅, 公園, スーパー, レストラン, 図書館, 病院
**Time:** 今日, 明日, 昨日, 毎日, 朝, 昼, 夜, 来週, 先週, ～時, ～分
**Actions:** 行く, 来る, 食べる, 飲む, 見る, 聞く, 話す, 読む, 書く, 買う, 勉強する
**Adjectives:** 大きい, 小さい, 新しい, 古い, いい/よい, 悪い, 高い, 安い, きれいな, 静かな, 元気な
**Counters:** 一つ, 二つ… / ～枚, ～本, ～冊, ～人, ～時間
**Connectors:** そして, でも, から, だから, が (contrast)

### Kanji in N5 Scope

Time: 日, 月, 年, 時, 分, 前, 後, 今 | Numbers: 一～万, 円
Nature: 山, 川, 木, 雨, 天, 空, 花 | People: 人, 男, 女, 子, 父, 母, 先, 生, 学, 校
Places: 上, 下, 中, 右, 左, 北, 南, 東, 西, 国, 駅, 店

---

## Grammar Patterns

Use only N5-level grammar:

| Pattern | Example |
|---------|---------|
| ～ます / ～ません | 食べます、行きません |
| ～ました / ～ませんでした | 見ました、来ませんでした |
| ～ている | 読んでいます |
| ～てください | 書いてください |
| ～たい | 行きたいです |
| ～から (reason) | 寒いから、コートを着ます |
| ～が (contrast) | 好きですが、高いです |
| AはBより～ | 日本語は英語より難しいです |
| Nのあとで | 食べたあとで |
| Nのまえに | 寝るまえに |
| ～でしょう | 明日は雨でしょう |

---

## Quality Rules

### Passage
- All vocabulary and kanji must be within N5 scope (no N4+ patterns/kanji).
- Sentences should reflect real daily-life contexts (school, work, home, shopping, nature).
- Natural Japanese: avoid unnatural word order or overly formal/literary expressions.
- `mid` passages may have a richer narrative arc (morning → day → evening, cause → effect).
- Use proper sentence spacing with spaces between clauses in `short` passages (matching real JLPT style).

### Questions
- Exactly 1 correct answer per question; 3 plausible distractors.
- Question must be answerable ONLY from the passage text (not from general knowledge).
- Distractors should use words from the passage in misleading combinations.
- `short` passages: 1–2 questions; `mid` passages: 2 questions.
- **DO NOT use circled numbers (①, ②, ③, etc.) in question text or furigana** — questions should have plain text only.

### Furigana
- Wrap EVERY kanji word with `<ruby>漢字<rt>reading</rt></ruby>`.
- Do NOT wrap hiragana, katakana, particles, or punctuation.
- Proper nouns (names, place names) must also have furigana.

### Romaji
- Modified Hepburn system.
- Long vowels: `aa`, `ii`, `uu`, `ee`, `oo` (or ā, ī, ū, ē, ō).
- Double consonants: `kk`, `tt`, `ss` etc.
- Sentence-final particles: capitalize first word of sentence only.

# selectText Modülü — Claude Kuralları

## Modül Amacı

Bu modül, JLPT N5 Listening **"Select Text"** soru tipini barındırır.
Kullanıcı bir diyalog dinler ve sorulan soruya uygun **metin seçeneğini** seçer (4 seçenek, Japonca metin).

---

## Klasör Yapısı

```
backend/listening/data/selectText/
  001/
    question.json        ← Soru verisi — Fat JSON (7 dil, Firebase-ready)
    question_data.json   ← Legacy tek-dil format (migration öncesi)
    tts_script.json      ← TTS ses üretim scripti
    audio.mp3            ← Dinleme sesi
  002/
    ...
  CLAUDE.md             ← Bu dosya
  migrate_to_fat_json.py ← Legacy → Fat JSON dönüşüm scripti
```

### Doküman ID Kuralı
Sequential, zero-padded 3 hane: `001`, `002`, `003`…

---

## question.json Şeması (Fat JSON — 7 Dil)

```json
{
  "metadata": {
    "level": "N5",
    "topic": { "ja": "...", "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." }
  },
  "audio_url": null,
  "options": ["Japonca seçenek 1", "Japonca seçenek 2", "Japonca seçenek 3", "Japonca seçenek 4"],
  "correct_option": 1,
  "transcriptions": {
    "ja": { "intro": "...", "dialogue": [{ "speaker": "おとこのひと", "text": "..." }], "question": "..." },
    "tr": { "intro": "...", "dialogue": [{ "speaker": "Erkek", "text": "..." }], "question": "..." },
    "en": { "..." }, "de": { "..." }, "fr": { "..." }, "es": { "..." }, "ko": { "..." }
  },
  "analysis": {
    "vocabulary": [
      { "word": "japonca kelime", "reading": "hiragana", "meanings": { "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." } }
    ],
    "grammar": [
      { "point": "～ます", "meanings": { "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." } }
    ]
  },
  "logic": { "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." }
}
```

### Önemli Alan Notları

| Alan | Açıklama |
|------|----------|
| `correct_option` | 0-tabanlı index (`0`=ilk seçenek, `1`=ikinci seçenek, ...) |
| `options` | Tam olarak 4 Japonca metin seçeneği |
| `audio_url` | Top-level. Upload öncesi `null`, sonrasında Firebase public URL |
| `transcriptions` | 7 dil: ja, tr, en, de, fr, es, ko. Her dilde intro + dialogue + question |
| `analysis.vocabulary` | `word` + `reading` + 6-dil `meanings` |
| `analysis.grammar` | `point` + 6-dil `meanings` |
| `logic` | 6 dilde (tr, en, de, fr, es, ko) cevap açıklaması |

---

## Firebase Yapısı (Hedef)

- **Firestore Collection:** `n5_listening_select_text_questions`
- **Storage Path:** `listening/selectText/{id}/audio.mp3`
- **Document ID:** `001`, `002`, `003`…

---

## Soru Tipi Özellikleri

- **Seçenekler Japonca metin** olmalı (görsel yok, resim yok)
- Diyalog genellikle 2 konuşmacı arasında geçer
- Soru her zaman diyalogda geçen bir eylemi, planı veya durumu sorar
- Dikkat dağıtıcı (distractor) bilgiler diyalogda kasıtlı olarak yer alır
- N5 seviyesi: hiragana/katakana ağırlıklı, az kanji

---

### Kullanılabilir Agent Yetenekleri (Skills)
- `jlpt-n5-listening-point-comprehension-creator`: Kaynak soruların varyasyonlarını üreterek yeni Point Comprehension soruları oluşturur.

---

## Yapılacak Çalışmalar

> Bu alan, modüldeki aktif geliştirme sürecini takip eder.

- [x] Yeni soru üretimi (30 soru, 002-031)
- [x] TTS audio üretimi (31 MP3, ~9 MB)
- [x] Multi-language (Fat JSON) desteği — `question.json` 7 dil
- [x] Upload script yazımı
- [x] Firebase entegrasyonu (31 soru, `n5_listening_select_text_questions`)

# JLPT Reading Passages — Backend

This folder manages JLPT N5 reading passages: extraction, translation, and Firebase upload.

---

## Klasör Yapısı

```
backend/reading/
├── data/                          # JSON veri dosyaları
│   ├── n5_passages_short_core.json          # Kısa metin (短文) — Japonca içerik
│   ├── n5_passages_mid_core.json            # Orta metin (中文) — Japonca içerik
│   ├── n5_passages_short_translations_en.json
│   ├── n5_passages_short_translations_tr.json
│   ├── n5_passages_short_translations_de.json
│   ├── n5_passages_short_translations_fr.json
│   ├── n5_passages_short_translations_es.json
│   ├── n5_passages_mid_translations_*.json  # (aynı diller, mid için)
│   └── n5_translations_to_distribute.json   # Staging: dağıtılmayı bekleyen çeviriler
├── prompts/
│   ├── step1_core_extraction.md   # Adım 1: Japonca içerik çıkarımı (OCR)
│   └── step2_translation_mining.md # Adım 2: Çeviri ve dil analizi
└── scripts/
    ├── upload_passages_v2.py      # Firebase upload scripti
    ├── split_json_data.py         # Monolitik JSON'u ayıran yardımcı script
    ├── upload.sh                  # Bash wrapper (eski)
    └── requirements.txt
```

---

## Soru Tipleri (JLPT N5)

| Tip | Kodu | Uzunluk | Soru Sayısı | İçerik |
|-----|------|---------|-------------|--------|
| Kısa metin | `short` | ~80–150 kelime | 1–2 | Günlük anlatılar, notlar, duyurular, mesajlar |
| Orta metin | `mid` | ~200–350 kelime | 2 | Daha uzun anlatılar, günlükler |

> **Not:** Framed içerik (duyuru, memo, mektup, e-posta), ayrı bir JLPT tipi değil; `visual_type` alanıyla gösterilir. `type` her zaman `short` veya `mid` olur.

---

## ID Formatı

```
n5_reading_{type}_{NNN}
```

Örnekler:
- `n5_reading_short_001`, `n5_reading_short_009`
- `n5_reading_mid_001`

Yeni passage eklenirken ilgili tip dosyasındaki son ID'nin devamından numaralandırılır.

---

## Dosya Yapısı: Core JSON

`n5_passages_{type}_core.json` dosyaları yalnızca Japonca içeriği saklar:

```json
{
  "passages": [
    {
      "id": "n5_reading_short_001",
      "title": "日本語クラスのお知らせ",
      "visual_type": "notice",   // "letter" | "memo" | "email" | "notice" | "none"
      "type": "short",           // "short" | "mid"
      "question_count": 1,
      "created_at": "2026-02-03T18:41:48Z",
      "sentences": [             // Çerçeve dışındaki bağlam cümleleri
        {
          "id": "s1",
          "original": "（大学で）",
          "furigana": "（<ruby>大学<rt>だいがく</rt></ruby>で）",
          "romaji": "(Daigaku de)"
        }
      ],
      "framed_sentences": [      // Çerçeve (kutu) içindeki asıl metin; yok ise []
        { "id": "s3", "original": "...", "furigana": "...", "romaji": "..." }
      ],
      "questions": [
        {
          "id": "q1",
          "text": "...",
          "furigana": "...",
          "romaji": "...",
          "options": [
            { "id": "opt1", "text": "...", "furigana": "...", "is_correct": false, "romaji": "..." },
            { "id": "opt2", "text": "...", "furigana": "...", "is_correct": true,  "romaji": "..." },
            { "id": "opt3", "text": "...", "furigana": "...", "is_correct": false, "romaji": "..." },
            { "id": "opt4", "text": "...", "furigana": "...", "is_correct": false, "romaji": "..." }
          ]
        }
      ]
    }
  ]
}
```

**Sentence ID sıralaması:** `sentences` listesinde s1'den başlar, `framed_sentences` devam eder (ör. sentences s1–s2 ise framed_sentences s3'ten başlar).

---

## Dosya Yapısı: Translation JSON

`n5_passages_{type}_translations_{lang}.json` dosyaları her dil için ayrı tutulur:

```json
{
  "passages": [
    {
      "id": "n5_reading_short_001",
      "sentences": {
        "s1": { "translation": "...", "mining_text": "..." },
        "s3": { "translation": "...", "mining_text": "..." }
      },
      "questions": {
        "q1": {
          "text": "...",
          "options": {
            "opt1": "...",
            "opt2": "...",
            "opt3": "...",
            "opt4": "..."
          }
        }
      }
    }
  ]
}
```

Desteklenen diller: `en`, `tr`, `de`, `fr`, `es`

---

## Firestore Yapısı

```
reading_contents/{level}_reading/passages/{passage_id}/
  ├── [metadata fields: id, title, visual_type, type, framed_sentences, ...]
  ├── sentences/ (subcollection)
  │     └── {sentence_id}/ → { original, furigana, romaji, order }
  ├── questions/ (subcollection)
  │     └── {question_id}/ → { text, furigana, romaji, options[], order }
  └── translations/ (subcollection)
        └── {lang}/ (document)
              ├── sentences/ (subcollection) → { translation, mining_text }
              └── questions/ (subcollection) → { text, options{} }
```

---

## Üretim Akışı (Workflow)

### Adım 1 — Japonca İçerik Çıkarımı

Sınav görseli → Claude'a `prompts/step1_core_extraction.md` promptu ile verilir.
- Çıktı: tek bir passage JSON nesnesi (id boş `""`)
- ID belirleme: ilgili tip dosyasındaki son ID'nin devamı atanır (ör. short dosyasında son `short_009` varsa → `short_010`)
- Çıktı, `n5_passages_{type}_core.json` dosyasının `passages` dizisine eklenir

### Adım 2 — Çeviri ve Dil Analizi

`prompts/step2_translation_mining.md` promptu ile her cümle çevrilir ve dil analizi (mining_text) üretilir.
- Çıktı, `n5_translations_to_distribute.json` dosyasına staging olarak yazılır
- Oradan her dil için `n5_passages_{type}_translations_{lang}.json` dosyasına dağıtılır

### Adım 3 — Firebase Upload

```bash
# Tüm tipleri ve dilleri yükle:
python3 scripts/upload_passages_v2.py n5

# Sadece core içerik:
python3 scripts/upload_passages_v2.py n5 --core-only

# Sadece çeviriler:
python3 scripts/upload_passages_v2.py n5 --translations-only

# Belirli dil(ler):
python3 scripts/upload_passages_v2.py n5 --languages en tr
```

---

## Mevcut Veri (N5)

| Tip | Dosya | Passage Sayısı |
|-----|-------|---------------|
| short | `n5_passages_short_core.json` | 9 (short_001–short_009) |
| mid | `n5_passages_mid_core.json` | 1 (mid_001) |

---

## Gereksinimler

```bash
pip install -r scripts/requirements.txt
```

Firebase service account key: `backend/service-account-key.json`

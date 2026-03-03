# N5 Vocabulary Modülü

Bu klasör, JLPT N5 kelime verisinin tamamını barındırır: kaynak JSON, doğrulama, ses üretimi ve Firebase yükleme.

---

## Klasör Yapısı

```
backend/n5_vocabulary/
├── data/
│   └── n5_vocabulary.json        ← Tek kaynak (712 kelime)
├── scripts/
│   ├── README.md                 ← Script detayları (bu dosya değil, detay için oraya bak)
│   ├── generate_and_upload_audio.py
│   ├── upload_n5_vocabulary.py
│   └── upload_vocabulary_index.py
└── venv/                         ← Python sanal ortamı (firebase-admin)
```

---

## Kaynak Veri: `n5_vocabulary.json`

Tüm kelimeler bu tek dosyada tutulur. Firestore bu dosyadan türetilir — kaynak her zaman burasıdır.

Her kelime şu alanları içerir:

```json
{
  "id": "n5_vocab_001",
  "word": "食べる",
  "reading": "たべる",
  "romaji": "taberu",
  "tag": "動詞",
  "translations": { "en": "...", "tr": "...", "de": "...", "es": "...", "fr": "..." },
  "audioUrl": "https://storage.googleapis.com/.../n5_vocab_001.mp3",
  "sentences": [
    {
      "ja": "毎日ご飯を食べます。",
      "furigana": "毎<ruby>日<rt>にち</rt></ruby>ご<ruby>飯<rt>はん</rt></ruby>を<ruby>食<rt>た</rt></ruby>べます。",
      "romaji": "Mainichi gohan o tabemasu.",
      "translations": { "en": "...", "tr": "...", "de": "...", "es": "...", "fr": "..." },
      "audioUrl": "https://storage.googleapis.com/.../n5_vocab_001_s1.mp3"
    }
  ]
}
```

**Furigana kuralları:**
- `<rt>` içinde **yalnızca hiragana** kullanılır — Latin harf kesinlikle giremez
- Kanji okunaklı (okurigana) parçalar ruby tag'ının **dışında** kalır: `<ruby>食<rt>た</rt></ruby>べます`
- Hiragana/katakana sözcükler olduğu gibi yazılır, ruby tag'ı kullanılmaz

---

## Veri Doğrulama (Test)

Veriyi değiştirdikten sonra mutlaka **n5-vocabulary-tester** skill'i çalıştır:

```
/n5-vocabulary-tester
```

veya Claude'a söyle: _"n5_vocabulary.json'u test et"_

### Skill ne kontrol eder?

**Pass 1 — Mekanik (script ile):**
| Kontrol | Açıklama |
|---------|----------|
| Gerekli alanlar | `id`, `word`, `reading`, `romaji`, `tag`, `translations`, `sentences` hepsi olmalı |
| ID formatı | `n5_vocab_NNN` formatı, tekrar yok |
| Tag değerleri | `動詞 名詞 形容詞 副詞 表現` dışında değer kabul edilmez |
| Çeviri dilleri | `en tr de es fr` — tüm diller, hiçbiri boş değil |
| Cümle alanları | `ja`, `furigana`, `romaji`, `translations` hepsi olmalı |
| `<ruby>/<rt>` dengesi | Açılan her tag kapatılmalı |
| **`<rt>` Latin harf kontrolü** | `<rt>` içinde `a-z A-Z` karakteri bulunursa hata verir — yalnızca hiragana/katakana kabul edilir |
| Romaji kontrolü | Romaji alanı İngilizce/Türkçe çeviri gibi görünüyorsa uyarır |

**Pass 2 — Semantik (Claude ile):**
- Her tag'dan rastgele kelimeler örneklenir
- `reading`, `romaji`, Japonca cümle kalitesi, furigana doğruluğu, çeviriler gözden geçirilir

### Tester script'ini doğrudan çalıştırmak için:

```bash
python3 ~/.claude/skills/n5-vocabulary-tester/scripts/validate_vocabulary.py \
  backend/n5_vocabulary/data/n5_vocabulary.json
```

---

## Firebase'e Yükleme

### Gereksinim

```bash
# venv zaten hazır:
backend/n5_vocabulary/venv/bin/python3 <script>

# venv yoksa kur:
python3 -m venv backend/n5_vocabulary/venv
backend/n5_vocabulary/venv/bin/pip install firebase-admin gtts
```

`backend/service-account-key.json` dosyası mevcut olmalıdır.

---

### Yükleme Sırası

```
1. generate_and_upload_audio.py   → ses üret + Storage'a yükle + JSON'daki audioUrl'leri doldur
2. upload_n5_vocabulary.py        → güncel JSON'u Firestore'a yaz
3. upload_vocabulary_index.py     → Flutter bootstrap index'ini güncelle
```

**Sadece kelime verisi değiştiyse** (furigana, romaji, çeviri, cümle), ses yeniden üretmeye gerek yok — doğrudan 2. adımdan başla.

---

### Script 1: `generate_and_upload_audio.py`

gTTS ile Japonca ses üretir, Firebase Storage'a yükler, `n5_vocabulary.json`'daki `audioUrl` alanlarını günceller. **Firestore'a dokunmaz.**

```bash
cd backend/n5_vocabulary/scripts
../venv/bin/python3 generate_and_upload_audio.py --dry-run        # önizle
../venv/bin/python3 generate_and_upload_audio.py                  # tümünü üret
../venv/bin/python3 generate_and_upload_audio.py --words-only     # sadece kelimeler
../venv/bin/python3 generate_and_upload_audio.py --sentences-only # sadece cümleler
../venv/bin/python3 generate_and_upload_audio.py --force          # mevcut seslerin üzerine yaz
```

**Storage yolları:**
```
sounds/n5_vocabulary/words/{word_id}.mp3
sounds/n5_vocabulary/sentences/{word_id}_s1.mp3
```

---

### Script 2: `upload_n5_vocabulary.py`

`n5_vocabulary.json`'daki her kelimeyi `n5_vocabulary/{word_id}` Firestore dokümanına yazar.

**Önemli davranışlar:**
- **Her çalıştırma tam overwrite'tır.** 712 kelimenin tamamı Firestore'a yazılır (400'lük batch'ler halinde).
- Versiyon karşılaştırması veya diff yapılmaz — JSON ne içeriyorsa Firestore'a o yazılır.
- JSON'da olmayan eski Firestore dokümanları otomatik silinmez.

```bash
cd backend/n5_vocabulary/scripts
../venv/bin/python3 upload_n5_vocabulary.py --dry-run   # önizle (Firestore'a yazmaz)
../venv/bin/python3 upload_n5_vocabulary.py             # tümünü yükle
../venv/bin/python3 upload_n5_vocabulary.py --tag 動詞  # sadece belirli tag
```

---

### Script 3: `upload_vocabulary_index.py`

Flutter uygulaması açılışta tüm 712 kelimeyi yüklemek yerine tek hafif doküman okur. Bu script o dokümanı oluşturur.

- **Firestore path:** `vocabulary_meta/n5_vocabulary`
- **İçerik:** Her kelime için yalnızca `{id, word, reading, tag}` (~20 KB, koleksiyonun tam hali 485 KB)
- Her çalıştırmada tamamen overwrite edilir.

```bash
cd backend/n5_vocabulary/scripts
../venv/bin/python3 upload_vocabulary_index.py --dry-run
../venv/bin/python3 upload_vocabulary_index.py
```

---

## Firebase Yapısı

| Servis | Path | İçerik |
|--------|------|--------|
| Firestore | `n5_vocabulary/{word_id}` | Tam kelime dokümanı (712 adet) |
| Firestore | `vocabulary_meta/n5_vocabulary` | Bootstrap index (id, word, reading, tag) |
| Storage | `sounds/n5_vocabulary/words/{id}.mp3` | Kelime sesi |
| Storage | `sounds/n5_vocabulary/sentences/{id}_s1.mp3` | Cümle sesi |

---

## Geçmiş Düzeltmeler

| Tarih | Kapsam | Sorun | Çözüm |
|-------|--------|-------|-------|
| 2026-03 | n5_vocab_151–714 (562 kelime) | `furigana` ve `romaji` alanları tamamen eksik | Gemini API ile otomatik üretildi |
| 2026-03 | n5_vocab_074–150 (75 kelime) | `<rt>` içinde Latin harf (romaji) kullanılmış | Gemini API ile hiragana'ya dönüştürüldü |
| 2026-03 | n5_vocab_150 | Cümle kelimeyle alakasız (靴下 için katakana cümlesi yazılmış) | Doğru cümleyle değiştirildi |
| 2026-03 | n5_vocab_489 | `<ruby>幾<rt>いくら</rt></ruby>` — okurigana yanlış kapsama dahil | `<ruby>幾<rt>いく</rt></ruby>ら` olarak düzeltildi |

Bu düzeltmelerin ardından **n5-vocabulary-tester** skill'ine `<rt>` içinde Latin harf kontrolü eklendi.

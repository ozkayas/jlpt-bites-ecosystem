# selectImage — JLPT Bites Dinleme Modülü

## Bu klasör ne için?

Bu klasör, **JLPT Bites** mobil uygulamasının "Resim Seç" dinleme soruları için gereken içeriklerin üretildiği ve hazırlandığı yerdir.

Uygulama kodunun kendisi burada değildir. Burada yalnızca şunlar vardır:
- Ham veri dosyaları (ses, görsel, JSON)
- İçerik üretim araçları (script ve pipeline)
- Firebase'e yüklenmeye hazır soru verileri

---

## Uygulamada bu soru türü nasıl görünür?

Kullanıcıya kısa bir Japonca konuşma (diyalog) dinletilir. Ardından tek bir görsel sunulur; bu görselde 1–4 arası numaralı konumlar veya paneller vardır. Kullanıcı diyaloğa göre doğru numarayı seçer. (Görsel türüne göre farklılık gösterir: 4 ayrı panelli grid, tek sahnede numaralı konumlar ya da numaralı harita.)

Mobil uygulama, soruları Firebase'den çeker:
- **Ses dosyası** → Firebase Storage'dan oynatılır
- **Görsel** → Firebase Storage'dan yüklenir
- **Soru metni, doğru cevap, analiz bilgileri** → Firestore'dan okunur

---

## Klasör Yapısı

```
selectImage/
│
├── README.md                          ← Bu dosya
│
├── 001/                               ← Elle hazırlanmış soru (eski format, artık kullanılmıyor)
│   └── data.json
│
└── listening-youtube-data/            ← YouTube kaynaklı soru üretim sistemi (aktif)
    │
    ├── input.json                     ← Hangi YouTube videosundan, hangi zaman aralıklarını kesmek istiyorsun
    ├── pipeline.py                    ← YouTube videoyu indir, belirtilen aralıkları ses dosyasına dönüştür
    ├── run.sh                         ← pipeline.py'yi sanal ortamla çalıştıran kısayol
    ├── requirements.txt               ← pipeline.py'nin Python bağımlılıkları
    ├── venv/                          ← Python 3.13 sanal ortamı (kurulu, hazır)
    │
    ├── source_audio/                  ← YouTube'dan indirilen tam ses dosyası (pipeline çıktısı)
    ├── config/
    │   └── n5_kanji.json              ← N5 seviyesi kanji listesi (pipeline tarafından kullanılır)
    ├── logs/                          ← pipeline.py'nin çalışma logları
    │
    ├── clips/                         ← Pipeline'ın kestiği ham ses klipleri
    │   └── clip_NN_XXmYYs_XXmYYs/
    │       ├── audio.mp3              ← Kesilmiş ses
    │       └── .done_slice            ← "Bu klip kesildi" işaretçisi (pipeline tekrar çalışırsa atlar)
    │
    ├── tobeprocessed/                 ← Soru üretimi için seçilmiş ve hazırlanmış klipler (Claude bekliyor)
    │   └── clip_NN_XXmYYs_XXmYYs/
    │       ├── audio.mp3
    │       ├── data.json              ← Sen yazarsın: transkripsiyon ve konu bilgisi
    │       └── .done_slice
    │
    └── processed/                     ← Soru üretimi tamamlanmış, Firebase'e yüklenmeye hazır klipler
        └── clip_NN_XXmYYs_XXmYYs/
            ├── audio.mp3              ← Orijinal ses
            ├── variation-audio.wav    ← Claude'un TTS ile ürettiği varyasyon sesi
            ├── image.webp             ← Claude'un AI ile ürettiği 4 panelli soru görseli (WebP, max 700px)
            ├── data.json              ← Ham transkripsiyon verisi
            ├── derived-data.json      ← Claude'un ürettiği zenginleştirilmiş analiz verisi
            └── question.json          ← Firebase'e yüklenecek nihai soru verisi
```

---

## Kullanılabilir Agent Yetenekleri (Skills)

Bu modülde Claude (Agent) tarafından kullanılan özel yetenekler şunlardır:

- `jlpt-n5-listening-variation-creator`: Ham diyalog verisinden görsel promptları, kelime analizleri ve mantık akışı (`derived-data.json`) üretir.
- `jlpt-n5-listening-variation-tester`: Üretilen verilerin şema doğruluğunu denetler, görselleri WebP'ye dönüştürür, Gemini TTS ile ses üretir ve final `question.json` dosyasını hazırlar.
- `jlpt-listening-multi-language-expander`: Mevcut `question.json` dosyalarını 6 dilli (TR, EN, DE, FR, ES, KO) "Fat JSON" mimarisine dönüştürür. Tüm transkripsiyonları ve analizleri JLPT N5 seviyesinde çevirir.

---

## Sorumluluk Dağılımı

Soru üretiminin 4 adımı vardır. **Her adımı kimin yaptığı aşağıda net olarak belirtilmiştir:**

| Adım | Yapılacak İş | Kim Yapar |
|---|---|---|
| 1 | YouTube'dan ses indir ve kes | 👤 Sen |
| 2 | İyi klipleri seç, hazırla | 👤 Sen |
| 3 | Soru içeriğini üret | 🤖 Claude |
| 4 | Firebase'e yükle | 👤 Sen |

---

## Adım Adım İş Akışı

---

### 👤 Adım 1 — YouTube'dan Ses İndir ve Kes

`input.json` dosyasını aç, YouTube video URL'ini ve kesmek istediğin zaman aralıklarını saniye cinsinden yaz:

```json
{
  "youtube_url": "https://www.youtube.com/watch?v=XXXXXX",
  "ranges": [
    { "start": 80, "end": 165 },
    { "start": 140, "end": 198 }
  ]
}
```

Sonra pipeline'ı çalıştır:

```bash
cd backend/listening/data/selectImage/listening-youtube-data
./run.sh
```

Pipeline şunları yapar:
1. YouTube videosunu `source_audio/` klasörüne indirir
2. Her zaman aralığını `clips/` altına ayrı bir klip olarak kaydeder
3. Her klip için bir `.done_slice` dosyası oluşturur (bir sonraki çalıştırmada aynı klibi tekrar kesmez)

---

### 👤 Adım 2 — İyi Klipleri Seç ve Hazırla

> **Bu adım tamamen senin sorumluluğundadır. Hiçbir şey otomatik değildir.**

`clips/` klasöründeki ses dosyalarını dinle. JLPT N5 seviyesine uygun, anlaşılır diyalog içeren klipleri seç.

Seçtiğin her klip için:

1. Klip klasörünü `clips/` altından `tobeprocessed/` altına taşı
2. Klip klasörünün içine bir `data.json` dosyası oluştur ve diyalogu Japonca olarak yaz:

```json
{
  "clip": "clip_01_02m00s_02m52s",
  "source": "youtube",
  "level": "N5",
  "topic": "としょかんで ほんを かりる",
  "transcription": {
    "intro": "おんなのひとと おとこのひとが はなしています。おんなのひとは はじめに なにを しますか。",
    "dialogue": [
      { "speaker": "女の人", "text": "すみません。ほんを かりたいんですが。" },
      { "speaker": "男の人", "text": "では、この かみに なまえと でんわばんごうを かいてください。" }
    ],
    "question": "おんなのひとは はじめに なにを しますか。"
  }
}
```

Bu adım bitmeden Adım 3 başlayamaz.

---

### 🤖 Adım 3 — Soru İçeriğini Üret (Claude)

Bu adım Claude tarafından yürütülür. İki aşamadan oluşur:

**3a — Variation Creator** (`jlpt-n5-listening-variation-creator` skill)
- `tobeprocessed/{klip}/data.json`'daki diyalogu ve mantık yapısını analiz eder — ses dosyası hiçbir zaman okunmaz
- Görsel için prompt üretir, kelime ve gramer notlarını çıkarır
- Sonucu `derived-data.json` olarak kaydeder

**3b — Variation Tester** (`jlpt-n5-listening-variation-tester` skill)

6 passtan oluşur:
- **Pass 1** — Mekanik şema doğrulaması (script)
- **Pass 2** — Semantik/dilbilimsel inceleme (Claude)
- **Pass 3** — Görsel doğrulama: `image.png` okunur, panel içerikleri ve stil kontrol edilir
- **Pass 3.5** — Görsel optimizasyon: `image.png` → `image.webp` (max 700×700 px, WebP quality 85); `image.png` silinir
- **Pass 4** — TTS ile `variation-audio.wav` ses dosyası üretilir (Gemini TTS)
- **Pass 5** — Firebase'e hazır `question.json` oluşturulur
- **Pass 6** — Klip klasörü `processed/` altına taşınır

> **Not:** Görsel (image.png) Variation Creator skill'i tarafından üretilir; kullanıcı onayından sonra Tester devreye girer.

Bu adımın sonunda `processed/` klasöründe ses, görsel ve soru verisi hazır olur. Yalnızca `question.json` içindeki `audio_url` ve `image_url` alanları henüz boştur — bu alanlar Adım 4'te doldurulur.

---

### 👤 Adım 4 — Firebase'e Yükle

```bash
backend/listening/scripts/venv/bin/python3.13 backend/listening/scripts/upload_youtube_variations.py \
  --bucket jlpt-bites.firebasestorage.app
```

Script şunları yapar:
1. `processed/` altındaki her klip için `question.json`'a bakar
2. `audio_url` alanı zaten doluysa o klibi atlar — yanlışlıkla iki kez çalıştırsan sorun olmaz
3. `variation-audio.wav` sesini MP3'e dönüştürür (ffmpeg kullanır; eski `variation.wav` adı da desteklenir)
4. MP3'ü ve `image.webp`'yi Firebase Storage'a yükler (yoksa `image.png`'ye düşer — eski klipler için)
5. `question.json`'daki `audio_url` ve `image_url` alanlarını Firebase'deki dosyanın adresiyle doldurur
6. Tüm soru verisini Firestore'a kaydeder

---

## Firebase Yapısı

### Firestore

| Koleksiyon | Döküman ID | İçerik |
|---|---|---|
| `n5_listening_select_image_questions` | `001`, `002`, `003`... | Soru verisi (question.json içeriği) |

Döküman ID'leri otomatik atanır: Firestore'daki mevcut en büyük ID'ye 1 eklenir. Üç haneli sıfır dolgulu format kullanılır (`001`, `002`...).

### Cloud Storage

```
n5_listening/selectImage/
├── 001/
│   ├── audio.mp3     ← Sorunun ses dosyası
│   └── image.webp    ← Sorunun görseli (WebP, max 700px)
├── 002/
│   ├── audio.mp3
│   └── image.webp
└── ...
```

---

## question.json Yapısı

Bu dosya hem diske (`processed/{klip}/question.json`) kaydedilir hem de Firestore'a yüklenir.

```json
{
  "metadata": {
    "level": "N5",
    "topic": "としょかんで ほんを かりる (Borrowing a book at the library)"
  },
  "audio_url": "https://storage.googleapis.com/.../audio.mp3",
  "image_url": "https://storage.googleapis.com/.../image.webp",
  "correct_option": 2,
  "transcription": {
    "intro": "Diyalog öncesi sunulan açıklama cümlesi",
    "dialogue": [
      { "speaker": "女の人", "text": "..." },
      { "speaker": "男の人", "text": "..." }
    ],
    "question": "Kullanıcıya sorulan soru"
  },
  "analysis": {
    "vocabulary": [
      { "word": "としょかん", "reading": "としょかん", "tr": "kütüphane", "en": "library" }
    ],
    "grammar": [
      { "point": "～てください", "tr": "lütfen ... yapın", "en": "please do ..." }
    ]
  },
  "logic": {
    "tr": "Doğru cevabın neden doğru olduğunun açıklaması (Türkçe)",
    "en": "Explanation of why the correct answer is correct (English)"
  }
}
```

`audio_url` ve `image_url`: Adım 3 sonunda bu alanlar boş (`null`) gelir. Adım 4'te upload scripti çalıştırıldığında Firebase'deki gerçek dosya adresleriyle doldurulur. Uygulama bu adresleri kullanarak sesi çalar ve görseli gösterir.

---

## Klip İsimlendirme Kuralı

```
clip_{youtube_video_id}_{sıra_no}_{başlangıç_dakika}m{başlangıç_saniye}s_{bitiş_dakika}m{bitiş_saniye}s
```

- `youtube_video_id`: YouTube URL'sindeki `?v=` parametresi (örneğin `0e0duD8_LFE`)
- `sıra_no`: Aynı videodan alınan kliplerin sıralama numarası (01, 02, ...)

| Klip adı | Anlamı |
|---|---|
| `clip_0e0duD8_LFE_01_02m00s_02m52s` | Video `0e0duD8_LFE`, 1. klip, 2:00–2:52 arası |
| `clip_0e0duD8_LFE_02_07m17s_08m08s` | Video `0e0duD8_LFE`, 2. klip, 7:17–8:08 arası |

---

## İlgili Scriptler

| Script | Konum | Ne yapar |
|---|---|---|
| `pipeline.py` | `listening-youtube-data/` | YouTube'dan ses indirir ve kliplere böler |
| `upload_youtube_variations.py` | `backend/listening/scripts/` | `processed/` klasöründeki klipleri Firebase'e yükler |
| `upload_select_image_questions.py` | `backend/listening/scripts/` | Eski manuel format sorularını Firebase'e yükler |

---

## Gereksinimler

| Araç | Açıklama | Kurulum |
|---|---|---|
| Python 3.13 | Pipeline için (venv hazır, kurmanıza gerek yok) | `listening-youtube-data/venv/` içinde mevcut |
| Python 3.13 | Upload scriptleri için (venv hazır) | `backend/listening/scripts/venv/` içinde mevcut |
| ffmpeg | Ses dönüştürme (WAV → MP3) | `brew install ffmpeg` |
| firebase-tools | Firebase CLI | `npm install -g firebase-tools` |
| service-account-key.json | Firebase kimlik doğrulama | `backend/service-account-key.json` — git'e eklenmez |

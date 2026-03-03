## 2026-03-03

### clip_03_04m11s_05m03s varyasyonu oluşturuldu

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/listening/data/selectImage/listening-youtube-data/processed/clip_03_04m11s_05m03s/derived-data.json` | YENİ | Eşya alışverişi varyasyonu (Attribute pattern) |
| `backend/listening/data/selectImage/listening-youtube-data/processed/clip_03_04m11s_05m03s/image.webp` | YENİ | Şemsiye / çanta / matara 4 panelli görsel (700×700, 17 KB) |
| `backend/listening/data/selectImage/listening-youtube-data/processed/clip_03_04m11s_05m03s/variation-audio.wav` | YENİ | Gemini TTS ses dosyası (34.1s) |
| `backend/listening/data/selectImage/listening-youtube-data/processed/clip_03_04m11s_05m03s/question.json` | YENİ | Firebase-ready soru JSON'u (upload bekliyor) |

**Yapılanlar:**
- Kaynak klip: `clip_03_04m11s_05m03s` (öğle yemeği alışverişi)
- Varyasyon: yemek öğeleri → eşya öğeleri (かさ + すいとう×2); orijinal gramer yapısı korundu
- Görsel: üst küme paneli sorunu nedeniyle eşya seçimleri yapıldı — her panel benzersiz kombinasyon: (1) çanta+2matara, (2) şemsiye+2matara ✓, (3) şemsiye+çanta, (4) 2şemsiye+1matara
- Tüm 6 pass tamamlandı

**Bağlam:** "Doğru panel = tüm öğelerin üst kümesi" olduğunda görsel model panelleri özdeş çiziyor. Çözüm: hiçbir panel diğerinin alt kümesi olmayacak şekilde panel kombinasyonları tasarlanmalı.

---

### README.md güncellendi — WebP ve yeni dosya adları

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/listening/data/selectImage/README.md` | DEĞİŞTİRİLDİ | `variation.wav` → `variation-audio.wav`, `image.png` → `image.webp`, Pass 3.5 açıklaması eklendi, upload komutu venv yoluyla güncellendi |

**Yapılanlar:**
- Klasör yapısı bölümünde `variation.wav` → `variation-audio.wav`, `image.png` → `image.webp` olarak güncellendi
- Adım 3b'ye Pass 3.5 (WebP optimizasyonu) dahil 6 pass listesi eklendi
- Adım 4 upload komutuna `venv/bin/python3.13` yolu eklendi; `variation-audio.wav` ve `image.webp` referansları güncellendi
- Firebase Storage yapısında `image.png` → `image.webp`
- question.json örneğinde `image_url` `.webp` uzantısına güncellendi
- Requirements tablosunda Python 3.9+ → Python 3.13 (venv) olarak güncellendi

---

## 2026-03-03

### WebP görsel optimizasyonu pipeline'a eklendi

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `.claude/skills/jlpt-n5-listening-variation-tester/SKILL.md` | DEĞİŞTİRİLDİ | Pass 3.5 eklendi: image.png → image.webp (max 700px, quality 85) |
| `backend/listening/scripts/upload_youtube_variations.py` | DEĞİŞTİRİLDİ | `image.webp` öncelikli upload; PNG fallback legacy clip'ler için korundu |

**Yapılanlar:**
- Tester skill'e yeni Pass 3.5 eklendi: image validation onayından hemen sonra, audio üretiminden önce çalışır
- `image.png` → `image.webp` dönüşümü: 1024×1024 → max 700×700, WebP quality 85
- Gerçek etki: 1057 KB PNG → 36 KB WebP (%97 küçülme)
- Upload script güncellendi: `.webp` varsa doğrudan upload eder (Pillow compress adımı yok), yoksa eski `.png` akışına düşer

---



### 3 clip Firebase'e yüklendi

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/listening/scripts/upload_youtube_variations.py` | DEĞİŞTİRİLDİ | `variation-audio.wav` fallback desteği eklendi (eski `variation.wav`'a ek olarak) |
| `processed/clip_02_03m05s_04m00s/question.json` | DEĞİŞTİRİLDİ | audio_url + image_url Firebase URL'leriyle güncellendi (ID: 003) |
| `processed/clip_02_03m32s_04m23s/question.json` | DEĞİŞTİRİLDİ | audio_url + image_url Firebase URL'leriyle güncellendi (ID: 004) |
| `processed/clip_YBAJDQ_zDJg_02m21s_03m13s/question.json` | DEĞİŞTİRİLDİ | audio_url + image_url Firebase URL'leriyle güncellendi (ID: 005) |

**Yapılanlar:**
- `n5_listening_select_image_questions` collection'ına 003, 004, 005 ID'leriyle 3 yeni doküman eklendi
- Her clip için WAV → MP3 dönüşümü + Storage upload (audio + image) + Firestore kayıt yapıldı
- `clip_01_02m00s_02m52s` ve `clip_01_02m22s_03m18s` zaten yüklü olduğu için skip edildi (idempotent)
- Upload script'i `variation-audio.wav` dosya adını da (yeni tester output adı) kabul edecek şekilde güncellendi

---



### clip_02_03m32s_04m23s varyasyonu oluşturuldu + klasör düzenlemesi

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/listening/data/selectImage/listening-youtube-data/processed/clip_02_03m32s_04m23s/derived-data.json` | YENİ | Piknik hazırlığı varyasyonu (Attribute pattern) |
| `backend/listening/data/selectImage/listening-youtube-data/processed/clip_02_03m32s_04m23s/image.png` | YENİ | Takeaway kahve bardağı + su şişesi 4-panel görseli |
| `backend/listening/data/selectImage/listening-youtube-data/processed/clip_02_03m32s_04m23s/variation-audio.wav` | YENİ | Gemini TTS ses dosyası (32.2s) |
| `backend/listening/data/selectImage/listening-youtube-data/processed/clip_02_03m32s_04m23s/question.json` | YENİ | Firebase-ready soru JSON'u (upload bekliyor) |
| `.claude/skills/jlpt-n5-listening-variation-creator/references/imagen3-prompting-guide.md` | DEĞİŞTİRİLDİ | "Visual Identification of Items" bölümü eklendi: ikon ve kısa text label kullanım kuralları |

**Yapılanlar:**
- `clip_02_03m32s_04m23s` için tam varyasyon oluşturuldu: はなみ→ピクニック, おかし→サンドイッチ, じゅうす→コーヒー, おちゃ→みず
- Görsel prompt 3 kez iyileştirildi: konserve kutu görünümünden al-götür kahve bardağı formuna geçildi; kahve fincanı ikonu ve "WATER" etiketi eklenerek evrensel tanınabilirlik sağlandı
- `imagen3-prompting-guide.md` güncellendi: monokrom çizimlerde ürünlerin ikon ve kısa text label ile tanınabilir hale getirilmesi kuralı skill'e kalıcı olarak eklendi
- Tüm 6 pass tamamlandı (mechanical → semantic → image → audio → question.json → move)
- `tobeprocessed/` içinde hatalı kalan 4 clip `processed/` altına taşındı: `clip_01_02m00s_02m52s`, `clip_01_02m22s_03m18s` (Firebase'e yüklenmiş), `clip_02_03m05s_04m00s`, `clip_YBAJDQ_zDJg_02m21s_03m13s` (upload bekliyor)

**Bağlam:** Görsel prompt rehberine eklenen ikon/label kuralı bundan sonraki tüm varyasyonlarda kullanılacak.

## 2026-03-19

### selectAudio 021–039 toplu derived-data.json üretimi ve pipeline tamamlama

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/listening/data/selectAudio/021/derived-data.json` | DEĞİŞTİRİLDİ | どうしましたか — doğru seçenek ve distractor güncellendi |
| `backend/listening/data/selectAudio/021/tts_script.json` | YENİ | Female_1 sesi, güncellenmiş seçenekler |
| `backend/listening/data/selectAudio/021/audio.mp3` | YENİ | Gemini TTS 22.8s |
| `backend/listening/data/selectAudio/021/question.json` | YENİ | Final Fat JSON |
| `backend/listening/data/selectAudio/017/audio.mp3` | YENİ | Gemini TTS 22.0s |
| `backend/listening/data/selectAudio/017/question.json` | YENİ | Final Fat JSON |
| `backend/listening/data/selectAudio/022/derived-data.json` | YENİ | ただいま — eve dönen çocuk |
| `backend/listening/data/selectAudio/022/tts_script.json` | YENİ | Male_1 sesi |
| `backend/listening/data/selectAudio/022/audio.mp3` | YENİ | Gemini TTS 23.2s |
| `backend/listening/data/selectAudio/022/question.json` | YENİ | Final Fat JSON |
| `backend/listening/data/selectAudio/023/derived-data.json` | YENİ | おやすみなさい — telefonda yatmadan önce |
| `backend/listening/data/selectAudio/024/derived-data.json` | YENİ | ごちそうさまでした — öğretmen yemeği ödedi |
| `backend/listening/data/selectAudio/025/derived-data.json` | YENİ | この靴をください — ayakkabı satın alma |
| `backend/listening/data/selectAudio/026/derived-data.json` | YENİ | これ、どうぞ — hediye verme |
| `backend/listening/data/selectAudio/027/derived-data.json` | YENİ | お大事に — hasta arkadaşın yanında |
| `backend/listening/data/selectAudio/028/derived-data.json` | YENİ | はじめまして — ilk tanışma |
| `backend/listening/data/selectAudio/029/derived-data.json` | YENİ | おめでとうございます — arkadaşın düğünü |
| `backend/listening/data/selectAudio/030/derived-data.json` | YENİ | いま、なんじ？ — saat sorma |
| `backend/listening/data/selectAudio/031/derived-data.json` | YENİ | きょうとまでいちまいください — bilet satın alma |
| `backend/listening/data/selectAudio/032/derived-data.json` | YENİ | スプーンはありませんか — kaşık isteme |
| `backend/listening/data/selectAudio/033/derived-data.json` | YENİ | どのぐらいかかりますか — trende süre sorma |
| `backend/listening/data/selectAudio/034/derived-data.json` | YENİ | ちかくのえきまでおねがいします — taksiye binerken hedef bildirme |
| `backend/listening/data/selectAudio/035/derived-data.json` | YENİ | こんばんは — gece komşuyla selamlaşma |
| `backend/listening/data/selectAudio/036/derived-data.json` | YENİ | ひとつもちましょうか — arkadaşın yükünü taşıma teklifi |
| `backend/listening/data/selectAudio/037/derived-data.json` | YENİ | やまだです。よろしくおねがいします — ilk tanışmada özkenditanıtma |
| `backend/listening/data/selectAudio/038/derived-data.json` | YENİ | ここ、いいですか — yemekhanede oturabilir miyim |
| `backend/listening/data/selectAudio/039/derived-data.json` | YENİ | そこのしおをとってください — masadan tuz isteme |

**Yapılanlar:**
- 7 sample_clip'teki tüm transcript.json dosyaları okundu (35 soru, 27 tekil doğru yanıt cümlesi)
- Mevcut 002–022 sorularıyla karşılaştırıldı: 17 eksik ifade belirlendi
- 023–039 arası 17 yeni derived-data.json yazıldı — transcript'teki birebir senaryolar kullanıldı
- 021, 017, 022 için pipeline tamamlandı: tts_script.json + audio.mp3 + question.json
- Her dosyada: 7 dil (ja/tr/en/de/fr/es/ko), 3 seçenek, vocabulary + grammar analizi, 6 dil logic açıklaması, image_prompt
- Trap tipleri: Rol Karışıklığı, Yön Karışıklığı, Register Karışıklığı, Bağlam Karışıklığı

**Bağlam:** Kullanıcı 023–039 için kendi imajlarını üretecek (sample_clip klonları). Sonraki adım: tts_script.json → audio.mp3 → question.json pipeline'ı 023–039 için koşturmak.

## 2026-03-18

### selectAudio Creator + Tester Skills eklendi

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `.agents/skills/jlpt-n5-listening-select-audio-creator/SKILL.md` | YENİ | Mondai 3 発話表現 soru üretici skill — imaj analizi, 3 seçenek (1 doğru + 2 distractor), Fat JSON derived-data.json |
| `.agents/skills/jlpt-n5-listening-select-audio-tester/SKILL.md` | YENİ | 6-pass tester: mekanik doğrulama, semantik review, TTS script, Imagen 3 imaj, Gemini TTS ses, question.json build |
| `.agents/skills/jlpt-n5-listening-select-audio-tester/scripts/validate_derived_data.py` | YENİ | Pass 1 Python validator — 10 check, exit 0/1 |

**Yapılanlar:**
- `jlpt-n5-listening-select-audio-creator` skill yazıldı: sample_clips'ten imaj seçme, sahne analizi, 4 trap tipi (Rol/Yön/Register/Bağlam), image_prompt üretimi, 7-dil Fat JSON derived-data.json, kullanıcı onayı bekleme
- `jlpt-n5-listening-select-audio-tester` skill yazıldı: Pass 1 (script), Pass 2 (Claude semantic), Pass 3 (TTS script — 3 seçenek aynı ses), Pass 4 (Imagen 3), Pass 5 (Gemini TTS), Pass 6 (question.json build)
- `validate_derived_data.py` yazıldı ve 10/10 smoke test geçti
- selectText'ten temel fark: 4 seçenek → 3 seçenek, dialogue yok → options array, image_url field eklendi, correct_option 0-2

**Bağlam:** Plan doğrultusunda selectAudio modülü için creator+tester skill çifti oluşturuldu.

## 2026-03-17

### selectText — Firebase Upload ve 001 Varyasyonu

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/listening/scripts/upload_select_text_questions.py` | DEĞİŞTİRİLDİ | Fat JSON uyumlu hale getirildi: question.json desteği, top-level audio_url, doğru collection adı, idempotency, clip_* filtresi |
| `backend/listening/data/selectText/001/question.json` | DEĞİŞTİRİLDİ | Kış tatili/onsen varyasyonu, intro typo düzeltmesi, speaker label'lar hiragana'ya çevrildi |
| `backend/listening/data/selectText/001/tts_script.json` | DEĞİŞTİRİLDİ | Yeni diyaloğa göre güncellendi |
| `backend/listening/data/selectText/001/audio.mp3` | DEĞİŞTİRİLDİ | Gemini TTS ile yeniden üretildi (35.6s, 304 KB) |
| `backend/listening/data/selectText/002-031/question.json` | DEĞİŞTİRİLDİ | audio_url Firebase URL ile güncellendi |
| `backend/listening/data/selectText/CLAUDE.md` | DEĞİŞTİRİLDİ | TODO: upload ve Firebase entegrasyonu tamamlandı |

**Yapılanlar:**
- Upload script 6 kritik hata düzeltildi (yanlış dosya adı, yanlış audio_url path, yanlış collection, clip filtresi yok, idempotency yok, bucket default yok)
- 001 sorusu varyasyonlandı: yaz→kış tatili, Fuji tırmanışı→Hakone onsen, koşu→yürüyüş
- 31 soru Firebase'e yüklendi: Storage `listening/selectText/{id}/audio.mp3`, Firestore `n5_listening_select_text_questions`

---

### selectText (Point Comprehension) Modülü — Skill Oluşturma ve 30 Soru Üretimi

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `.agents/skills/jlpt-n5-listening-point-comprehension-creator/SKILL.md` | YENİ | Point Comprehension soru üretici skill |
| `.agents/skills/jlpt-n5-listening-point-comprehension-creator/references/n5-grammar-points.md` | YENİ | N5 gramer referansı |
| `.agents/skills/jlpt-n5-listening-point-comprehension-creator/references/n5-point-comprehension-patterns.md` | YENİ | 8 tuzak kalıbı detaylı referans |
| `backend/listening/data/selectText/CLAUDE.md` | DEĞİŞTİRİLDİ | Skill bilgisi ve yapılacaklar güncellendi |
| `backend/listening/data/selectText/002-031/question_data.json` | YENİ | 30 adet Point Comprehension sorusu |
| `backend/listening/data/selectText/generate_batch.py` | YENİ | Toplu soru üretim scripti |

**Yapılanlar:**
- 5 kaynak clip (30 gerçek JLPT sorusu) analiz edildi, 8 tuzak kalıbı çıkarıldı
- `jlpt-n5-listening-point-comprehension-creator` skill oluşturuldu
- Kaynak sorulardan varyasyon yöntemiyle 30 yeni soru (002-031) üretildi
- Kalıp dağılımı: Fikir Değiştirme (10), Dikkat Dağıtıcı (5), Hesaplama (5), Zaman Çıkarımı (4), Olumsuz Eleme (3), Düzeltme (1), Sipariş (1), Neden (1)
- correct_option dağılımı: {0: 9, 1: 8, 2: 11, 3: 3}

**Bağlam:** selectText (Mondai 2) modülü sıfırdan oluşturuldu. Audio üretimi ve Firebase upload sonraki adım.

---

## 2026-03-04

### Listening Modülü Çok Dilli Yapı Göçü ve Yeni Varyasyonlar

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/listening/data/selectImage/listening-youtube-data/processed/*/question.json` | DEĞİŞTİRİLDİ | 30 adet soru 6 dilli (TR, EN, DE, FR, ES, KO) "Fat JSON" yapısına dönüştürüldü. |
| `.agents/skills/jlpt-listening-multi-language-expander/` | YENİ | Çok dilli dönüşümü otomatize eden yeni Agent Skill oluşturuldu. |
| `backend/listening/data/selectImage/README.md` | DEĞİŞTİRİLDİ | Kullanılabilir Agent yetenekleri (Skills) bölümü eklendi ve dokümante edildi. |
| `CLAUDE.md` | DEĞİŞTİRİLDİ | Yeni Agent yeteneklerinin modül README'lerine eklenmesi zorunluluğu kural olarak eklendi. |
| `backend/n5_vocabulary/data/n5_vocabulary.json` | DEĞİŞTİRİLDİ | 026-075 arası kelimelere Korece çeviriler eklendi. |
| `processed/clip_7HfHdb5J3f4_01_06m15s_07m30s/` | YENİ | "Mendil Seçimi" varyasyonu (Küçük kediler vs Büyük köpekler) tamamlandı. |
| `processed/clip_7HfHdb5J3f4_02_08m45s_09m25s/` | YENİ | "Ofiste Bekleme" varyasyonu (Kitaplık yanındaki koltuk) tamamlandı. |
| `tobeprocessed/clip_7HfHdb5J3f4_03_09m40s_10m50s/` | DEĞİŞTİRİLDİ | "Kütüphanede Ders Çalışma" varyasyonu hazırlandı (Görsel ve JSON hazır, Ses API limiti nedeniyle bekliyor). |

**Yapılanlar:**
- Dinleme modülündeki tüm `question.json` dosyaları tek bir dosyada 6 dili (TR, EN, DE, FR, ES, KO) destekleyecek "Fat JSON" mimarisine taşındı.
- `jlpt-listening-multi-language-expander` yeteneği geliştirildi; Japonca ana referans alınarak N5 seviyesinde profesyonel çeviriler ve JSON validasyonu yapıldı.
- `clip_7HfHdb5J3f4` YouTube klibinden 3 yeni varyasyon üretildi. Görsel üretiminde Imagen 3 kullanıldı ve WebP optimizasyonu (max 700px) uygulandı.
- `selectImage` README'si yeni yetenekleri ve sorumluluk dağılımını içerecek şekilde güncellendi.
- N5 kelime listesinde Korece çeviri süreci başlatıldı (İlk 75 kelime tamamlandı).

**Bağlam:**
Uygulamanın uluslararasılaşma (i18n) stratejisi doğrultusunda içerik altyapısı tekilleştirildi ve 6 dil desteği tüm dinleme sorularına uygulandı.

---

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

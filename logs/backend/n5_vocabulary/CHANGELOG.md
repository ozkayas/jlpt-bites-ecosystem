# N5 Vocabulary — Changelog

## 2026-03-14

### active_recall_pool → Firebase upload pipeline oluşturuldu

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/n5_vocabulary/scripts/upload_active_recall_pool.py` | YENİ | 152 checkpoint'i `n5_active_recall_pool` Firestore collection'ına yükler. Idempotent (set), batch write, `--dry-run`, `--checkpoint`, `--clear` flag'leri. |
| `backend/n5_vocabulary/scripts/add_language_to_pool.py` | YENİ | Mevcut collection'a yeni bir UI dili ekler. Firestore `update()` kullanır — diğer alanları korur. `--lang`, `--file`, `--checkpoint`, `--dry-run` flag'leri. |

**Yapılanlar:**
- `n5_active_recall_pool/{cp_id}` yapısında checkpoint başına bir Firestore dokümanı (ort. ~7 KB, limit altında)
- Dry-run doğrulandı: 152 checkpoint, 760 cümle, cp_15 → cp_770
- `upload_n5_vocabulary.py` pattern'ı aynen takip edildi (batch 400 op limit)
- `add_language_to_pool.py` — gelecekte dil ekleme ihtiyacı için hazır; mevcut sentences array'ini okuyup merge eder

**Bağlam:** `active_recall_pool.json` 1.1 MB (Firestore 1 MB limit aşıyor). Checkpoint başına doküman mimarisi seçildi: granüler güncelleme, OTA içerik değiştirme ve mevcut backend pipeline uyumu sağlar.

## 2026-03-09

### Audio ID migrasyonu — v01.json pedagojik sıralama sonrası ses yolları düzeltildi

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/n5_vocabulary/scripts/migrate_audio_ids.py` | YENİ | Storage'daki ses dosyalarını eski ID → yeni ID path'lerine kopyalayan migrasyon scripti |
| `backend/n5_vocabulary/data/n5_vocabulary_v01.json` | DEĞİŞTİRİLDİ | Tüm `audioUrl` ve `sentences[].audioUrl` alanları yeni ID path'leriyle güncellendi |

**Yapılanlar:**
- v01.json pedagojik sıralama sırasında ID'ler yeniden atanmış, Storage ses dosyaları eski ID'lerde kalmıştı
- `migrate_audio_ids.py` scripti: eski→yeni ID mapping çıkararak 1539 Storage dosyasını kopyaladı
- v01.json'daki tüm audioUrl'ler yeni path'lerle güncellendi
- Firestore ve vocabulary_meta yeniden yüklendi
- `～かい` kelimesinin cümle sesi değiştiğinden null bırakıldı (yeniden üretilmesi gerekiyor)

**Bağlam:** Pedagojik sıralama sırasında ID'ler değiştirilmişti ancak Storage ses dosyaları eski ID'lerde kalmıştı; her kelime yanlış sesi çalıyordu.

---

## 2026-03-08

### n5_vocabulary_v01.json Firebase'e yüklendi

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/n5_vocabulary/data/n5_vocabulary_v01.json` | YENİ | 770 kelimeli yeni vocabulary verisi; `ko` (Korece) translations ve `furigana` alanları eklendi |
| `backend/n5_vocabulary/scripts/upload_n5_vocabulary.py` | DEĞİŞTİRİLDİ | `--file`, `--clear` parametreleri eklendi; `clear_collection()` fonksiyonu eklendi |

**Yapılanlar:**
- Firestore `n5_vocabulary` collection'ındaki 844 eski döküman silindi
- `n5_vocabulary_v01.json`'dan 770 kelime Firestore'a yüklendi
- Upload scripti `--file` (kaynak dosya seçimi) ve `--clear` (önce sil) parametreleriyle güncellendi
- Yeni şema: translations artık `ko` (Korece) içeriyor; sentences'da `furigana` alanı mevcut

**Bağlam:** Vocabulary verisi yeni 6-dil şemasına (TR, EN, DE, ES, FR, KO) ve furigana desteğine güncellendi.

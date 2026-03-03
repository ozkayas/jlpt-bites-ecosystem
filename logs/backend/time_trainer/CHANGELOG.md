# Time Trainer — Değişiklik Günlüğü

---

## 2026-03-03

### Upload pipeline kuruldu + 84 ses Firebase'e yüklendi

**Değiştirilen / Eklenen Dosyalar:**

| Dosya | Aksiyon | Açıklama |
|-------|---------|----------|
| `backend/time_trainer/scripts/upload_audio.py` | YENİ | `output_verified/*.mp3` dosyalarını Firebase Storage'a yükleyen script |
| `backend/time_trainer/TIME_TRAINER_APP_INTEGRATION.md` | YENİ | Flutter uygulaması için entegrasyon paketi (prompt + URL listesi) |

**Yapılanlar:**

- `upload_audio.py` oluşturuldu: `output_verified/` içindeki MP3'leri `time_trainer/audio/HHMM.mp3` path'ine yükler
  - `--dry-run`: upload yapmadan listeyi gösterir
  - `--force`: mevcut blob'ların üzerine yazar
  - Idempotent: blob zaten varsa skip eder
  - Firebase init pattern: `backend/listening/scripts/upload_youtube_variations.py`'den alındı
- 84 adet doğrulanmış MP3 Firebase Storage'a yüklendi (bucket: `jlpt-bites.firebasestorage.app`)
- Storage path: `time_trainer/audio/{HHMM}.mp3` — tümü public
- `TIME_TRAINER_APP_INTEGRATION.md` oluşturuldu: uygulama ajanına verilecek prompt + `availableTimes` Dart listesi + tam URL tablosu

**Bağlam:**

Önceki oturumda (2026-03-02) Gemini TTS ile 84 saat için MP3 üretilmiş, leading silence trim edilmiş ve `output_verified/` klasörüne taşınmıştı. Bu oturumda upload adımı tamamlandı.

**Çalıştırma Komutu:**

```bash
PYTHONPATH=backend/listening/scripts/venv/lib/python3.13/site-packages \
python3.13 backend/time_trainer/scripts/upload_audio.py \
  --bucket jlpt-bites.firebasestorage.app
```

# Time Trainer Audio

Firebase Storage'daki 1440 saat sesi (0:00–23:59) için üretim pipeline'ı.

## Storage Path

```
time_trainer/audio/HHMM.mp3
```

Örnekler:
- `time_trainer/audio/0000.mp3` → 0時 (れいじ)
- `time_trainer/audio/0130.mp3` → 1時30分 (いちじさんじゅっぷん)
- `time_trainer/audio/2359.mp3` → 23時59分 (にじゅうさんじごじゅうきゅうふん)

## Ses Üretimi

Skill: `skills/time-trainer-audio-generator/`

Gemini TTS (Kore voice) ile 15'er batch üretim + Gemini Flash doğrulama döngüsü.

### Hızlı Başlangıç

```bash
# Venv kur (ilk seferinde)
cd skills/time-trainer-audio-generator
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Tek batch test
skills/time-trainer-audio-generator/venv/bin/python3 \
  skills/time-trainer-audio-generator/scripts/generate_and_verify.py \
  --batch 0100-0114

# Tam çalıştırma
skills/time-trainer-audio-generator/venv/bin/python3 \
  skills/time-trainer-audio-generator/scripts/generate_and_verify.py \
  --bucket jlpt-bites.firebasestorage.app
```

### Dry Run (API çağrısı yok)

```bash
skills/time-trainer-audio-generator/venv/bin/python3 \
  skills/time-trainer-audio-generator/scripts/generate_and_verify.py \
  --dry-run --batch 0100-0114
```

## Dosya Yapısı

```
backend/time_trainer/
  scripts/
    generate_time_audio.py     # Eski script (hours+minutes separate approach)
    generate_and_verify.py     # Yeni script (→ skills/ içinde)
  state/
    progress.json              # Batch ilerleme durumu
  output/
    0000.mp3                   # Üretilen MP3 dosyaları
    0001.mp3
    ...
    2359.mp3
  test_audio/
    batch_1_00_to_1_14.wav     # Test ses dosyaları
```

## Batch Yapısı

1440 kombinasyon → 96 batch (15'er):

| Batch ID    | İçerik                        |
|-------------|-------------------------------|
| `0000-0014` | 0時, 0時1分, ..., 0時14分     |
| `0015-0029` | 0時15分, ..., 0時29分         |
| `0030-0044` | 0時30分, ..., 0時44分         |
| `0045-0059` | 0時45分, ..., 0時59分         |
| `0100-0114` | 1時, 1時1分, ..., 1時14分     |
| ...         | ...                           |
| `2345-2359` | 23時45分, ..., 23時59分       |

## İlerleme Takibi

```bash
cat backend/time_trainer/state/progress.json
```

Çıktı:
```json
{
  "last_verified_batch": "0100-0114",
  "completed_batches": ["0000-0014", "0015-0029", "0100-0114"],
  "failed_batches": {},
  "total_batches": 96,
  "last_updated": "2026-03-02T15:00:00"
}
```

Kesintiden devam:
```bash
python generate_and_verify.py --bucket jlpt-bites.firebasestorage.app --resume
```

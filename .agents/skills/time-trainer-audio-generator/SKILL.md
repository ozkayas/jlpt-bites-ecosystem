---
name: time-trainer-audio-generator
description: "Generate 1440 Japanese time-reading MP3 files (0:00–23:59) for the JLPT Time Trainer feature. Uses Gemini TTS in batches of 15 with Gemini Flash verification per segment. Stateful: resumes from progress.json if interrupted. Use when user asks to 'time trainer ses üret', 'generate time audio', 'saat seslerini oluştur', or '1440 mp3'."
---

# Time Trainer Audio Generator

Generate all 1440 Japanese time-reading MP3 files (0:00–23:59) using Gemini TTS with automatic verification.

## Overview

- **1440 combinations** = 24 hours × 60 minutes
- **96 batches** of 15 items each (4 batches per hour)
- **Each batch**: TTS → split → MP3 → Gemini Flash verify → save → upload
- **Stateful**: progress saved to `backend/time_trainer/state/progress.json`
- **Output**: `backend/time_trainer/output/HHMM.mp3` + Firebase Storage `time_trainer/audio/HHMM.mp3`

---

## Prerequisites

- `GEMINI_API_KEY` or `GEMINI_API_KEYS` (comma-separated) in environment or `.env`
- `backend/service-account-key.json` (for Firebase upload)
- `ffmpeg` installed (`brew install ffmpeg`)

---

## Venv Setup (one-time)

```bash
cd skills/time-trainer-audio-generator
python3 -m venv venv
venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## Claude Workflow

### Step 1 — Setup

Check prerequisites:
```bash
# Verify ffmpeg
which ffmpeg

# Verify API key
echo $GEMINI_API_KEY

# Create venv if needed
ls skills/time-trainer-audio-generator/venv/bin/python3 || (
  cd skills/time-trainer-audio-generator && python3 -m venv venv && venv/bin/pip install -r requirements.txt
)
```

### Step 2 — Check State

```bash
cat backend/time_trainer/state/progress.json 2>/dev/null || echo "No state yet — fresh start"
```

Report: total completed, total failed, last verified batch.

### Step 3 — Run Script

**Next batch (default: processes the next uncompleted batch):**
```bash
skills/time-trainer-audio-generator/venv/bin/python3 \
  skills/time-trainer-audio-generator/scripts/generate_and_verify.py \
  --bucket jlpt-bites.firebasestorage.app
```

Each invocation processes exactly one batch and prints which batch comes next.

**Specific batch:**
```bash
skills/time-trainer-audio-generator/venv/bin/python3 \
  skills/time-trainer-audio-generator/scripts/generate_and_verify.py \
  --batch 0100-0114
```

**Dry run (no API calls):**
```bash
skills/time-trainer-audio-generator/venv/bin/python3 \
  skills/time-trainer-audio-generator/scripts/generate_and_verify.py \
  --dry-run --batch 0100-0114
```

### Step 4 — Monitor Progress

After each batch the script prints:
```
[Batch 0100-0114] 1時00分 – 1時14分
  TTS generated: 54.3s audio
  Split: 14 silences detected
  ✓ [1/15] 1時: 'いちじ'
  ✓ [2/15] 1時1分: 'いちじいっぷん'
  ...
  Saved 15 MP3 files to output/
  ↑ 0100.mp3
  ↑ 0101.mp3
  ...
```

If the script is interrupted, rerun with `--resume` — it skips completed batches.

### Step 5 — Report Results

After completion, report:
- Total batches completed / failed
- Any failed batches with error details from `progress.json`
- Storage path: `time_trainer/audio/HHMM.mp3`

If there are failed batches, retry them individually:
```bash
skills/time-trainer-audio-generator/venv/bin/python3 \
  skills/time-trainer-audio-generator/scripts/generate_and_verify.py \
  --bucket jlpt-bites.firebasestorage.app --batch HHMM-HHMM
```

---

## Batch ID Format

`HHMM-HHMM` where HH = hour (00–23), MM = start/end minute:

| Batch ID | Contents |
|----------|----------|
| `0000-0014` | 0時, 0時1分, ..., 0時14分 |
| `0015-0029` | 0時15分, ..., 0時29分 |
| `0030-0044` | 0時30分, ..., 0時44分 |
| `0045-0059` | 0時45分, ..., 0時59分 |
| `0100-0114` | 1時, 1時1分, ..., 1時14分 |
| ... | ... |
| `2345-2359` | 23時45分, ..., 23時59分 |

---

## State File Reference

`backend/time_trainer/state/progress.json`:
```json
{
  "last_verified_batch": "0100-0114",
  "completed_batches": ["0000-0014", "0015-0029", "0100-0114"],
  "failed_batches": {
    "0030-0044": {"attempts": 3, "errors": ["0時30分: got 'さんじゅっぷん'"]}
  },
  "total_batches": 96,
  "last_updated": "2026-03-02T15:00:00"
}
```

---

## Resources

| Resource | Purpose |
|----------|---------|
| `scripts/generate_and_verify.py` | Main script: TTS → split → verify → upload |
| `references/kanji-reading-map.md` | Expected hiragana readings for all times |
| `requirements.txt` | Python dependencies |
| `backend/time_trainer/README.md` | Backend documentation |

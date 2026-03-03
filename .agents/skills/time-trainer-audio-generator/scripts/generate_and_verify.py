#!/usr/bin/env python3
"""
Time Trainer Audio Generator — Curated 86-item set.

Generates MP3 files for a curated selection of 86 Japanese time expressions:
  Group A: 24 hours (0時–23時)
  Group B: 12 half-hours (1時30分–12時30分)
  Group C: 50 mixed (covering every minute reading pattern)

State machine per batch:
  pending → tts_done → completed
                    ↘ failed (content mismatch — human review)

Per invocation:
  - Verifies pending (tts_done) batch first if one exists — no TTS regeneration
  - Otherwise generates TTS for the next pending batch
  - On rate limit during verification: saves state, exits cleanly
  - Verification: ONE Gemini Flash call for the full batch audio

Usage:
    python generate_and_verify.py                               # next batch
    python generate_and_verify.py --bucket jlpt-bites.firebasestorage.app
    python generate_and_verify.py --batch 000-009              # specific batch
    python generate_and_verify.py --dry-run [--batch ID]       # no API calls
    python generate_and_verify.py --no-verify                  # skip verification

Environment:
    GEMINI_API_KEY or GEMINI_API_KEYS (comma-separated)
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave
import argparse
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

try:
    import firebase_admin
    from firebase_admin import credentials, storage as fb_storage
    _FIREBASE_AVAILABLE = True
except ImportError:
    _FIREBASE_AVAILABLE = False


# ─── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR  = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent.parent.parent
STATE_DIR   = REPO_ROOT / "backend" / "time_trainer" / "state"
OUTPUT_DIR  = REPO_ROOT / "backend" / "time_trainer" / "output"
PENDING_DIR = REPO_ROOT / "backend" / "time_trainer" / "pending"


# ─── Constants ────────────────────────────────────────────────────────────────

MODEL_TTS    = "gemini-2.5-flash-preview-tts"
MODEL_VERIFY = "gemini-2.5-flash"
VOICE        = "Kore"

SAMPLE_RATE  = 24000
SAMPLE_WIDTH = 2
CHANNELS     = 1

BATCH_SIZE     = 10
REQUESTS_PER_KEY = 3    # free tier: 3 req/min
MAX_RETRIES      = 3

STORAGE_PREFIX = "time_trainer/audio"


# ─── Time Readings ────────────────────────────────────────────────────────────

HOUR_READINGS = [
    'れいじ',           # 0時
    'いちじ',           # 1時
    'にじ',             # 2時
    'さんじ',           # 3時
    'よじ',             # 4時
    'ごじ',             # 5時
    'ろくじ',           # 6時
    'しちじ',           # 7時
    'はちじ',           # 8時
    'くじ',             # 9時
    'じゅうじ',         # 10時
    'じゅういちじ',     # 11時
    'じゅうにじ',       # 12時
    'じゅうさんじ',     # 13時
    'じゅうよじ',       # 14時
    'じゅうごじ',       # 15時
    'じゅうろくじ',     # 16時
    'じゅうしちじ',     # 17時
    'じゅうはちじ',     # 18時
    'じゅうくじ',       # 19時
    'にじゅうじ',       # 20時
    'にじゅういちじ',   # 21時
    'にじゅうにじ',     # 22時
    'にじゅうさんじ',   # 23時
]

MINUTE_READINGS = {
    1:  'いっぷん',
    2:  'にふん',
    3:  'さんぷん',
    4:  'よんぷん',
    5:  'ごふん',
    6:  'ろっぷん',
    7:  'ななふん',
    8:  'はっぷん',
    9:  'きゅうふん',
    10: 'じゅっぷん',
    11: 'じゅういっぷん',
    12: 'じゅうにふん',
    13: 'じゅうさんぷん',
    14: 'じゅうよんぷん',
    15: 'じゅうごふん',
    16: 'じゅうろっぷん',
    17: 'じゅうななふん',
    18: 'じゅうはっぷん',
    19: 'じゅうきゅうふん',
    20: 'にじゅっぷん',
    21: 'にじゅういっぷん',
    22: 'にじゅうにふん',
    23: 'にじゅうさんぷん',
    24: 'にじゅうよんぷん',
    25: 'にじゅうごふん',
    26: 'にじゅうろっぷん',
    27: 'にじゅうななふん',
    28: 'にじゅうはっぷん',
    29: 'にじゅうきゅうふん',
    30: 'さんじゅっぷん',
    31: 'さんじゅういっぷん',
    32: 'さんじゅうにふん',
    33: 'さんじゅうさんぷん',
    34: 'さんじゅうよんぷん',
    35: 'さんじゅうごふん',
    36: 'さんじゅうろっぷん',
    37: 'さんじゅうななふん',
    38: 'さんじゅうはっぷん',
    39: 'さんじゅうきゅうふん',
    40: 'よんじゅっぷん',
    41: 'よんじゅういっぷん',
    42: 'よんじゅうにふん',
    43: 'よんじゅうさんぷん',
    44: 'よんじゅうよんぷん',
    45: 'よんじゅうごふん',
    46: 'よんじゅうろっぷん',
    47: 'よんじゅうななふん',
    48: 'よんじゅうはっぷん',
    49: 'よんじゅうきゅうふん',
    50: 'ごじゅっぷん',
    51: 'ごじゅういっぷん',
    52: 'ごじゅうにふん',
    53: 'ごじゅうさんぷん',
    54: 'ごじゅうよんぷん',
    55: 'ごじゅうごふん',
    56: 'ごじゅうろっぷん',
    57: 'ごじゅうななふん',
    58: 'ごじゅうはっぷん',
    59: 'ごじゅうきゅうふん',
}

# 0時: TTS may say れいじ or ぜろじ — both accepted
HOUR_ALTERNATIVES = {
    0: ['れいじ', 'ぜろじ'],
}

MINUTE_ALTERNATIVES = {}


# ─── Curated 86-item List ─────────────────────────────────────────────────────

CURATED_TIMES = [
    # ── Group A: Hours only (24) ──────────────────────────────────────────────
    (0, 0),  (1, 0),  (2, 0),  (3, 0),  (4, 0),  (5, 0),  (6, 0),  (7, 0),
    (8, 0),  (9, 0),  (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0),
    (16, 0), (17, 0), (18, 0), (19, 0), (20, 0), (21, 0), (22, 0), (23, 0),
    # ── Group B: X時30分 (12) ─────────────────────────────────────────────────
    (1, 30),  (2, 30),  (3, 30),  (4, 30),  (5, 30),  (6, 30),
    (7, 30),  (8, 30),  (9, 30),  (10, 30), (11, 30), (12, 30),
    # ── Group C: Mixed 50 ────────────────────────────────────────────────────
    # 1–9分 (9)
    (1, 1),  (3, 2),  (5, 3),  (7, 4),  (9, 5),
    (11, 6), (13, 7), (0, 8),  (2, 9),
    # 5分刻み: 10, 15, 20, 25, 30, 35, 40, 45, 50, 55 (10)
    (4, 10),  (6, 15),  (8, 20),  (10, 25), (14, 30),
    (16, 35), (18, 40), (20, 45), (22, 50), (17, 55),
    # 11–19分 (15除く) (8)
    (15, 11), (19, 12), (21, 13), (23, 14),
    (2, 16),  (4, 17),  (6, 18),  (8, 19),
    # 21–29分 (25除く) (8)
    (10, 21), (12, 22), (14, 23), (16, 24),
    (18, 26), (20, 27), (22, 28), (0, 29),
    # 31–39分 (30・35除く) (5)
    (1, 31), (3, 33), (5, 36), (7, 38), (9, 39),
    # 41–49分 (40・45除く) (5)
    (11, 41), (13, 43), (15, 46), (17, 48), (19, 49),
    # 51–59分 (50・55除く) (5)
    (21, 51), (23, 52), (1, 53), (5, 58), (7, 59),
]

assert len(CURATED_TIMES) == 86, f"Expected 86 items, got {len(CURATED_TIMES)}"

TOTAL_BATCHES = (len(CURATED_TIMES) + BATCH_SIZE - 1) // BATCH_SIZE  # = 9


# ─── State ────────────────────────────────────────────────────────────────────

def load_state():
    state_file = STATE_DIR / "progress.json"
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {
        "completed_batches": [],
        "tts_done":      {},   # {batch_id: {pending_dir, start_idx}}
        "failed_batches":{},   # {batch_id: {reason, errors, pending_dir}}
        "total_batches": TOTAL_BATCHES,
        "last_updated":  None,
    }


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    with open(STATE_DIR / "progress.json", "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ─── Batch Structure ──────────────────────────────────────────────────────────

def all_batches():
    """Returns list of (batch_id, start_idx) for every curated batch."""
    result = []
    for i in range(0, len(CURATED_TIMES), BATCH_SIZE):
        end = min(i + BATCH_SIZE, len(CURATED_TIMES))
        bid = f"{i:03d}-{end-1:03d}"
        result.append((bid, i))
    return result


def build_batch_items(hm_list):
    """Convert list of (hour, minute) to list of (kanji, hiragana)."""
    items = []
    for h, m in hm_list:
        if m == 0:
            kanji    = f"{h}時"
            hiragana = HOUR_READINGS[h]
        else:
            kanji    = f"{h}時{m}分"
            hiragana = HOUR_READINGS[h] + MINUTE_READINGS[m]
        items.append((kanji, hiragana))
    return items


def batch_text(items):
    return " ".join(k for k, _ in items)


def get_accepted_readings(hour, minute):
    if minute == 0:
        return HOUR_ALTERNATIVES.get(hour, [HOUR_READINGS[hour]])
    hour_variants   = HOUR_ALTERNATIVES.get(hour,   [HOUR_READINGS[hour]])
    minute_variants = MINUTE_ALTERNATIVES.get(minute, [MINUTE_READINGS[minute]])
    return [h + m for h in hour_variants for m in minute_variants]


# ─── API Keys & Key Rotator ───────────────────────────────────────────────────

def load_api_keys():
    keys_str = os.environ.get("GEMINI_API_KEYS")
    if keys_str:
        keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if keys:
            return keys
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return [key]
    for env_path in [REPO_ROOT / ".env", SCRIPT_DIR / ".env"]:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEYS="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        return [k.strip() for k in val.split(",") if k.strip()]
                    if line.startswith("GEMINI_API_KEY="):
                        return [line.split("=", 1)[1].strip().strip('"').strip("'")]
    print("GEMINI_API_KEY(S) not found. Set with: export GEMINI_API_KEYS='key1,key2'")
    sys.exit(1)


class KeyRotator:
    def __init__(self, api_keys):
        self.keys         = api_keys
        self.clients      = [genai.Client(api_key=k) for k in api_keys]
        self.usage        = [0] * len(api_keys)
        self.window_start = [0.0] * len(api_keys)
        self.current      = 0

    def get_client(self):
        now = time.time()
        for _ in range(len(self.keys)):
            idx     = self.current
            elapsed = now - self.window_start[idx]
            if elapsed >= 60:
                self.usage[idx]        = 0
                self.window_start[idx] = now
            if self.usage[idx] < REQUESTS_PER_KEY:
                return idx, self.clients[idx]
            self.current = (self.current + 1) % len(self.keys)

        oldest = min(range(len(self.keys)), key=lambda i: self.window_start[i])
        wait   = 60 - (time.time() - self.window_start[oldest]) + 2
        if wait > 0:
            print(f"  All {len(self.keys)} keys exhausted. Waiting {wait:.0f}s...")
            time.sleep(wait)
        self.usage[oldest]        = 0
        self.window_start[oldest] = time.time()
        self.current              = oldest
        return oldest, self.clients[oldest]

    def record_usage(self, idx):
        self.usage[idx] += 1
        self.current = (self.current + 1) % len(self.keys)


# ─── TTS ──────────────────────────────────────────────────────────────────────

def generate_tts(rotator, text):
    prompt = (
        "Speak the following Japanese text slowly and clearly, "
        "as a formal narrator for a JLPT language listening exam. "
        f"Use a slow, measured pace with clear pronunciation:\n{text}"
    )
    for attempt in range(1, MAX_RETRIES + 1):
        idx, client = rotator.get_client()
        try:
            response = client.models.generate_content(
                model=MODEL_TTS,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)
                        )
                    ),
                ),
            )
            rotator.record_usage(idx)
            c = response.candidates[0]
            if c.content is None:
                raise RuntimeError(f"TTS returned no audio (finish_reason={c.finish_reason})")
            return c.content.parts[0].inline_data.data
        except RuntimeError:
            raise
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                rotator.usage[idx] = REQUESTS_PER_KEY
                rotator.current    = (idx + 1) % len(rotator.keys)
                print(f"    Key {idx+1} rate limited (attempt {attempt}/{MAX_RETRIES}), rotating...")
            elif "400" in err and "generate text" in err.lower():
                # TTS model returned text instead of audio — rotate to next key
                rotator.usage[idx] = REQUESTS_PER_KEY
                rotator.current    = (idx + 1) % len(rotator.keys)
                print(f"    Key {idx+1} returned text not audio (attempt {attempt}/{MAX_RETRIES}), rotating...")
            elif "500" in err or "INTERNAL" in err:
                wait = 5 * attempt
                print(f"    Server error (attempt {attempt}/{MAX_RETRIES}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("TTS failed after max retries")


def generate_single_tts(rotator, kanji_text):
    """Fallback: single item TTS."""
    prompt = (
        "Speak the following Japanese text slowly and clearly, "
        "as a formal narrator for a JLPT language listening exam. "
        f"Use a slow, measured pace with clear pronunciation:\n{kanji_text}"
    )
    for attempt in range(1, MAX_RETRIES + 1):
        idx, client = rotator.get_client()
        try:
            response = client.models.generate_content(
                model=MODEL_TTS,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)
                        )
                    ),
                ),
            )
            rotator.record_usage(idx)
            c = response.candidates[0]
            if c.content is None:
                raise RuntimeError(f"TTS returned no audio for '{kanji_text}'")
            return c.content.parts[0].inline_data.data
        except RuntimeError:
            raise
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                rotator.usage[idx] = REQUESTS_PER_KEY
                rotator.current    = (idx + 1) % len(rotator.keys)
                print(f"    Key {idx+1} rate limited (attempt {attempt}/{MAX_RETRIES}), rotating...")
            elif "500" in err or "INTERNAL" in err:
                time.sleep(5 * attempt)
            else:
                raise
    raise RuntimeError(f"TTS failed after max retries: {kanji_text}")


# ─── WAV / ffmpeg ─────────────────────────────────────────────────────────────

def save_wav(pcm_data, path):
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)


def get_audio_duration(path):
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())


class SplitError(Exception):
    pass


def detect_silences(wav_path, noise_db=-35, min_duration=0.4):
    result = subprocess.run(
        ['ffmpeg', '-i', str(wav_path), '-af', f'silencedetect=n={noise_db}dB:d={min_duration}',
         '-f', 'null', '-'],
        capture_output=True, text=True
    )
    starts = [float(m) for m in re.findall(r'silence_start: ([\d.]+)', result.stderr)]
    ends   = [float(m) for m in re.findall(r'silence_end: ([\d.]+)',   result.stderr)]
    return list(zip(starts, ends[:len(starts)]))


def split_wav_at_times(wav_path, split_times, out_dir, prefix):
    total      = get_audio_duration(wav_path)
    boundaries = [0.0] + split_times + [total]
    paths      = []
    for i in range(len(boundaries) - 1):
        out_path = out_dir / f"{prefix}_{i:03d}.wav"
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(wav_path),
             '-ss', f'{boundaries[i]:.6f}', '-to', f'{boundaries[i+1]:.6f}',
             '-ar', str(SAMPLE_RATE), '-ac', str(CHANNELS), str(out_path)],
            check=True, capture_output=True
        )
        paths.append(out_path)
    return paths


def split_audio(wav_path, n, out_dir, prefix):
    """
    Split into exactly n segments using the N-1 longest silences.

    Kanji TTS creates two kinds of silences:
      - intra-item: short pause at 時/分 boundary
      - inter-item: longer pause between separate time expressions

    Taking the N-1 longest silences correctly selects inter-item boundaries.
    """
    target_gaps = n - 1
    silences = detect_silences(wav_path, noise_db=-30, min_duration=0.15)

    if len(silences) < target_gaps:
        raise SplitError(f"Only {len(silences)} silences found, need {target_gaps}.")

    silences_by_len = sorted(silences, key=lambda s: s[1] - s[0], reverse=True)
    top_silences    = silences_by_len[:target_gaps]
    split_times     = sorted((s + e) / 2 for s, e in top_silences)

    durations = [f"{e-s:.2f}s" for s, e in sorted(top_silences, key=lambda x: x[0])]
    print(f"    Split: {len(silences)} silences found, using {target_gaps} longest → {durations}")

    return split_wav_at_times(wav_path, split_times, out_dir, prefix)


def fallback_individual(rotator, items, out_dir, prefix):
    print(f"    Fallback: {len(items)} individual TTS calls")
    paths = []
    for i, (kanji, _) in enumerate(items):
        print(f"      [{i+1}/{len(items)}] {kanji}")
        pcm      = generate_single_tts(rotator, kanji)
        wav_path = out_dir / f"{prefix}_fb_{i:03d}.wav"
        save_wav(pcm, wav_path)
        paths.append(wav_path)
    return paths


def wav_to_mp3(wav_path, mp3_path):
    subprocess.run(
        ['ffmpeg', '-y', '-i', str(wav_path), '-codec:a', 'libmp3lame', '-qscale:a', '2', str(mp3_path)],
        check=True, capture_output=True
    )


# ─── Verification (single Flash call for full batch) ─────────────────────────

class RateLimitError(Exception):
    pass


def normalize_hiragana(text):
    text = re.sub(r'[\s\u3000]', '', text)
    text = re.sub(r'[。、！？!?.,・]', '', text)
    result = []
    for char in text:
        code = ord(char)
        if 0x30A1 <= code <= 0x30F6:   # katakana → hiragana
            result.append(chr(code - 0x60))
        else:
            result.append(char)
    text = ''.join(result)
    return re.sub(r'[^\u3041-\u3096\u309D\u309E]', '', text)


def verify_batch_single_call(client, batch_wav_path, items):
    """
    Send the full batch WAV to Gemini Flash in ONE call.
    Returns (all_ok, errors, transcription_lines).
    Raises RateLimitError if the API is rate limited.
    """
    n = len(items)
    with open(batch_wav_path, "rb") as f:
        audio_bytes = f.read()

    prompt = (
        f"This audio contains {n} Japanese time readings spoken one by one with short pauses between them.\n"
        f"Transcribe all {n} readings in order in hiragana only.\n"
        f"Write exactly {n} lines, one reading per line. No numbering, no extra text."
    )

    try:
        response = client.models.generate_content(
            model=MODEL_VERIFY,
            contents=[
                types.Part(inline_data=types.Blob(data=audio_bytes, mime_type="audio/wav")),
                types.Part(text=prompt),
            ],
        )
        text = response.text or ""
    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            raise RateLimitError(f"Gemini Flash rate limited: {err[:120]}")
        raise

    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

    if len(lines) != n:
        return False, [
            {"index": -1, "kanji": "—",
             "expected": f"{n} lines",
             "got": f"Flash returned {len(lines)} lines: {lines}"}
        ], lines

    errors = []
    for i, (line, (kanji, _)) in enumerate(zip(lines, items)):
        # Extract hour and minute from kanji (items may span different hours)
        h_match = re.search(r'^(\d+)時', kanji)
        m_match = re.search(r'(\d+)分', kanji)
        h = int(h_match.group(1)) if h_match else 0
        m = int(m_match.group(1)) if m_match else 0
        accepted = get_accepted_readings(h, m)

        normalized_got = normalize_hiragana(line)
        is_ok = any(normalize_hiragana(a) in normalized_got or
                    normalized_got == normalize_hiragana(a)
                    for a in accepted)

        if is_ok:
            print(f"    ✓ [{i+1:02d}/{n}] {kanji}: '{line}'")
        else:
            print(f"    ✗ [{i+1:02d}/{n}] {kanji}: expected '{accepted[0]}', got '{line}'")
            errors.append({"index": i, "kanji": kanji, "expected": accepted[0], "got": line})

    return len(errors) == 0, errors, lines


# ─── Firebase ─────────────────────────────────────────────────────────────────

def initialize_firebase(bucket_name):
    if not _FIREBASE_AVAILABLE:
        print("firebase-admin not installed. Run: pip install firebase-admin")
        sys.exit(1)
    key_path = REPO_ROOT / "backend" / "service-account-key.json"
    options  = {"storageBucket": bucket_name}
    if key_path.exists():
        try:
            firebase_admin.initialize_app(credentials.Certificate(str(key_path)), options)
            print("Firebase initialized (service-account-key.json)")
            return
        except Exception as e:
            print(f"service-account-key.json error: {e}")
    try:
        firebase_admin.initialize_app(options=options)
        print("Firebase initialized (Application Default Credentials)")
    except Exception as e:
        print(f"Firebase init failed: {e}")
        sys.exit(1)


def upload_mp3s(bucket, mp3_paths):
    for mp3_path in mp3_paths:
        key         = mp3_path.stem
        remote_path = f"{STORAGE_PREFIX}/{key}.mp3"
        blob        = bucket.blob(remote_path)
        if blob.exists():
            print(f"    ~ {key}.mp3 (already exists)")
            continue
        blob.upload_from_filename(str(mp3_path), content_type="audio/mpeg")
        blob.make_public()
        print(f"    ↑ {key}.mp3")


# ─── Audio Generation (TTS → split → MP3 → pending/) ─────────────────────────

def generate_audio(rotator, bid, items):
    """
    Generate TTS for a batch, split into N segments, convert to MP3.
    Saves to PENDING_DIR/{bid}/:
      - batch.wav   (full audio, used for verification)
      - HHMM.mp3    (individual files)
    Returns (batch_wav_path, mp3_paths).
    """
    text      = batch_text(items)
    n         = len(items)
    first_k   = items[0][0]
    last_k    = items[-1][0]

    print(f"\n[Batch {bid}] {first_k} – {last_k}")
    print(f"  Text: {text}")
    print("  Generating TTS...")

    pcm = generate_tts(rotator, text)

    pending_dir = PENDING_DIR / bid
    pending_dir.mkdir(parents=True, exist_ok=True)

    batch_wav = pending_dir / "batch.wav"
    save_wav(pcm, batch_wav)
    duration = get_audio_duration(batch_wav)
    print(f"  Audio: {duration:.1f}s")

    tmp = Path(tempfile.mkdtemp(prefix="time_split_"))
    try:
        try:
            wav_paths = split_audio(batch_wav, n, tmp, "seg")
        except SplitError as e:
            print(f"  Split failed: {e}")
            wav_paths = fallback_individual(rotator, items, tmp, "seg")

        mp3_paths = []
        for wav_p, (kanji, _) in zip(wav_paths, items):
            h_m = re.search(r'^(\d+)時', kanji)
            m_m = re.search(r'(\d+)分', kanji)
            h   = int(h_m.group(1))
            m   = int(m_m.group(1)) if m_m else 0
            mp3_path = pending_dir / f"{h:02d}{m:02d}.mp3"
            wav_to_mp3(wav_p, mp3_path)
            mp3_paths.append(mp3_path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"  Audio saved → pending/{bid}/  ({len(mp3_paths)} MP3s + batch.wav)")
    return batch_wav, mp3_paths


# ─── Process One Batch ────────────────────────────────────────────────────────

def process_batch(rotator, verify_client, bid, start_idx, state, bucket, no_verify=False):
    """
    Full cycle for one batch.

    If tts_done state exists and pending files are present:
      → skips TTS generation, goes straight to verification (or save if no_verify).
    Otherwise:
      → generates TTS, saves to pending/, then verifies (or saves if no_verify).

    no_verify=True: skip verification, copy MP3s directly to output/.
    On rate limit: saves tts_done state, exits cleanly.
    Returns: "completed" | "pending_verification" | "failed"
    """
    hm_list     = CURATED_TIMES[start_idx:start_idx + BATCH_SIZE]
    items       = build_batch_items(hm_list)
    pending_dir = PENDING_DIR / bid
    tts_done    = state.get("tts_done", {})

    batch_wav  = pending_dir / "batch.wav"
    have_audio = bid in tts_done and pending_dir.exists() and batch_wav.exists()

    if have_audio:
        mp3_paths = sorted(pending_dir.glob("*.mp3"))
        if no_verify:
            print(f"\n[Batch {bid}] Audio in pending/ — saving directly (--no-verify)")
        else:
            print(f"\n[Batch {bid}] Resuming verification (audio already in pending/)")
    else:
        batch_wav, mp3_paths = generate_audio(rotator, bid, items)
        tts_done[bid] = {"pending_dir": str(pending_dir), "start_idx": start_idx}
        state["tts_done"] = tts_done
        save_state(state)

    # ── No-verify path ────────────────────────────────────────────────────────
    if no_verify:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        saved = []
        for mp3_path in mp3_paths:
            out = OUTPUT_DIR / mp3_path.name
            shutil.copy(str(mp3_path), str(out))
            saved.append(out)
        print(f"  Saved {len(saved)} MP3 files → output/  (no-verify)")

        if bucket:
            print("  Uploading to Firebase Storage...")
            upload_mp3s(bucket, saved)

        shutil.rmtree(str(pending_dir), ignore_errors=True)
        completed = state.setdefault("completed_batches", [])
        if bid not in completed:
            completed.append(bid)
        state.get("tts_done", {}).pop(bid, None)
        state.get("failed_batches", {}).pop(bid, None)
        save_state(state)
        return "completed"

    # ── Verify with a single Flash call ──────────────────────────────────────
    print("  Verifying batch (single Flash call)...")
    try:
        all_ok, errors, transcriptions = verify_batch_single_call(
            verify_client, batch_wav, items
        )
    except RateLimitError:
        print(f"\n  ⚠ Rate limited during verification.")
        print(f"  Audio is safe in pending/{bid}/")
        print(f"  Run again to retry verification — no TTS will be regenerated.")
        return "pending_verification"

    if all_ok:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        saved = []
        for mp3_path in mp3_paths:
            out = OUTPUT_DIR / mp3_path.name
            shutil.copy(str(mp3_path), str(out))
            saved.append(out)
        print(f"  Saved {len(saved)} MP3 files → output/")

        if bucket:
            print("  Uploading to Firebase Storage...")
            upload_mp3s(bucket, saved)

        shutil.rmtree(str(pending_dir), ignore_errors=True)
        completed = state.setdefault("completed_batches", [])
        if bid not in completed:
            completed.append(bid)
        state.get("tts_done", {}).pop(bid, None)
        state.get("failed_batches", {}).pop(bid, None)
        save_state(state)
        return "completed"

    else:
        print(f"\n  ✗ Verification failed ({len(errors)} content errors).")
        print(f"  Audio kept in pending/{bid}/ for manual review.")
        state.setdefault("failed_batches", {})[bid] = {
            "reason":  "verification_content",
            "errors":  [f"{e['kanji']}: expected '{e['expected']}', got '{e['got']}'" for e in errors],
            "pending_dir": str(pending_dir),
        }
        state.get("tts_done", {}).pop(bid, None)
        save_state(state)
        return "failed"


# ─── Status Printer ───────────────────────────────────────────────────────────

def print_status(result, state, batches):
    completed_set = set(state.get("completed_batches", []))
    tts_done      = state.get("tts_done", {})
    failed_set    = set(state.get("failed_batches", {}).keys())
    total         = len(batches)
    done          = len(completed_set)

    print(f"\nResult: {result}")
    print(f"Progress: {done}/{total} batches completed  ({done * BATCH_SIZE}/{len(CURATED_TIMES)} files)")

    if tts_done:
        print(f"Pending verification: {list(tts_done.keys())}")
    if failed_set:
        print(f"Failed (content): {list(failed_set)}")

    if tts_done:
        print(f"Next run: will verify pending batch {list(tts_done.keys())[0]}")
        return
    for bid, _ in batches:
        if bid not in completed_set and bid not in failed_set:
            print(f"Next run: will generate batch {bid}")
            return
    print("All batches processed!")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate 86 curated Japanese time audio MP3 files"
    )
    parser.add_argument("--bucket", default=None,
        help="Firebase Storage bucket. Omit to skip upload.")
    parser.add_argument("--batch", default=None,
        help="Process specific batch by ID (e.g. --batch 000-009)")
    parser.add_argument("--dry-run", action="store_true",
        help="Print batch info without making API calls")
    parser.add_argument("--no-verify", action="store_true",
        help="Skip verification — generate and save MP3s directly to output/")
    args = parser.parse_args()

    batches = all_batches()   # list of (bid, start_idx)

    # ── Dry run ──────────────────────────────────────────────────────────────
    if args.dry_run:
        print(f"=== DRY RUN — {len(CURATED_TIMES)} items in {len(batches)} batches ===\n")
        target_batches = batches
        if args.batch:
            target_batches = [(bid, si) for bid, si in batches if bid == args.batch]
            if not target_batches:
                print(f"Batch '{args.batch}' not found.")
                return
        for bid, si in target_batches:
            hm_list = CURATED_TIMES[si:si + BATCH_SIZE]
            items   = build_batch_items(hm_list)
            print(f"Batch {bid}: {batch_text(items)}")
            for i, (k, r) in enumerate(items):
                print(f"  [{i+1:02d}] {k}  →  {r}")
            print()
        return

    # ── Init ─────────────────────────────────────────────────────────────────
    api_keys      = load_api_keys()
    rotator       = KeyRotator(api_keys)
    verify_client = genai.Client(api_key=api_keys[0])
    print(f"API keys: {len(api_keys)} ({len(api_keys) * REQUESTS_PER_KEY} TTS req/min)")

    fb_bucket = None
    if args.bucket:
        initialize_firebase(args.bucket)
        fb_bucket = fb_storage.bucket()

    state         = load_state()
    completed_set = set(state.get("completed_batches", []))
    tts_done      = state.get("tts_done", {})
    failed_set    = set(state.get("failed_batches", {}).keys())
    done          = len(completed_set)

    print(f"\nProgress  : {done}/{len(batches)} batches  ({done * BATCH_SIZE}/{len(CURATED_TIMES)} files)")
    if tts_done:
        print(f"Pending   : {list(tts_done.keys())} (audio ready, awaiting verification)")
    if failed_set:
        print(f"Failed    : {list(failed_set)}")

    # ── Single batch mode ────────────────────────────────────────────────────
    if args.batch:
        for bid, si in batches:
            if bid == args.batch:
                result = process_batch(rotator, verify_client, bid, si, state, fb_bucket,
                                       no_verify=args.no_verify)
                print_status(result, state, batches)
                return
        print(f"Batch '{args.batch}' not found. Valid IDs: {[b for b,_ in batches]}")
        return

    # ── Priority 1: verify/save pending batch ────────────────────────────────
    if tts_done:
        bid  = next(iter(tts_done))
        info = tts_done[bid]
        si   = info["start_idx"]
        result = process_batch(rotator, verify_client, bid, si, state, fb_bucket,
                               no_verify=args.no_verify)
        print_status(result, state, batches)
        return

    # ── Priority 2: generate next unprocessed batch ───────────────────────────
    for bid, si in batches:
        if bid not in completed_set and bid not in failed_set:
            result = process_batch(rotator, verify_client, bid, si, state, fb_bucket,
                                   no_verify=args.no_verify)
            print_status(result, state, batches)
            return

    print("\nAll batches processed!")
    if failed_set:
        print(f"Failed batches needing review: {list(failed_set)}")


if __name__ == "__main__":
    main()

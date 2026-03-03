#!/usr/bin/env python3
"""
Gemini TTS Audio Generator for Time Trainer.

Batch strategy (7 API calls vs 1440 naive):
  - 24 hour readings  → 1 API call  → silencedetect split → 24 WAV files
  - 60 minute readings → 6 API calls (batches of 10) → split → 60 WAV files
  - 1440 combinations → ffmpeg concat (local, zero API calls)
  - Upload → Firebase Storage (idempotent: skips existing files)

Usage:
    python generate_time_audio.py --bucket jlpt-bites.firebasestorage.app
    python generate_time_audio.py --bucket ... --output-dir /tmp/time_audio
    python generate_time_audio.py --bucket ... --test --hours 1 2 3 --minutes 0 15 30

Environment:
    GEMINI_API_KEY or GEMINI_API_KEYS (comma-separated)

Requirements:
    pip install google-genai firebase-admin
    brew install ffmpeg
"""

import os
import sys
import time
import wave
import subprocess
import tempfile
import argparse
import re
import shutil
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

# Minute 0 has no reading (just say the hour)
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

# ─── TTS Config ───────────────────────────────────────────────────────────────

MODEL = "gemini-2.5-flash-preview-tts"
VOICE = "Kore"
SAMPLE_RATE = 24000
SAMPLE_WIDTH = 2
CHANNELS = 1

REQUESTS_PER_KEY = 3  # free tier: 3 req/min
MAX_RETRIES = 3

STORAGE_PREFIX = "time_trainer/audio"


# ─── Key Rotator (same pattern as generate_tts_audio.py) ─────────────────────

class KeyRotator:
    def __init__(self, api_keys):
        self.keys = api_keys
        self.clients = [genai.Client(api_key=k) for k in api_keys]
        self.usage = [0] * len(api_keys)
        self.window_start = [0.0] * len(api_keys)
        self.current = 0

    def get_client(self):
        now = time.time()
        attempts = 0
        while attempts < len(self.keys):
            idx = self.current
            elapsed = now - self.window_start[idx]
            if elapsed >= 60:
                self.usage[idx] = 0
                self.window_start[idx] = now
            if self.usage[idx] < REQUESTS_PER_KEY:
                return idx, self.clients[idx]
            self.current = (self.current + 1) % len(self.keys)
            attempts += 1

        oldest = min(range(len(self.keys)), key=lambda i: self.window_start[i])
        wait = 60 - (time.time() - self.window_start[oldest]) + 2
        if wait > 0:
            print(f"  All {len(self.keys)} keys exhausted. Waiting {wait:.0f}s...")
            time.sleep(wait)
        self.usage[oldest] = 0
        self.window_start[oldest] = time.time()
        self.current = oldest
        return oldest, self.clients[oldest]

    def record_usage(self, idx):
        self.usage[idx] += 1
        self.current = (self.current + 1) % len(self.keys)


def load_api_keys():
    keys_str = os.environ.get("GEMINI_API_KEYS")
    if keys_str:
        keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if keys:
            return keys

    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return [key]

    env_paths = [
        Path(__file__).parent.parent.parent.parent / ".env",
        Path(__file__).parent / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEYS="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        return [k.strip() for k in val.split(",") if k.strip()]
                    if line.startswith("GEMINI_API_KEY="):
                        return [line.split("=", 1)[1].strip().strip('"').strip("'")]

    print("GEMINI_API_KEY(S) not found.")
    print("Set with: export GEMINI_API_KEYS='key1,key2'")
    sys.exit(1)


# ─── TTS Generation ──────────────────────────────────────────────────────────

def generate_batch_tts(rotator, items, label):
    """
    Generate TTS for a list of Japanese readings in a single API call.
    Items are read one by one with 2-second pauses between them.
    Returns raw PCM bytes (24kHz, 16-bit, mono).
    """
    # Join with regular space — newlines/fullwidth-space cause FinishReason.OTHER
    items_text = " ".join(items)
    prompt = (
        f"Speak the following Japanese text slowly and clearly, "
        f"as a formal narrator for a JLPT language listening exam. "
        f"Use a slow, measured pace with clear pronunciation:\n{items_text}"
    )

    print(f"  TTS batch [{label}]: {len(items)} items → {', '.join(items[:3])}{'...' if len(items) > 3 else ''}")

    for attempt in range(1, MAX_RETRIES + 1):
        idx, client = rotator.get_client()
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=VOICE
                            )
                        )
                    ),
                ),
            )
            rotator.record_usage(idx)
            c = response.candidates[0]
            if c.content is None:
                raise RuntimeError(
                    f"TTS returned no audio (finish_reason={c.finish_reason}). "
                    f"Try adjusting the prompt or use individual calls."
                )
            return c.content.parts[0].inline_data.data

        except RuntimeError:
            raise  # propagate no-audio errors immediately
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                if "PerDay" in err or "daily" in err.lower():
                    # Daily quota exhausted — all keys are likely affected
                    print(f"    Key {idx+1} daily quota exhausted.")
                    rotator.usage[idx] = REQUESTS_PER_KEY
                    rotator.current = (idx + 1) % len(rotator.keys)
                else:
                    rotator.usage[idx] = REQUESTS_PER_KEY
                    rotator.current = (idx + 1) % len(rotator.keys)
                    print(f"    Key {idx+1} rate limited (attempt {attempt}/{MAX_RETRIES}), rotating...")
            elif "500" in err or "INTERNAL" in err:
                wait = 5 * attempt
                print(f"    Server error (attempt {attempt}/{MAX_RETRIES}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"Failed after {MAX_RETRIES} retries for batch [{label}]")


def generate_single_tts(rotator, text, label):
    """Fallback: single item TTS call."""
    prompt = (
        f"Speak the following Japanese text slowly and clearly, "
        f"as a formal narrator for a JLPT language listening exam. "
        f"Use a slow, measured pace with clear pronunciation:\n{text}"
    )
    for attempt in range(1, MAX_RETRIES + 1):
        idx, client = rotator.get_client()
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=VOICE
                            )
                        )
                    ),
                ),
            )
            rotator.record_usage(idx)
            c = response.candidates[0]
            if c.content is None:
                raise RuntimeError(
                    f"TTS returned no audio for '{text}' (finish_reason={c.finish_reason})"
                )
            return c.content.parts[0].inline_data.data
        except RuntimeError:
            raise
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                rotator.usage[idx] = REQUESTS_PER_KEY
                rotator.current = (idx + 1) % len(rotator.keys)
                print(f"    Key {idx+1} rate limited (attempt {attempt}/{MAX_RETRIES}), rotating...")
            elif "500" in err or "INTERNAL" in err:
                wait = 5 * attempt
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Failed after {MAX_RETRIES} retries: {text}")


# ─── WAV I/O ──────────────────────────────────────────────────────────────────

def save_wav(pcm_data, path):
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)


def get_audio_duration(path):
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', str(path)],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())


# ─── Silence Detection & Splitting ───────────────────────────────────────────

class SplitError(Exception):
    pass


def detect_silences(wav_path, noise_db=-35, min_duration=0.4):
    """
    Run ffmpeg silencedetect and return list of (start, end) tuples.
    noise_db:     silence threshold in dB (e.g. -35 means anything quieter is silence)
    min_duration: minimum silence length in seconds to count
    """
    result = subprocess.run(
        ['ffmpeg', '-i', str(wav_path),
         '-af', f'silencedetect=n={noise_db}dB:d={min_duration}',
         '-f', 'null', '-'],
        capture_output=True, text=True
    )
    output = result.stderr

    starts = [float(m) for m in re.findall(r'silence_start: ([\d.]+)', output)]
    ends = [float(m) for m in re.findall(r'silence_end: ([\d.]+)', output)]

    # Last silence might not have an end (reaches EOF)
    pairs = list(zip(starts, ends[:len(starts)]))
    return pairs


def split_wav(wav_path, split_times, out_dir, prefix):
    """
    Split wav_path at given split_times (seconds) into len(split_times)+1 segments.
    Returns list of output paths.
    """
    total = get_audio_duration(wav_path)
    boundaries = [0.0] + split_times + [total]
    paths = []

    for i in range(len(boundaries) - 1):
        t_start = boundaries[i]
        t_end = boundaries[i + 1]
        out_path = out_dir / f"{prefix}_{i:03d}.wav"
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(wav_path),
             '-ss', f'{t_start:.6f}', '-to', f'{t_end:.6f}',
             '-ar', str(SAMPLE_RATE), '-ac', str(CHANNELS),
             str(out_path)],
            check=True, capture_output=True
        )
        paths.append(out_path)

    return paths


def split_batch_audio(wav_path, expected_n, out_dir, prefix):
    """
    Split a batch WAV file into exactly expected_n segments using silence detection.
    Tries progressively relaxed thresholds before raising SplitError.
    Returns list of output paths in order.
    """
    # We need (expected_n - 1) split points between items
    target_gaps = expected_n - 1

    # Try different noise thresholds — start strict, relax if needed
    for noise_db, min_dur in [(-35, 0.4), (-30, 0.3), (-25, 0.2)]:
        silences = detect_silences(wav_path, noise_db=noise_db, min_duration=min_dur)

        if len(silences) >= target_gaps:
            # Use the first target_gaps silences as split points (midpoints)
            split_times = [(s + e) / 2 for s, e in silences[:target_gaps]]
            print(f"    Split: found {len(silences)} silences, using {target_gaps} "
                  f"(threshold={noise_db}dB, min={min_dur}s)")
            return split_wav(wav_path, split_times, out_dir, prefix)

    raise SplitError(
        f"Could not find {target_gaps} silences in {wav_path.name} "
        f"(best: {len(detect_silences(wav_path))} found). "
        f"Will fallback to individual API calls."
    )


# ─── MP3 Conversion & Concatenation ──────────────────────────────────────────

def wav_to_mp3(wav_path, mp3_path):
    """Convert WAV to MP3 using ffmpeg."""
    subprocess.run(
        ['ffmpeg', '-y', '-i', str(wav_path),
         '-codec:a', 'libmp3lame', '-qscale:a', '2',
         str(mp3_path)],
        check=True, capture_output=True
    )


def concat_mp3s(part_paths, out_path):
    """
    Concatenate multiple MP3 files using ffmpeg filter_complex.
    Adds a short 50ms silence between parts for natural transition.
    """
    if len(part_paths) == 1:
        shutil.copy(str(part_paths[0]), str(out_path))
        return

    # Build concat filter: [0:a][silence][1:a] concat
    # Use a simpler approach: concat demuxer
    list_file = out_path.parent / f"_concat_{out_path.stem}.txt"
    try:
        with open(list_file, "w") as f:
            for p in part_paths:
                f.write(f"file '{p.resolve()}'\n")

        subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
             '-i', str(list_file),
             '-codec:a', 'libmp3lame', '-qscale:a', '2',
             str(out_path)],
            check=True, capture_output=True
        )
    finally:
        if list_file.exists():
            list_file.unlink()


# ─── Firebase ────────────────────────────────────────────────────────────────

def initialize_firebase(bucket_name):
    if not _FIREBASE_AVAILABLE:
        print("firebase_admin not installed. Run: pip install firebase-admin")
        sys.exit(1)

    key_path = Path(__file__).parent.parent.parent / 'service-account-key.json'
    options = {'storageBucket': bucket_name}

    if key_path.exists():
        try:
            cred = credentials.Certificate(str(key_path))
            firebase_admin.initialize_app(cred, options)
            print(f"Firebase initialized (service-account-key.json)")
            return
        except Exception as e:
            print(f"service-account-key.json load error: {e}")

    try:
        firebase_admin.initialize_app(options=options)
        print("Firebase initialized (Application Default Credentials)")
    except Exception as e:
        print(f"Firebase init failed: {e}")
        sys.exit(1)


def storage_exists(bucket, remote_path):
    blob = bucket.blob(remote_path)
    return blob.exists()


def upload_mp3(bucket, local_path, remote_path):
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(str(local_path), content_type="audio/mpeg")
    blob.make_public()
    return blob.public_url


# ─── Core Pipeline ────────────────────────────────────────────────────────────

def generate_and_split_batch(rotator, items, labels, out_dir, prefix):
    """
    Generate TTS for a batch of items, split into individual WAV files.
    Falls back to individual API calls if splitting fails.
    Returns dict: {label: wav_path}
    """
    # Try batch approach first
    print(f"\n[Batch] {prefix}: {len(items)} items")
    try:
        pcm = generate_batch_tts(rotator, items, prefix)
        batch_wav = out_dir / f"{prefix}_batch.wav"
        save_wav(pcm, batch_wav)

        duration = get_audio_duration(batch_wav)
        print(f"    Batch audio: {duration:.1f}s")

        segment_paths = split_batch_audio(batch_wav, len(items), out_dir, prefix)
        batch_wav.unlink()  # Clean up batch file

        result = {}
        for label, seg_path in zip(labels, segment_paths):
            named_path = out_dir / f"{label}.wav"
            seg_path.rename(named_path)
            result[label] = named_path
            print(f"    ✓ {label}.wav ({get_audio_duration(named_path):.2f}s)")

        return result

    except SplitError as e:
        print(f"    ⚠ Batch split failed: {e}")
        print(f"    Falling back to {len(items)} individual API calls...")

    # Fallback: individual calls
    result = {}
    for item, label in zip(items, labels):
        print(f"    [Fallback] {label}: {item}")
        pcm = generate_single_tts(rotator, item, label)
        wav_path = out_dir / f"{label}.wav"
        save_wav(pcm, wav_path)
        result[label] = wav_path
        print(f"    ✓ {label}.wav")

    return result


def run_pipeline(rotator, hours_to_process, minutes_to_process, output_dir, bucket):
    """
    Full pipeline:
      1. Generate hour WAVs (batch)
      2. Generate minute WAVs (batches of 10)
      3. Combine into HHMM.mp3
      4. Upload to Storage
    """
    output_dir = Path(output_dir)
    wav_dir = output_dir / "wav"
    mp3_dir = output_dir / "mp3"
    wav_dir.mkdir(parents=True, exist_ok=True)
    mp3_dir.mkdir(parents=True, exist_ok=True)

    hour_wavs = {}  # {hour_int: Path}
    minute_wavs = {}  # {minute_int: Path}

    # ── Step 1: Hours ──────────────────────────────────────────────────────────
    hours_needed = sorted(set(hours_to_process))
    hour_items = [HOUR_READINGS[h] for h in hours_needed]
    hour_labels = [f"hour_{h:02d}" for h in hours_needed]

    hour_results = generate_and_split_batch(
        rotator, hour_items, hour_labels, wav_dir, "hours"
    )
    for h, label in zip(hours_needed, hour_labels):
        hour_wavs[h] = hour_results[label]

    # ── Step 2: Minutes (batches of 10) ───────────────────────────────────────
    minutes_needed = sorted(m for m in minutes_to_process if m > 0)

    # Group into batches of 10
    batches = []
    for i in range(0, len(minutes_needed), 10):
        batches.append(minutes_needed[i:i + 10])

    for batch_idx, batch in enumerate(batches):
        min_items = [MINUTE_READINGS[m] for m in batch]
        min_labels = [f"min_{m:02d}" for m in batch]
        prefix = f"minutes_batch{batch_idx + 1}"

        min_results = generate_and_split_batch(
            rotator, min_items, min_labels, wav_dir, prefix
        )
        for m, label in zip(batch, min_labels):
            minute_wavs[m] = min_results[label]

    # ── Step 3: Combine hour + minute → HHMM.mp3 ─────────────────────────────
    print(f"\n[Combine] Building {len(hours_to_process) * len(minutes_to_process)} MP3 files...")

    mp3_files = {}
    for h in hours_to_process:
        for m in minutes_to_process:
            key = f"{h:02d}{m:02d}"
            mp3_path = mp3_dir / f"{key}.mp3"

            if mp3_path.exists():
                mp3_files[key] = mp3_path
                continue

            if m == 0:
                # Minute 0: just the hour
                wav_to_mp3(hour_wavs[h], mp3_path)
            else:
                # Concat hour + minute WAVs → MP3
                hour_mp3_tmp = mp3_dir / f"_h{h:02d}.mp3"
                min_mp3_tmp = mp3_dir / f"_m{m:02d}.mp3"

                if not hour_mp3_tmp.exists():
                    wav_to_mp3(hour_wavs[h], hour_mp3_tmp)
                if not min_mp3_tmp.exists():
                    wav_to_mp3(minute_wavs[m], min_mp3_tmp)

                concat_mp3s([hour_mp3_tmp, min_mp3_tmp], mp3_path)

            mp3_files[key] = mp3_path

    # Clean up temp per-hour/minute MP3s
    for f in mp3_dir.glob("_h*.mp3"):
        f.unlink()
    for f in mp3_dir.glob("_m*.mp3"):
        f.unlink()

    print(f"  ✓ {len(mp3_files)} MP3 files built in {mp3_dir}")

    # ── Step 4: Upload ─────────────────────────────────────────────────────────
    if bucket is None:
        print("\n[Upload] No bucket specified — skipping upload.")
        print(f"  MP3 files ready in: {mp3_dir}")
        return mp3_files

    print(f"\n[Upload] Uploading to gs://{bucket.name}/{STORAGE_PREFIX}/...")
    uploaded = 0
    skipped = 0

    for key, mp3_path in sorted(mp3_files.items()):
        remote_path = f"{STORAGE_PREFIX}/{key}.mp3"
        if storage_exists(bucket, remote_path):
            skipped += 1
            continue

        url = upload_mp3(bucket, mp3_path, remote_path)
        uploaded += 1
        print(f"  ↑ {key}.mp3 → {url}")

    print(f"\n  ✓ Uploaded: {uploaded}  Skipped (already exist): {skipped}")
    return mp3_files


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate time trainer audio files using Gemini TTS"
    )
    parser.add_argument(
        "--bucket", default=None,
        help="Firebase Storage bucket (e.g. jlpt-bites.firebasestorage.app). "
             "Omit to skip upload."
    )
    parser.add_argument(
        "--output-dir", default="/tmp/time_audio",
        help="Local output directory (default: /tmp/time_audio)"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Test mode: process only the hours/minutes specified below"
    )
    parser.add_argument(
        "--hours", type=int, nargs="+", default=list(range(24)),
        help="Hours to process (0-23). Default: all 24."
    )
    parser.add_argument(
        "--minutes", type=int, nargs="+", default=list(range(60)),
        help="Minutes to process (0-59). Default: all 60."
    )
    args = parser.parse_args()

    # Validate ranges
    hours = sorted(set(h for h in args.hours if 0 <= h <= 23))
    minutes = sorted(set(m for m in args.minutes if 0 <= m <= 59))

    if not hours or not minutes:
        print("No valid hours or minutes specified.")
        sys.exit(1)

    total_combinations = len(hours) * len(minutes)
    minutes_no_zero = [m for m in minutes if m > 0]
    minutes_batches = (len(minutes_no_zero) + 9) // 10
    total_api_calls = 1 + minutes_batches  # 1 for all hours + batches for minutes

    print("=" * 60)
    print("Time Trainer Audio Generator")
    print("=" * 60)
    print(f"  Hours:        {len(hours)} ({hours[0]}–{hours[-1]})")
    print(f"  Minutes:      {len(minutes)} ({minutes[0]}–{minutes[-1]})")
    print(f"  Combinations: {total_combinations}")
    print(f"  API calls:    ~{total_api_calls} (vs {total_combinations} naive)")
    print(f"  Output dir:   {args.output_dir}")
    print(f"  Bucket:       {args.bucket or '(none — local only)'}")
    if args.test:
        print("  Mode:         TEST")
    print()

    # Load API keys
    api_keys = load_api_keys()
    rotator = KeyRotator(api_keys)
    print(f"API keys loaded: {len(api_keys)} ({len(api_keys) * REQUESTS_PER_KEY} req/min)")

    # Initialize Firebase
    fb_bucket = None
    if args.bucket:
        initialize_firebase(args.bucket)
        fb_bucket = fb_storage.bucket()

    # Run
    start_time = time.time()
    run_pipeline(rotator, hours, minutes, args.output_dir, fb_bucket)
    elapsed = time.time() - start_time

    print(f"\nDone in {elapsed:.0f}s")


if __name__ == "__main__":
    main()

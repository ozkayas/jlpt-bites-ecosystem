#!/usr/bin/env python3
"""
Gemini TTS Audio Generator for JLPT Listening Questions.

Uses a hybrid approach:
  - Intro & Question repeat: Single-speaker API calls (formal narrator voice)
  - Dialogue: Multi-speaker API call (natural conversational flow)
  - Breaks: Generated silence segments

All segments are stitched together into a final WAV file.

Supports multiple API keys with round-robin rotation to avoid rate limits.

Usage:
    python generate_tts_audio.py <question_json_file> [--output <output.wav>]

Requirements:
    pip install google-genai

Environment:
    GEMINI_API_KEY (single key) or GEMINI_API_KEYS (comma-separated) must be set.
"""

import json
import sys
import os
import wave
import time
import argparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai package not found. Install with:")
    print("  pip install google-genai")
    sys.exit(1)


# ─── Voice Mapping ───────────────────────────────────────────────────────────
VOICE_MAP = {
    "Intro_Voice": "Kore",      # Firm, formal — narrator
    "Male_1":      "Puck",      # Upbeat — young male
    "Female_1":    "Zephyr",    # Bright — young female
}

# Speaker names used in multi-speaker dialogue prompt
SPEAKER_NAMES = {
    "Male_1":   "Man",
    "Female_1": "Woman",
}

MODEL = "gemini-2.5-flash-preview-tts"

# Audio format: 24kHz, 16-bit, mono
SAMPLE_RATE = 24000
SAMPLE_WIDTH = 2
CHANNELS = 1

# Rate limiting per key: free tier = 3 req/min
REQUESTS_PER_KEY = 3
MAX_RETRIES = 3


class KeyRotator:
    """Round-robin API key manager with per-key rate tracking."""

    def __init__(self, api_keys):
        self.keys = api_keys
        self.clients = [genai.Client(api_key=k) for k in api_keys]
        self.usage = [0] * len(api_keys)
        self.window_start = [0.0] * len(api_keys)
        self.current = 0

    def get_client(self):
        """Get the next available client, rotating keys."""
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

        # All keys exhausted — wait for first key to reset
        oldest = min(range(len(self.keys)), key=lambda i: self.window_start[i])
        wait = 60 - (now - self.window_start[oldest]) + 2
        if wait > 0:
            print(f"    All {len(self.keys)} keys exhausted. Waiting {wait:.0f}s...")
            time.sleep(wait)
        self.usage[oldest] = 0
        self.window_start[oldest] = time.time()
        self.current = oldest
        return oldest, self.clients[oldest]

    def record_usage(self, idx):
        """Record that a request was made with the given key index."""
        self.usage[idx] += 1
        self.current = (self.current + 1) % len(self.keys)


def load_api_keys():
    """Load API keys from environment or .env file."""
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
    print("Set with: export GEMINI_API_KEYS='key1,key2,key3'")
    sys.exit(1)


# ─── Single Speaker TTS ─────────────────────────────────────────────────────

def generate_single_speech(rotator, text, voice_name):
    """Generate single-speaker audio with retry and key rotation."""
    # Wrap with slow/clear instruction for language exam style
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
                                voice_name=voice_name
                            )
                        )
                    ),
                ),
            )
            rotator.record_usage(idx)
            return response.candidates[0].content.parts[0].inline_data.data

        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                rotator.usage[idx] = REQUESTS_PER_KEY
                rotator.current = (idx + 1) % len(rotator.keys)
                print(f"    Key {idx+1} rate limited (attempt {attempt}/{MAX_RETRIES}), rotating...")
            elif "500" in err or "INTERNAL" in err:
                wait = 5 * attempt
                print(f"    Server error (attempt {attempt}/{MAX_RETRIES}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"Failed after {MAX_RETRIES} retries: {text[:50]}...")


# ─── Multi-Speaker Dialogue TTS ─────────────────────────────────────────────

def generate_dialogue_speech(rotator, dialogue_entries):
    """Generate multi-speaker dialogue audio in a single API call."""

    # Collect unique speakers from dialogue
    speakers_in_dialogue = []
    seen = set()
    for entry in dialogue_entries:
        voice_id = entry["voice"]
        if voice_id not in seen:
            seen.add(voice_id)
            speakers_in_dialogue.append(voice_id)

    # Build speaker voice configs
    speaker_configs = []
    for voice_id in speakers_in_dialogue:
        speaker_name = SPEAKER_NAMES.get(voice_id, voice_id)
        gemini_voice = VOICE_MAP.get(voice_id, "Kore")
        speaker_configs.append(
            types.SpeakerVoiceConfig(
                speaker=speaker_name,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=gemini_voice
                    )
                )
            )
        )

    # Build dialogue text prompt — keep instruction minimal for multi-speaker mode
    speaker_names_list = [SPEAKER_NAMES.get(s, s) for s in speakers_in_dialogue]
    dialogue_lines = []
    for entry in dialogue_entries:
        speaker_name = SPEAKER_NAMES.get(entry["voice"], entry["voice"])
        dialogue_lines.append(f"{speaker_name}: {entry['text']}")

    prompt = (
        f"TTS the following slow-paced Japanese conversation between "
        f"{' and '.join(speaker_names_list)}. Speak slowly and clearly:\n"
        + "\n".join(dialogue_lines)
    )

    prompt_lines = [prompt]  # for display

    print(f"  Dialogue prompt:\n    " + "\n    ".join(prompt_lines))

    # Make API call with retry
    for attempt in range(1, MAX_RETRIES + 1):
        idx, client = rotator.get_client()
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                            speaker_voice_configs=speaker_configs
                        )
                    ),
                ),
            )
            rotator.record_usage(idx)
            return response.candidates[0].content.parts[0].inline_data.data

        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                rotator.usage[idx] = REQUESTS_PER_KEY
                rotator.current = (idx + 1) % len(rotator.keys)
                print(f"    Key {idx+1} rate limited (attempt {attempt}/{MAX_RETRIES}), rotating...")
            elif "500" in err or "INTERNAL" in err:
                wait = 5 * attempt
                print(f"    Server error (attempt {attempt}/{MAX_RETRIES}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"Failed after {MAX_RETRIES} retries for dialogue")


# ─── Silence ─────────────────────────────────────────────────────────────────

def generate_silence(duration_seconds):
    """Generate silence as raw PCM bytes."""
    num_samples = int(SAMPLE_RATE * duration_seconds)
    return b'\x00' * (num_samples * SAMPLE_WIDTH)


def parse_break_duration(break_str):
    s = break_str.strip().lower()
    if s.endswith("s"):
        return float(s[:-1])
    return float(s)


# ─── Smart Script Processor ─────────────────────────────────────────────────

def process_tts_script(rotator, tts_script):
    """
    Process tts_script with hybrid approach:
    - Groups consecutive dialogue entries (Male_1, Female_1) into one multi-speaker call
    - Intro_Voice entries are single-speaker calls
    - Break entries between dialogue lines are skipped (Gemini handles pacing)
    - Break entries between sections are kept as silence
    """
    all_audio = bytearray()

    # Parse script into segments: intro, dialogue_group, break, question
    segments = []
    i = 0
    while i < len(tts_script):
        entry = tts_script[i]

        if "voice" in entry and entry["voice"] == "Intro_Voice":
            segments.append({"type": "single", "entry": entry})
            i += 1

        elif "voice" in entry and entry["voice"] in ("Male_1", "Female_1"):
            # Collect consecutive dialogue entries (skip breaks between them)
            dialogue_group = [entry]
            i += 1
            while i < len(tts_script):
                next_entry = tts_script[i]
                if "voice" in next_entry and next_entry["voice"] in ("Male_1", "Female_1"):
                    dialogue_group.append(next_entry)
                    i += 1
                elif "break" in next_entry:
                    # Check if next non-break entry is still dialogue
                    peek = i + 1
                    if peek < len(tts_script) and "voice" in tts_script[peek] and tts_script[peek]["voice"] in ("Male_1", "Female_1"):
                        # Skip this break — Gemini handles dialogue pacing
                        i += 1
                    else:
                        break
                else:
                    break
            segments.append({"type": "dialogue", "entries": dialogue_group})

        elif "break" in entry:
            segments.append({"type": "break", "duration": parse_break_duration(entry["break"])})
            i += 1

        else:
            i += 1

    # Process segments
    total = len(segments)
    for idx, seg in enumerate(segments):
        step = f"[{idx+1}/{total}]"

        if seg["type"] == "single":
            entry = seg["entry"]
            gemini_voice = VOICE_MAP.get(entry["voice"], "Kore")
            print(f"  {step} Single [{gemini_voice}]: {entry['text']}")
            audio = generate_single_speech(rotator, entry["text"], gemini_voice)
            all_audio.extend(audio)

        elif seg["type"] == "dialogue":
            entries = seg["entries"]
            print(f"  {step} Multi-speaker dialogue ({len(entries)} lines):")
            audio = generate_dialogue_speech(rotator, entries)
            all_audio.extend(audio)

        elif seg["type"] == "break":
            print(f"  {step} Silence: {seg['duration']}s")
            all_audio.extend(generate_silence(seg["duration"]))

    return bytes(all_audio)


# ─── WAV Output ──────────────────────────────────────────────────────────────

def save_wav(pcm_data, output_path):
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)

    file_size = os.path.getsize(output_path)
    duration = len(pcm_data) / (SAMPLE_RATE * SAMPLE_WIDTH * CHANNELS)
    print(f"\nSaved: {output_path}")
    print(f"  Duration: {duration:.1f}s | Size: {file_size / 1024:.0f} KB")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate TTS audio from JLPT listening question JSON"
    )
    parser.add_argument("input_file", help="Path to the question JSON file")
    parser.add_argument("--output", "-o", help="Output WAV file path")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    with open(input_path) as f:
        question = json.load(f)

    question_id = question.get("id", "unknown")
    tts_script = question.get("tts_script")
    if not tts_script:
        print("No tts_script found in JSON file")
        sys.exit(1)

    # Load API keys
    api_keys = load_api_keys()
    rotator = KeyRotator(api_keys)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".wav")

    # Count API calls: 1 intro + 1 dialogue + 1 question = 3 calls
    print(f"Question: {question_id}")
    print(f"API keys: {len(api_keys)} ({len(api_keys) * REQUESTS_PER_KEY} req/min)")
    print(f"Mode: Hybrid (single intro/question + multi-speaker dialogue)")
    print(f"Output: {output_path}")
    print()

    print("Generating audio...")
    start_time = time.time()
    pcm_audio = process_tts_script(rotator, tts_script)
    elapsed = time.time() - start_time

    save_wav(pcm_audio, output_path)
    print(f"Total time: {elapsed:.0f}s")
    print("Done!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generates image.png for a processed JLPT N5 listening variation clip
by calling the Gemini API with the image_prompt from derived-data.json.

API key: set JLPT_IMAGE_GEMINI_API_KEY in your environment.
  (kept separate from any other GEMINI_API_KEY you may have)

Usage:
  python generate_image.py                           # auto-discover latest clip missing image.png
  python generate_image.py clip_01_01m06s_02m06s     # named clip (searches processed/ then tobeprocessed/)
  python generate_image.py /absolute/path/to/clip/   # absolute path
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Repo layout ──────────────────────────────────────────────────────────────
# This script lives at:  skills/jlpt-n5-listening-variation-creator/scripts/generate_image.py
# Clip folders live at:  backend/listening/listening-youtube-data/processed/<clip>/
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]  # scripts/ → skill/ → skills/ → repo root
PROCESSED_DIR = REPO_ROOT / "backend" / "listening" / "data" / "selectImage" / "listening-youtube-data" / "processed"
TOBEPROCESSED_DIR = REPO_ROOT / "backend" / "listening" / "data" / "selectImage" / "listening-youtube-data" / "tobeprocessed"

ENV_KEY_NAME = "JLPT_IMAGE_GEMINI_API_KEY"
MODEL_ID = "gemini-2.5-flash-image"
OUTPUT_FILENAME = "image.png"


def find_clip_folder(name: Optional[str]) -> Path:
    """Resolve the clip folder from a name, absolute path, or auto-discover."""
    if name is None:
        # Auto-discover: find clip folders in processed/ that are missing image.png
        candidates = sorted(
            [d for d in PROCESSED_DIR.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )
        for candidate in candidates:
            if not (candidate / OUTPUT_FILENAME).exists():
                print(f"[auto] Found clip missing image.png: {candidate.name}")
                return candidate
        print("✗ All clips in processed/ already have image.png. Nothing to do.")
        sys.exit(0)

    # Absolute path provided
    p = Path(name)
    if p.is_absolute() and p.is_dir():
        return p

    # Clip name provided — search processed/ then tobeprocessed/
    for search_dir in (PROCESSED_DIR, TOBEPROCESSED_DIR):
        candidate = search_dir / name
        if candidate.is_dir():
            return candidate

    print(f"✗ Clip folder not found: {name!r}")
    print(f"  Searched in:\n    {PROCESSED_DIR}\n    {TOBEPROCESSED_DIR}")
    sys.exit(1)


def load_image_prompt(clip_folder: Path) -> str:
    """Read derived-data.json and return the image_prompt string."""
    derived = clip_folder / "derived-data.json"
    if not derived.exists():
        print(f"✗ derived-data.json not found in: {clip_folder}")
        sys.exit(1)

    with open(derived, "r", encoding="utf-8") as f:
        data = json.load(f)

    prompt = data.get("visual_prompts", {}).get("image_prompt", "")
    if not prompt:
        print("✗ visual_prompts.image_prompt is missing or empty in derived-data.json")
        sys.exit(1)

    return prompt


def generate_and_save(clip_folder: Path, prompt: str, api_key: str) -> None:
    """Call Gemini API and save the first image part as image.png."""
    try:
        from google import genai  # type: ignore
    except ImportError:
        print("✗ google-genai package not installed.")
        print("  Install with:  pip install google-genai")
        sys.exit(1)

    output_path = clip_folder / OUTPUT_FILENAME

    if output_path.exists():
        print(f"⚠  {OUTPUT_FILENAME} already exists in {clip_folder.name} — skipping.")
        print("   Delete it first if you want to regenerate.")
        sys.exit(0)

    print(f"[api] Calling {MODEL_ID} …")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[prompt],
    )

    # Find the first image part in the response
    image_part = None
    for part in response.parts:
        if part.inline_data is not None:
            image_part = part
            break

    if image_part is None:
        print("✗ No image returned by the API. Full response:")
        for part in response.parts:
            if part.text:
                print(f"  text: {part.text[:500]}")
        sys.exit(1)

    # Save using PIL if available, otherwise write raw bytes
    try:
        image = image_part.as_image()
        image.save(str(output_path))
    except Exception:
        # Fallback: write raw bytes directly
        import base64
        raw = base64.b64decode(image_part.inline_data.data)
        output_path.write_bytes(raw)

    print(f"✓ Image saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate image.png for a JLPT N5 listening clip via Gemini API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "clip",
        nargs="?",
        default=None,
        help="Clip folder name or absolute path. Omit to auto-discover.",
    )
    args = parser.parse_args()

    # Read API key from environment
    api_key = os.environ.get(ENV_KEY_NAME, "")
    if not api_key:
        print(f"✗ Environment variable {ENV_KEY_NAME!r} is not set.")
        print(f"  Export it before running:  export {ENV_KEY_NAME}=<your-key>")
        sys.exit(1)

    clip_folder = find_clip_folder(args.clip)
    print(f"[clip] {clip_folder.name}")
    print(f"[dir]  {clip_folder}")

    prompt = load_image_prompt(clip_folder)
    print(f"[prompt] {prompt[:120]}…" if len(prompt) > 120 else f"[prompt] {prompt}")

    generate_and_save(clip_folder, prompt, api_key)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Transform derived-data.json into the final question.json format for Firebase.

Removes internal fields (source_clip, visual_prompts, tts_script, pattern_used),
normalises metadata.level to uppercase, maps speaker IDs to Japanese labels,
and adds placeholder audio_url / image_url fields.

Usage:
    python3 build_question_json.py <path/to/derived-data.json>

Output:
    question.json written to the same directory as derived-data.json
"""

import json
import os
import sys

SPEAKER_MAP = {
    "Male_1": "男の人",
    "Female_1": "女の人",
}


def build_question(derived: dict) -> dict:
    return {
        "metadata": {
            "level": derived["metadata"]["level"].upper(),
            "topic": derived["metadata"]["topic"],
        },
        "audio_url": None,
        "image_url": None,
        "correct_option": derived["correct_option"],
        "transcription": {
            "intro": derived["transcription"]["intro"],
            "dialogue": [
                {
                    "speaker": SPEAKER_MAP.get(turn["speaker"], turn["speaker"]),
                    "text": turn["text"],
                }
                for turn in derived["transcription"]["dialogue"]
            ],
            "question": derived["transcription"]["question"],
        },
        "analysis": derived["analysis"],
        "logic": derived["logic"],
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: build_question_json.py <path/to/derived-data.json>")
        sys.exit(1)

    derived_path = sys.argv[1]
    out_path = os.path.join(os.path.dirname(os.path.abspath(derived_path)), "question.json")

    with open(derived_path, "r", encoding="utf-8") as f:
        derived = json.load(f)

    question = build_question(derived)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(question, f, ensure_ascii=False, indent=4)

    print(f"✓ question.json written: {out_path}")


if __name__ == "__main__":
    main()

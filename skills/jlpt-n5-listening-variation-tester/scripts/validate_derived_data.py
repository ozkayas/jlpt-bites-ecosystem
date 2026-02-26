#!/usr/bin/env python3
"""
Mechanical validator for derived-data.json files produced by jlpt-n5-listening-variation-creator.
Exit code 0 = all checks passed. Exit code 1 = one or more checks failed.
"""

import json
import sys
import argparse

VALID_PATTERNS = {"Reconsideration", "Shortage", "Attribute", "Negative", "Sequential", "Location"}
VALID_LOGIC_ROLES = {"Correct", "Distractor_A", "Distractor_B", "Distractor_C"}


def check(label, condition, detail=""):
    if condition:
        print(f"  ✓ {label}")
        return True
    else:
        msg = f"  ✗ {label}"
        if detail:
            msg += f": {detail}"
        print(msg)
        return False


def validate(data):
    results = []

    # source_clip
    results.append(check(
        "source_clip: present and non-empty",
        isinstance(data.get("source_clip"), str) and len(data["source_clip"]) > 0,
        f"got {data.get('source_clip')!r}"
    ))

    # metadata.level
    metadata = data.get("metadata", {})
    results.append(check(
        'metadata.level: "n5"',
        metadata.get("level") == "n5",
        f"got {metadata.get('level')!r}"
    ))

    # metadata.pattern_used
    results.append(check(
        f"metadata.pattern_used: one of {sorted(VALID_PATTERNS)}",
        metadata.get("pattern_used") in VALID_PATTERNS,
        f"got {metadata.get('pattern_used')!r}"
    ))

    # visual_prompts.image_prompt: present and non-empty string
    visual_prompts = data.get("visual_prompts", {})
    image_prompt = visual_prompts.get("image_prompt")
    results.append(check(
        "visual_prompts.image_prompt: present and non-empty string",
        isinstance(image_prompt, str) and len(image_prompt) > 0,
        f"got {image_prompt!r}"
    ))

    # visual_prompts.panel_map: exactly 4 items
    panel_map = visual_prompts.get("panel_map", [])
    results.append(check(
        "visual_prompts.panel_map: exactly 4 items",
        isinstance(panel_map, list) and len(panel_map) == 4,
        f"got {len(panel_map) if isinstance(panel_map, list) else type(panel_map).__name__} items"
    ))

    # logic_role distribution via panel_map: exactly 1 Correct + 3 Distractors
    if isinstance(panel_map, list):
        roles = [entry.get("logic_role") for entry in panel_map]
        correct_count = roles.count("Correct")
        dist_a = roles.count("Distractor_A")
        dist_b = roles.count("Distractor_B")
        dist_c = roles.count("Distractor_C")
        role_ok = (correct_count == 1 and dist_a == 1 and dist_b == 1 and dist_c == 1)
        results.append(check(
            "logic_role distribution: 1 Correct + 1 Distractor_A + 1 Distractor_B + 1 Distractor_C",
            role_ok,
            f"got {roles}"
        ))
    else:
        results.append(check("logic_role distribution", False, "panel_map is not a list"))

    # correct_option: integer 0-3
    correct_option = data.get("correct_option")
    results.append(check(
        "correct_option: integer 0-3",
        correct_option in (0, 1, 2, 3),
        f"got {correct_option!r}"
    ))

    # tts_script: all entries are valid (voice+text OR break only)
    tts = data.get("tts_script", [])
    tts_valid = True
    tts_error = ""
    if not isinstance(tts, list) or len(tts) == 0:
        tts_valid = False
        tts_error = "tts_script is empty or not a list"
    else:
        for i, entry in enumerate(tts):
            if not isinstance(entry, dict):
                tts_valid = False
                tts_error = f"entry {i} is not an object"
                break
            keys = set(entry.keys())
            is_voice_entry = keys == {"voice", "text"}
            is_break_entry = keys == {"break"}
            if not (is_voice_entry or is_break_entry):
                tts_valid = False
                tts_error = f"entry {i} has invalid keys: {keys} (must be {{voice,text}} or {{break}})"
                break
    results.append(check(
        "tts_script: all entries are valid {voice,text} or {break} objects",
        tts_valid,
        tts_error
    ))

    # transcription.dialogue: non-empty array
    transcription = data.get("transcription", {})
    dialogue = transcription.get("dialogue", [])
    results.append(check(
        "transcription.dialogue: non-empty array",
        isinstance(dialogue, list) and len(dialogue) > 0,
        f"got {len(dialogue) if isinstance(dialogue, list) else type(dialogue).__name__} items"
    ))

    # translations.tr: present
    translations = data.get("translations", {})
    results.append(check(
        "translations.tr: present",
        "tr" in translations and translations["tr"] is not None,
        "missing" if "tr" not in translations else ""
    ))

    # translations.en: present
    results.append(check(
        "translations.en: present",
        "en" in translations and translations["en"] is not None,
        "missing" if "en" not in translations else ""
    ))

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate derived-data.json")
    parser.add_argument("file", nargs="?", help="Path to derived-data.json")
    parser.add_argument("--stdin", action="store_true", help="Read JSON from stdin")
    args = parser.parse_args()

    if args.stdin:
        raw = sys.stdin.read()
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        print("Error: provide a file path or use --stdin")
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parse error: {e}")
        print("\nRESULT: FAIL — invalid JSON")
        sys.exit(1)

    print("Pass 1 — Mechanical Validation")
    results = validate(data)
    passed = sum(1 for r in results if r)
    total = len(results)

    if all(results):
        print(f"\nRESULT: PASS — {passed}/{total} checks passed")
        sys.exit(0)
    else:
        print(f"\nRESULT: FAIL — {passed}/{total} checks passed")
        sys.exit(1)


if __name__ == "__main__":
    main()

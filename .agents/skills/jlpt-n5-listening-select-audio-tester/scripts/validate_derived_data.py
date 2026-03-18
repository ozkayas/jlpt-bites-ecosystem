#!/usr/bin/env python3
"""
Mechanical validator for derived-data.json files produced by jlpt-n5-listening-select-audio-creator.
Checks schema, option count, correct_option range, transcriptions structure, and required fields.
Exit code 0 = all checks passed. Exit code 1 = one or more checks failed.

Usage:
  python3 validate_derived_data.py backend/listening/data/selectAudio/002/derived-data.json
  python3 validate_derived_data.py --stdin <<'EOF'
  {...json...}
  EOF
"""

import json
import sys
import argparse

REQUIRED_LANGS = {"ja", "tr", "en", "de", "fr", "es", "ko"}
TOPIC_LANGS = {"ja", "tr", "en", "de", "fr", "es", "ko"}


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

    # 1. source_clip: present and non-empty string
    results.append(check(
        "source_clip: present and non-empty",
        isinstance(data.get("source_clip"), str) and len(data["source_clip"]) > 0,
        f"got {data.get('source_clip')!r}"
    ))

    # 2. metadata.level: "N5"
    metadata = data.get("metadata", {})
    results.append(check(
        'metadata.level: "N5"',
        metadata.get("level") == "N5",
        f"got {metadata.get('level')!r}"
    ))

    # 3. metadata.topic: object with ja + all 6 UI lang keys
    topic = metadata.get("topic", {})
    topic_keys = set(topic.keys()) if isinstance(topic, dict) else set()
    results.append(check(
        f"metadata.topic: object with all keys {sorted(TOPIC_LANGS)}",
        isinstance(topic, dict) and TOPIC_LANGS.issubset(topic_keys),
        f"missing keys: {sorted(TOPIC_LANGS - topic_keys)}" if TOPIC_LANGS - topic_keys else ""
    ))

    # 4. correct_option: integer 0, 1, or 2
    correct_option = data.get("correct_option")
    results.append(check(
        "correct_option: integer 0, 1, or 2",
        correct_option in (0, 1, 2),
        f"got {correct_option!r}"
    ))

    # 5. transcriptions present with all 7 language keys
    transcriptions = data.get("transcriptions", {})
    trans_keys = set(transcriptions.keys()) if isinstance(transcriptions, dict) else set()
    results.append(check(
        f"transcriptions: all 7 lang keys present {sorted(REQUIRED_LANGS)}",
        isinstance(transcriptions, dict) and REQUIRED_LANGS.issubset(trans_keys),
        f"missing: {sorted(REQUIRED_LANGS - trans_keys)}" if REQUIRED_LANGS - trans_keys else ""
    ))

    # 6. transcriptions.ja.intro: present, >10 chars, ends with か。
    ja = transcriptions.get("ja", {}) if isinstance(transcriptions, dict) else {}
    intro = ja.get("intro", "")
    results.append(check(
        'transcriptions.ja.intro: present, >10 chars, ends with か。',
        isinstance(intro, str) and len(intro) > 10 and intro.rstrip().endswith("か。"),
        f"got {intro!r}"
    ))

    # 7. transcriptions.ja.options: exactly 3 items, each with number (1/2/3) and text
    options = ja.get("options", [])
    options_ok = (
        isinstance(options, list) and
        len(options) == 3 and
        all(
            isinstance(o, dict) and
            o.get("number") in (1, 2, 3) and
            isinstance(o.get("text"), str) and len(o["text"]) > 0
            for o in options
        )
    )
    results.append(check(
        "transcriptions.ja.options: exactly 3 items with number (1/2/3) and non-empty text",
        options_ok,
        f"got {len(options) if isinstance(options, list) else type(options).__name__} items"
    ))

    # 8. transcriptions.ja.question: present, >5 chars, ends with か。
    question = ja.get("question", "")
    results.append(check(
        'transcriptions.ja.question: present, >5 chars, ends with か。',
        isinstance(question, str) and len(question) > 5 and question.rstrip().endswith("か。"),
        f"got {question!r}"
    ))

    # 9. analysis.vocabulary: >=2 items, each with word, reading, meanings (object)
    analysis = data.get("analysis", {})
    vocabulary = analysis.get("vocabulary", [])
    vocab_ok = (
        isinstance(vocabulary, list) and
        len(vocabulary) >= 2 and
        all(
            isinstance(v, dict) and
            isinstance(v.get("word"), str) and len(v["word"]) > 0 and
            isinstance(v.get("reading"), str) and len(v["reading"]) > 0 and
            isinstance(v.get("meanings"), dict)
            for v in vocabulary
        )
    )
    results.append(check(
        "analysis.vocabulary: >=2 items, each with word, reading, meanings",
        vocab_ok,
        f"got {len(vocabulary) if isinstance(vocabulary, list) else type(vocabulary).__name__} items"
    ))

    # 10. image_prompt: present and non-empty string
    image_prompt = data.get("image_prompt", "")
    results.append(check(
        "image_prompt: present and non-empty string",
        isinstance(image_prompt, str) and len(image_prompt) > 0,
        f"got {image_prompt!r}"
    ))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate derived-data.json for jlpt-n5-listening-select-audio"
    )
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

    print("Pass 1 — Mechanical Validation (selectAudio)")
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

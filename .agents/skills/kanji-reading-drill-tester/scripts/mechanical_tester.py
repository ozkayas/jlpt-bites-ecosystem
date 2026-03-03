#!/usr/bin/env python3
"""
Mechanical validator for kanji_reading_drill.json (and kanji_selection_drill.json).

Usage:
    python3 mechanical_tester.py <path/to/kanji_reading_drill.json>

Exit code 0 = all checks passed, 1 = one or more errors found.
"""
import json
import re
import sys
import os

# CJK Unified Ideographs block — basic kanji range
KANJI_RE = re.compile(r'[\u4E00-\u9FFF]')
TAG_RE = re.compile(r'<t>(.*?)</t>', re.DOTALL)
ID_RE = re.compile(r'^\d{5}$')


def check_item(index, item, seen_ids):
    errors = []

    # ── Structure ────────────────────────────────────────────────────────────
    if not isinstance(item, list) or len(item) != 4:
        errors.append(f"Index {index}: item must be an array of exactly 4 elements (got {type(item).__name__} len={len(item) if isinstance(item, list) else '?'})")
        return errors  # can't continue without structure

    item_id, sentence, translations, options = item
    item_id = str(item_id)

    # ── ID ───────────────────────────────────────────────────────────────────
    if not ID_RE.match(item_id):
        errors.append(f"Index {index}: ID '{item_id}' must be a 5-digit zero-padded string (e.g. '00001')")
    if item_id in seen_ids:
        errors.append(f"Index {index}: duplicate ID '{item_id}'")
    seen_ids.add(item_id)

    # ── Sentence / <t> tag ───────────────────────────────────────────────────
    if not isinstance(sentence, str) or not sentence.strip():
        errors.append(f"ID {item_id}: sentence must be a non-empty string")
    else:
        tags = TAG_RE.findall(sentence)
        if len(tags) != 1:
            errors.append(f"ID {item_id}: sentence must contain exactly one <t>…</t> tag (found {len(tags)})")
        else:
            tagged = tags[0]
            if not KANJI_RE.search(tagged):
                errors.append(f"ID {item_id}: text inside <t>…</t> ('{tagged}') must contain at least one kanji character")

    # ── Options ──────────────────────────────────────────────────────────────
    if not isinstance(options, list) or len(options) < 2:
        errors.append(f"ID {item_id}: options must be an array with at least 2 items")
    else:
        if len(options) > 4:
            errors.append(f"ID {item_id}: options has {len(options)} items (max 4; app grid shows exactly 4)")

        correct = str(options[0]).strip()
        if not correct:
            errors.append(f"ID {item_id}: options[0] (correct answer) must not be empty")

        distractors = [str(o).strip() for o in options[1:]]
        if correct in distractors:
            errors.append(f"ID {item_id}: correct answer '{correct}' must not appear in distractors {distractors}")

        all_opts = [correct] + distractors
        if len(all_opts) != len(set(all_opts)):
            errors.append(f"ID {item_id}: options contain duplicates: {all_opts}")

        for i, opt in enumerate(all_opts):
            if not opt:
                errors.append(f"ID {item_id}: options[{i}] is empty")

    # ── Translations ─────────────────────────────────────────────────────────
    if not isinstance(translations, dict):
        errors.append(f"ID {item_id}: translations must be a dict")
    else:
        for lang in ('tr', 'en'):
            if lang not in translations:
                errors.append(f"ID {item_id}: translations missing required key '{lang}'")
            elif not str(translations[lang]).strip():
                errors.append(f"ID {item_id}: translations['{lang}'] is empty")

    return errors


def check_id_sequence(items):
    """Warn if IDs are not consecutive starting from 00001."""
    warnings = []
    for i, item in enumerate(items):
        if not isinstance(item, list) or not item:
            continue
        expected = f"{i + 1:05d}"
        actual = str(item[0])
        if actual != expected:
            warnings.append(f"Index {i}: expected ID '{expected}', got '{actual}' (sequence broken)")
    return warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mechanical_tester.py <path/to/kanji_reading_drill.json>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Error: file not found: {path}")
        sys.exit(1)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}")
        sys.exit(1)

    # ── Root structure ────────────────────────────────────────────────────────
    root_errors = []
    if not isinstance(data, dict):
        root_errors.append("Root must be a JSON object")
    else:
        if data.get('v') != 1:
            root_errors.append(f"Root 'v' must equal 1 (got {data.get('v')!r})")
        if 'items' not in data or not isinstance(data['items'], list):
            root_errors.append("Root must have an 'items' array")
        elif len(data['items']) == 0:
            root_errors.append("'items' array is empty")

    if root_errors:
        for e in root_errors:
            print(f"❌ {e}")
        sys.exit(1)

    items = data['items']
    all_errors = []
    seen_ids = set()

    for i, item in enumerate(items):
        all_errors.extend(check_item(i, item, seen_ids))

    seq_warnings = check_id_sequence(items)

    # ── Report ────────────────────────────────────────────────────────────────
    if seq_warnings:
        print(f"\n⚠️  ID sequence warnings ({len(seq_warnings)}):")
        for w in seq_warnings:
            print(f"  {w}")

    if all_errors:
        print(f"\n❌ Mechanical validation FAILED — {len(all_errors)} error(s) in {len(items)} items:\n")
        for e in all_errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"✅ Mechanical validation PASSED — {len(items)} items, no errors.")
        if seq_warnings:
            print(f"   ({len(seq_warnings)} ID sequence warning(s) above — review if intentional)")


if __name__ == '__main__':
    main()

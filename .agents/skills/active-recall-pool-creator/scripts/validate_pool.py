#!/usr/bin/env python3
"""
Validate active_recall_pool.json for structural correctness and quality.

Usage:
    python3 validate_pool.py <pool_json_path> [--vocab-source <n5_vocabulary.json>]

Checks:
  1. JSON structure and required fields
  2. Checkpoint ID format and sequentiality (every multiple of 5, no gaps)
  3. Sentence ID format and uniqueness
  4. All 6 language keys present in prompts and grammar_hints
  5. No empty values
  6. grammar_hints quality (rejects category-label-only hints)
  7. Vocabulary scope (if --vocab-source provided)
"""

import json
import sys
import argparse
import re
from pathlib import Path

REQUIRED_LANGS = {"tr", "en", "de", "es", "fr", "ko"}

# Patterns that indicate a hint is just a category label (too short/generic)
CATEGORY_LABEL_PATTERNS = [
    r"^(asking|greeting|counting|introducing|polite|daily|basic)\b",
    r"^(yer|nesne|isim|sayı|zaman|selaml|tanı[şs]|temel|nazik|resmi|günlük)\b",
    r"^(fragen|begrüßung|grundzahlen|höfliche|tägliche)\b",
    r"^(preguntar|saludo|números|presentación|cortés)\b",
    r"^(demander|salutation|nombres|présentation|poli)\b",
    r"^(묻기|인사|숫자|소개|정중)\b",
]


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_category_label(hint: str) -> bool:
    """Check if a hint looks like a useless category label rather than a real hint."""
    hint_lower = hint.strip().rstrip(".").lower()
    # Too short to be useful (under 20 chars is likely just a label)
    if len(hint_lower) < 20:
        return True
    # Matches known category label patterns
    for pattern in CATEGORY_LABEL_PATTERNS:
        if re.search(pattern, hint_lower, re.IGNORECASE):
            # But only if it's still short (a longer hint starting with these words might be fine)
            if len(hint_lower) < 40:
                return True
    return False


def validate_structure(pool: dict, errors: list, warnings: list):
    """Validate JSON structure and required fields."""
    if "checkpoints" not in pool:
        errors.append("Root object missing 'checkpoints' key")
        return

    checkpoints = pool["checkpoints"]
    if not isinstance(checkpoints, list):
        errors.append("'checkpoints' must be an array")
        return

    if len(checkpoints) == 0:
        errors.append("'checkpoints' array is empty")
        return

    seen_ids = set()
    seen_sentence_ids = set()
    learned_counts = []

    for i, cp in enumerate(checkpoints):
        prefix = f"checkpoints[{i}]"

        # Required fields
        for field in ("id", "learned_word_count", "sentences"):
            if field not in cp:
                errors.append(f"{prefix}: missing required field '{field}'")

        if "id" not in cp:
            continue

        cp_id = cp["id"]

        # ID format
        if not re.match(r"^cp_\d+$", cp_id):
            errors.append(f"{prefix}: id '{cp_id}' does not match format 'cp_N'")

        # Duplicate ID
        if cp_id in seen_ids:
            errors.append(f"{prefix}: duplicate checkpoint id '{cp_id}'")
        seen_ids.add(cp_id)

        # learned_word_count
        lwc = cp.get("learned_word_count")
        if isinstance(lwc, int):
            if lwc % 5 != 0:
                errors.append(f"{prefix} ({cp_id}): learned_word_count {lwc} is not a multiple of 5")
            if lwc <= 0:
                errors.append(f"{prefix} ({cp_id}): learned_word_count must be positive")
            expected_id = f"cp_{lwc}"
            if cp_id != expected_id:
                errors.append(f"{prefix}: id '{cp_id}' does not match learned_word_count {lwc} (expected '{expected_id}')")
            learned_counts.append(lwc)

        # Sentences
        sentences = cp.get("sentences", [])
        if not isinstance(sentences, list):
            errors.append(f"{prefix} ({cp_id}): 'sentences' must be an array")
            continue

        if len(sentences) < 2:
            warnings.append(f"{prefix} ({cp_id}): only {len(sentences)} sentence(s), recommended minimum is 2")

        for j, sent in enumerate(sentences):
            s_prefix = f"{prefix}.sentences[{j}]"
            validate_sentence(sent, s_prefix, cp_id, lwc, seen_sentence_ids, errors, warnings)

    # Check sequentiality
    if learned_counts:
        learned_counts_sorted = sorted(learned_counts)
        expected = list(range(5, learned_counts_sorted[-1] + 1, 5))
        missing = set(expected) - set(learned_counts_sorted)
        if missing:
            warnings.append(f"Missing checkpoints for learned_word_count: {sorted(missing)}")


def validate_sentence(sent, prefix, cp_id, lwc, seen_ids, errors, warnings):
    """Validate a single sentence object."""
    for field in ("id", "prompts", "japanese_target", "grammar_hints"):
        if field not in sent:
            errors.append(f"{prefix}: missing required field '{field}'")

    if "id" not in sent:
        return

    sid = sent["id"]

    # ID format: cpN_sM
    if not re.match(r"^cp\d+_s\d+$", sid):
        errors.append(f"{prefix}: sentence id '{sid}' does not match format 'cpN_sM'")

    if sid in seen_ids:
        errors.append(f"{prefix}: duplicate sentence id '{sid}'")
    seen_ids.add(sid)

    # Prompts — all 6 languages
    prompts = sent.get("prompts", {})
    if isinstance(prompts, dict):
        missing_langs = REQUIRED_LANGS - set(prompts.keys())
        if missing_langs:
            errors.append(f"{prefix} ({sid}): prompts missing languages: {sorted(missing_langs)}")
        for lang, val in prompts.items():
            if not val or not val.strip():
                errors.append(f"{prefix} ({sid}): prompts['{lang}'] is empty")

    # Grammar hints — all 6 languages + quality check
    hints = sent.get("grammar_hints", {})
    if isinstance(hints, dict):
        missing_langs = REQUIRED_LANGS - set(hints.keys())
        if missing_langs:
            errors.append(f"{prefix} ({sid}): grammar_hints missing languages: {sorted(missing_langs)}")
        for lang, val in hints.items():
            if not val or not val.strip():
                errors.append(f"{prefix} ({sid}): grammar_hints['{lang}'] is empty")
            elif is_category_label(val):
                errors.append(
                    f"{prefix} ({sid}): grammar_hints['{lang}'] looks like a category label, "
                    f"not a real hint: \"{val}\". Hints must contain vocabulary mappings, "
                    f"grammar patterns, or structural clues."
                )

    # japanese_target not empty
    jt = sent.get("japanese_target", "")
    if not jt or not jt.strip():
        errors.append(f"{prefix} ({sid}): japanese_target is empty")


def validate_vocab_scope(pool: dict, vocab_path: str, errors: list, warnings: list):
    """Check that each checkpoint only uses vocabulary within its scope."""
    vocab_data = load_json(vocab_path)
    words = vocab_data.get("words", [])

    if not words:
        warnings.append(f"Vocabulary source has no words, skipping scope check")
        return

    for cp in pool.get("checkpoints", []):
        lwc = cp.get("learned_word_count", 0)
        cp_id = cp.get("id", "?")

        # Build allowed vocabulary set from first lwc words
        allowed_words = set()
        allowed_readings = set()
        for w in words[:lwc]:
            allowed_words.add(w.get("word", ""))
            allowed_readings.add(w.get("reading", ""))

        for sent in cp.get("sentences", []):
            sid = sent.get("id", "?")
            jt = sent.get("japanese_target", "")

            # Extract potential kanji words (sequences of kanji characters)
            kanji_words = re.findall(r"[\u4e00-\u9fff]+", jt)
            for kw in kanji_words:
                if kw not in allowed_words:
                    # Check if it's part of a longer word
                    found = any(kw in w for w in allowed_words)
                    if not found:
                        errors.append(
                            f"{cp_id}/{sid}: kanji '{kw}' in japanese_target not found "
                            f"in first {lwc} vocabulary words"
                        )


def main():
    parser = argparse.ArgumentParser(description="Validate active_recall_pool.json")
    parser.add_argument("pool_path", help="Path to active_recall_pool.json")
    parser.add_argument("--vocab-source", help="Path to n5_vocabulary.json for scope checking")
    args = parser.parse_args()

    pool_path = Path(args.pool_path)
    if not pool_path.exists():
        print(f"ERROR: File not found: {pool_path}")
        sys.exit(1)

    try:
        pool = load_json(str(pool_path))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        sys.exit(1)

    errors = []
    warnings = []

    validate_structure(pool, errors, warnings)

    if args.vocab_source:
        vocab_path = Path(args.vocab_source)
        if vocab_path.exists():
            validate_vocab_scope(pool, str(vocab_path), errors, warnings)
        else:
            warnings.append(f"Vocabulary source not found: {vocab_path}, skipping scope check")

    # Report
    total_checkpoints = len(pool.get("checkpoints", []))
    total_sentences = sum(len(cp.get("sentences", [])) for cp in pool.get("checkpoints", []))

    print(f"\n{'='*60}")
    print(f"Active Recall Pool Validation Report")
    print(f"{'='*60}")
    print(f"Checkpoints: {total_checkpoints}")
    print(f"Total sentences: {total_sentences}")
    print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
        print()

    if not errors and not warnings:
        print("✓ All checks passed!")

    if errors:
        print(f"\nResult: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        sys.exit(1)
    else:
        print(f"\nResult: PASS ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()

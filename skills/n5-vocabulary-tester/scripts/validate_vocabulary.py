#!/usr/bin/env python3
"""
Mechanical validator for JLPT N5 vocabulary JSON (n5_vocabulary.json).

Usage:
    python3 validate_vocabulary.py <path/to/n5_vocabulary.json>

Exit codes:
    0 — No errors (warnings may exist)
    1 — One or more errors found
"""

import json
import sys
import re
from collections import Counter
from pathlib import Path


REQUIRED_WORD_FIELDS = {"id", "word", "reading", "romaji", "tag", "translations", "sentences"}
VALID_TAGS = {"動詞", "名詞", "形容詞", "副詞", "表現"}
REQUIRED_TRANSLATION_LANGS = {"en", "tr", "de", "es", "fr"}
REQUIRED_SENTENCE_FIELDS = {"ja", "furigana", "romaji", "translations"}
REQUIRED_SENTENCE_TRANS_LANGS = {"en", "tr"}
ID_PATTERN = re.compile(r"^n5_vocab_\d{3,}$")

# Heuristic: detect English translations mistakenly placed in the romaji field.
# If the text contains common English-only words AND lacks Japanese romaji markers
# (desu, masu, wa, ga, ni, wo, ka) it's likely an English sentence, not romaji.
ENGLISH_SIGNAL = re.compile(
    r"\b(the|want|going|birthday|beautiful|people|second|trip|shirt|wearing|like this)\b",
    re.IGNORECASE,
)
ROMAJI_MARKER = re.compile(
    r"\b(desu|masu|dewa|imasu|arimasu|shimasu|taberu|iku|kuru|wa|ga|ni|wo|ka|san|kun|chan|suru|nai|naru)\b",
    re.IGNORECASE,
)


def validate(path: str):
    errors = []
    warnings = []

    # ── Load JSON ──────────────────────────────────────────────────────────
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        sys.exit(1)

    # ── Root structure ─────────────────────────────────────────────────────
    if not isinstance(data, dict) or "words" not in data:
        errors.append("Root must be an object with a 'words' array")
        report(errors, warnings)
        return

    words = data["words"]
    if not isinstance(words, list):
        errors.append("'words' must be an array")
        report(errors, warnings)
        return

    # ── Per-word checks ────────────────────────────────────────────────────
    ids_seen = []

    for i, word in enumerate(words):
        loc = f"words[{i}]"
        if not isinstance(word, dict):
            errors.append(f"{loc}: entry is not an object")
            continue

        word_id = word.get("id", f"<missing id at index {i}>")
        loc = word_id

        # Required fields
        missing = REQUIRED_WORD_FIELDS - set(word.keys())
        for field in sorted(missing):
            errors.append(f"{loc}: missing required field '{field}'")

        # id format
        if "id" in word:
            if not ID_PATTERN.match(word["id"]):
                errors.append(f"{loc}: id format invalid (expected n5_vocab_NNN): '{word['id']}'")
            ids_seen.append(word["id"])

        # audioUrl: track count for summary warning at end
        if "audioUrl" not in word:
            pass  # counted below

        # tag
        tag = word.get("tag")
        if tag is not None and tag not in VALID_TAGS:
            errors.append(f"{loc}: invalid tag '{tag}' (must be one of: {', '.join(sorted(VALID_TAGS))})")

        # translations
        trans = word.get("translations")
        if trans is not None:
            if not isinstance(trans, dict):
                errors.append(f"{loc}: 'translations' must be an object")
            else:
                missing_langs = REQUIRED_TRANSLATION_LANGS - set(trans.keys())
                for lang in sorted(missing_langs):
                    errors.append(f"{loc}: translations missing language '{lang}'")
                for lang, val in trans.items():
                    if lang in REQUIRED_TRANSLATION_LANGS and not val:
                        errors.append(f"{loc}: translations.{lang} is empty")

        # sentences
        sentences = word.get("sentences")
        if sentences is not None:
            if not isinstance(sentences, list) or len(sentences) == 0:
                errors.append(f"{loc}: 'sentences' must be a non-empty array")
            else:
                for j, sent in enumerate(sentences):
                    sloc = f"{loc} sentence[{j}]"
                    if not isinstance(sent, dict):
                        errors.append(f"{sloc}: not an object")
                        continue

                    # Required sentence fields
                    missing_sf = REQUIRED_SENTENCE_FIELDS - set(sent.keys())
                    for field in sorted(missing_sf):
                        errors.append(f"{sloc}: missing field '{field}'")

                    # furigana tag balance
                    furi = sent.get("furigana", "")
                    if furi:
                        ruby_open  = furi.count("<ruby>")
                        ruby_close = furi.count("</ruby>")
                        rt_open    = furi.count("<rt>")
                        rt_close   = furi.count("</rt>")
                        if ruby_open != ruby_close:
                            errors.append(f"{sloc}: unbalanced <ruby> tags ({ruby_open} open, {ruby_close} close)")
                        if rt_open != rt_close:
                            errors.append(f"{sloc}: unbalanced <rt> tags ({rt_open} open, {rt_close} close)")

                    # romaji should not be English text
                    romaji = sent.get("romaji", "")
                    if romaji and ENGLISH_SIGNAL.search(romaji) and not ROMAJI_MARKER.search(romaji):
                        errors.append(
                            f"{sloc}: 'romaji' looks like an English translation, not romanized Japanese: \"{romaji}\""
                        )

                    # sentence translations
                    strans = sent.get("translations")
                    if strans is not None:
                        if not isinstance(strans, dict):
                            errors.append(f"{sloc}: 'translations' must be an object")
                        else:
                            missing_sl = REQUIRED_SENTENCE_TRANS_LANGS - set(strans.keys())
                            for lang in sorted(missing_sl):
                                errors.append(f"{sloc}: translations missing language '{lang}'")
                            for lang in REQUIRED_SENTENCE_TRANS_LANGS:
                                if lang in strans and not strans[lang]:
                                    errors.append(f"{sloc}: translations.{lang} is empty")

    # ── ID uniqueness ──────────────────────────────────────────────────────
    dup_ids = [id_ for id_, count in Counter(ids_seen).items() if count > 1]
    for dup in dup_ids:
        errors.append(f"Duplicate id: '{dup}'")

    # ── audioUrl summary warning ───────────────────────────────────────────
    no_audio_count = sum(1 for w in words if "audioUrl" not in w)
    if no_audio_count:
        warnings.append(f"{no_audio_count}/{len(words)} words missing 'audioUrl' field (audio not yet generated)")

    # ── ID sequence gaps (warnings) ────────────────────────────────────────
    nums = []
    for id_ in ids_seen:
        match = re.search(r"(\d+)$", id_)
        if match:
            nums.append(int(match.group(1)))
    nums.sort()
    if nums:
        expected = set(range(nums[0], nums[-1] + 1))
        gaps = sorted(expected - set(nums))
        if gaps:
            warnings.append(f"ID sequence gaps (non-consecutive): {gaps}")

    report(errors, warnings, total=len(words))


def report(errors, warnings, total=None):
    print()
    if total is not None:
        print(f"Checked {total} words.")
    print()

    if warnings:
        print(f"⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"   {w}")
        print()

    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"   {e}")
        print()
        print("Pass 1 FAILED — fix errors before semantic review.")
        sys.exit(1)
    else:
        print("✅ Pass 1 PASSED — no errors found.")
        if warnings:
            print("   Review warnings above before proceeding to Pass 2.")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <path/to/n5_vocabulary.json>")
        sys.exit(1)
    validate(sys.argv[1])

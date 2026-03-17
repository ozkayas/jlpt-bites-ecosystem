#!/usr/bin/env python3
"""
Mechanical validator for selectText question_data.json files.

Usage:
  python3 validate_question_data.py <path_to_question_data.json>
  python3 validate_question_data.py --batch <selectText_directory>

Exit code 0 = all checks pass, 1 = at least one failure.
"""
import json
import sys
import os
import glob
import re

# --- Allowed speaker labels ---
ALLOWED_SPEAKERS = {
    "おとこのひと", "おんなのひと",
    "おとこのがくせい", "おんなのがくせい",
    "せんせい", "がくせい",
    "てんいん", "おみせのひと",
    "いしゃ",
    "男の人", "女の人",
}

# --- N5 question word patterns (must appear in intro) ---
QUESTION_PATTERNS = [
    r"なにを", r"なにが", r"どこで", r"どこへ", r"いつ", r"なんじ",
    r"どうして", r"どうやって", r"なんにん", r"いくら", r"なんまい",
    r"どれ", r"どの", r"どちら", r"どんな",
]


def validate(filepath: str) -> list[str]:
    """Validate a single question_data.json. Returns list of error strings."""
    errors = []

    # --- Load JSON ---
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"FATAL: Invalid JSON — {e}"]
    except FileNotFoundError:
        return [f"FATAL: File not found — {filepath}"]

    # --- Check 1: metadata ---
    meta = data.get("metadata")
    if not isinstance(meta, dict):
        errors.append("CHECK 1 FAIL: 'metadata' missing or not an object")
    else:
        if meta.get("level") != "N5":
            errors.append(f"CHECK 1 FAIL: metadata.level must be 'N5', got '{meta.get('level')}'")
        if not meta.get("topic") or not isinstance(meta.get("topic"), str):
            errors.append("CHECK 1 FAIL: metadata.topic missing or empty")
        # audio_url can be null or a string
        if "audio_url" not in meta:
            errors.append("CHECK 1 FAIL: metadata.audio_url field missing")

    # --- Check 2: options ---
    options = data.get("options")
    if not isinstance(options, list) or len(options) != 4:
        errors.append(f"CHECK 2 FAIL: 'options' must be array of exactly 4 items, got {type(options).__name__} len={len(options) if isinstance(options, list) else 'N/A'}")
    else:
        for i, opt in enumerate(options):
            if not isinstance(opt, str) or len(opt.strip()) == 0:
                errors.append(f"CHECK 2 FAIL: options[{i}] is empty or not a string")

    # --- Check 3: correct_option ---
    correct = data.get("correct_option")
    if not isinstance(correct, int) or correct < 0 or correct > 3:
        errors.append(f"CHECK 3 FAIL: correct_option must be int 0-3, got '{correct}'")

    # --- Check 4: transcription ---
    trans = data.get("transcription")
    if not isinstance(trans, dict):
        errors.append("CHECK 4 FAIL: 'transcription' missing or not an object")
    else:
        # intro
        intro = trans.get("intro", "")
        if not isinstance(intro, str) or len(intro.strip()) < 10:
            errors.append("CHECK 4 FAIL: transcription.intro missing or too short (< 10 chars)")

        # question
        question = trans.get("question", "")
        if not isinstance(question, str) or len(question.strip()) < 5:
            errors.append("CHECK 4 FAIL: transcription.question missing or too short")

        # question should end with か。
        if question and not question.strip().endswith("か。"):
            errors.append(f"CHECK 4 WARN: transcription.question should end with 'か。', got '{question[-5:]}'")

        # dialogue
        dialogue = trans.get("dialogue")
        if not isinstance(dialogue, list) or len(dialogue) < 2:
            errors.append(f"CHECK 4 FAIL: transcription.dialogue must have >= 2 turns, got {len(dialogue) if isinstance(dialogue, list) else 0}")
        elif len(dialogue) > 10:
            errors.append(f"CHECK 4 WARN: transcription.dialogue has {len(dialogue)} turns (expected 4-7)")
        else:
            for j, turn in enumerate(dialogue):
                if not isinstance(turn, dict):
                    errors.append(f"CHECK 4 FAIL: dialogue[{j}] is not an object")
                    continue
                speaker = turn.get("speaker", "")
                text = turn.get("text", "")
                if speaker not in ALLOWED_SPEAKERS:
                    errors.append(f"CHECK 4 WARN: dialogue[{j}].speaker '{speaker}' not in allowed list")
                if not isinstance(text, str) or len(text.strip()) == 0:
                    errors.append(f"CHECK 4 FAIL: dialogue[{j}].text is empty")

    # --- Check 5: analysis ---
    analysis = data.get("analysis")
    if not isinstance(analysis, dict):
        errors.append("CHECK 5 FAIL: 'analysis' missing or not an object")
    else:
        # vocabulary
        vocab = analysis.get("vocabulary")
        if not isinstance(vocab, list) or len(vocab) < 2:
            errors.append(f"CHECK 5 FAIL: analysis.vocabulary must have >= 2 items, got {len(vocab) if isinstance(vocab, list) else 0}")
        else:
            for k, v in enumerate(vocab):
                if not isinstance(v, dict):
                    errors.append(f"CHECK 5 FAIL: vocabulary[{k}] is not an object")
                    continue
                for field in ["word", "tr", "en"]:
                    if not v.get(field):
                        errors.append(f"CHECK 5 FAIL: vocabulary[{k}].{field} missing or empty")

        # grammar
        grammar = analysis.get("grammar")
        if not isinstance(grammar, list) or len(grammar) < 1:
            errors.append(f"CHECK 5 FAIL: analysis.grammar must have >= 1 item, got {len(grammar) if isinstance(grammar, list) else 0}")
        else:
            for k, g in enumerate(grammar):
                if not isinstance(g, dict):
                    errors.append(f"CHECK 5 FAIL: grammar[{k}] is not an object")
                    continue
                for field in ["point", "tr", "en"]:
                    if not g.get(field):
                        errors.append(f"CHECK 5 FAIL: grammar[{k}].{field} missing or empty")

    # --- Check 6: logic ---
    logic = data.get("logic")
    if not isinstance(logic, dict):
        errors.append("CHECK 6 FAIL: 'logic' missing or not an object")
    else:
        for lang in ["tr", "en"]:
            val = logic.get(lang, "")
            if not isinstance(val, str) or len(val.strip()) < 20:
                errors.append(f"CHECK 6 FAIL: logic.{lang} missing or too short (< 20 chars)")

    # --- Check 7: correct_option matches an option ---
    if isinstance(correct, int) and 0 <= correct <= 3 and isinstance(options, list) and len(options) == 4:
        correct_text = options[correct]
        if not correct_text or not isinstance(correct_text, str):
            errors.append(f"CHECK 7 FAIL: options[correct_option={correct}] is empty")

    # --- Check 8: No duplicate options ---
    if isinstance(options, list) and len(options) == 4:
        unique = set(opt.strip() for opt in options if isinstance(opt, str))
        if len(unique) < 4:
            errors.append(f"CHECK 8 FAIL: Duplicate options found ({4 - len(unique)} duplicates)")

    # --- Check 9: intro contains a question pattern ---
    if isinstance(trans, dict):
        intro = trans.get("intro", "")
        has_question = any(re.search(p, intro) for p in QUESTION_PATTERNS)
        if not has_question:
            errors.append("CHECK 9 WARN: intro does not contain a recognizable question word (なにを, どこ, いつ, etc.)")

    # --- Check 10: No kanji in options (N5 text should be mostly hiragana/katakana) ---
    if isinstance(options, list):
        kanji_pattern = re.compile(r'[\u4e00-\u9fff]')
        for i, opt in enumerate(options):
            if isinstance(opt, str) and kanji_pattern.search(opt):
                kanji_found = kanji_pattern.findall(opt)
                errors.append(f"CHECK 10 WARN: options[{i}] contains kanji: {''.join(kanji_found)} — N5 selectText options should prefer hiragana/katakana")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_question_data.py <file.json>")
        print("       python3 validate_question_data.py --batch <selectText_dir>")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Usage: python3 validate_question_data.py --batch <selectText_dir>")
            sys.exit(1)
        base_dir = sys.argv[2]
        files = sorted(glob.glob(os.path.join(base_dir, "[0-9][0-9][0-9]", "question_data.json")))
        if not files:
            print(f"No question_data.json files found in {base_dir}/*/")
            sys.exit(1)

        total_errors = 0
        total_warnings = 0
        total_files = len(files)
        failed_files = []

        for fp in files:
            folder = os.path.basename(os.path.dirname(fp))
            errs = validate(fp)
            fails = [e for e in errs if "FAIL" in e]
            warns = [e for e in errs if "WARN" in e]
            total_errors += len(fails)
            total_warnings += len(warns)

            if fails:
                failed_files.append(folder)
                print(f"\n❌ {folder}/question_data.json — {len(fails)} error(s), {len(warns)} warning(s)")
                for e in errs:
                    print(f"   {e}")
            elif warns:
                print(f"⚠️  {folder}/question_data.json — {len(warns)} warning(s)")
                for w in warns:
                    print(f"   {w}")
            else:
                print(f"✅ {folder}/question_data.json — OK")

        print(f"\n{'='*50}")
        print(f"Total: {total_files} files, {total_errors} errors, {total_warnings} warnings")
        if failed_files:
            print(f"Failed: {', '.join(failed_files)}")
            sys.exit(1)
        else:
            print("All files passed mechanical validation.")
            sys.exit(0)
    else:
        filepath = sys.argv[1]
        errs = validate(filepath)
        if not errs:
            print(f"✅ PASS — {filepath}")
            sys.exit(0)
        else:
            fails = [e for e in errs if "FAIL" in e]
            warns = [e for e in errs if "WARN" in e]
            print(f"{'❌ FAIL' if fails else '⚠️  WARN'} — {filepath}")
            for e in errs:
                print(f"  {e}")
            sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

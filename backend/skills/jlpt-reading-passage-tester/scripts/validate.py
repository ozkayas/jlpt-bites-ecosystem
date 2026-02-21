#!/usr/bin/env python3
"""
JLPT N5 Reading Passage Validator
Validates core passage JSON for jlpt-n5-reading-passage-creator.

Usage:
    python3 validate.py <path-to-json-file>
    python3 validate.py --stdin
"""

import json
import re
import sys

ID_RE = re.compile(r"^n5_reading_(short|mid)_\d{3}$")
VALID_VISUAL_TYPES = {"letter", "notice", "memo", "email", "none"}
VALID_TYPES = {"short", "mid"}


def validate_sentence(s, idx_label):
    errors = []
    if not isinstance(s.get("id"), str) or not s["id"].strip():
        errors.append(f"{idx_label}.id: must be a non-empty string")
    if not isinstance(s.get("original"), str) or not s["original"].strip():
        errors.append(f"{idx_label}.original: must be a non-empty string")
    if not isinstance(s.get("furigana"), str) or not s["furigana"].strip():
        errors.append(f"{idx_label}.furigana: must be a non-empty string")
    if not isinstance(s.get("romaji"), str) or not s["romaji"].strip():
        errors.append(f"{idx_label}.romaji: must be a non-empty string")
    return errors


def validate_question(q, idx_label):
    errors = []
    if not isinstance(q.get("id"), str) or not q["id"].strip():
        errors.append(f"{idx_label}.id: must be a non-empty string")
    if not isinstance(q.get("text"), str) or not q["text"].strip():
        errors.append(f"{idx_label}.text: must be a non-empty string")

    options = q.get("options", [])
    if not isinstance(options, list) or len(options) != 4:
        errors.append(
            f"{idx_label}.options: must be an array of exactly 4, got "
            f"{len(options) if isinstance(options, list) else type(options).__name__}"
        )
    else:
        correct_count = 0
        for i, opt in enumerate(options):
            opt_label = f"{idx_label}.options[{i}]"
            if not isinstance(opt.get("id"), str) or not opt["id"].strip():
                errors.append(f"{opt_label}.id: must be a non-empty string")
            if not isinstance(opt.get("text"), str) or not opt["text"].strip():
                errors.append(f"{opt_label}.text: must be a non-empty string")
            if opt.get("is_correct") is True:
                correct_count += 1

        if correct_count != 1:
            errors.append(
                f"{idx_label}.options: exactly 1 option must have is_correct=true, found {correct_count}"
            )

    return errors


def validate_passage(p, index):
    errors = []
    idx = f"passages[{index}]"

    # id
    pid = p.get("id", "")
    if not ID_RE.match(pid):
        errors.append(f"{idx}.id: '{pid}' does not match n5_reading_(short|mid)_NNN")

    # type
    ptype = p.get("type")
    if ptype not in VALID_TYPES:
        errors.append(f"{idx}.type: expected 'short' or 'mid', got {ptype!r}")

    # visual_type
    vt = p.get("visual_type")
    if vt not in VALID_VISUAL_TYPES:
        errors.append(f"{idx}.visual_type: expected one of {sorted(VALID_VISUAL_TYPES)}, got {vt!r}")

    # title
    if not isinstance(p.get("title"), str) or not p["title"].strip():
        errors.append(f"{idx}.title: must be a non-empty string")

    # sentences — at least 1 required
    sentences = p.get("sentences", [])
    if not isinstance(sentences, list) or len(sentences) == 0:
        errors.append(f"{idx}.sentences: must be a non-empty array")
    else:
        for i, s in enumerate(sentences):
            errors.extend(validate_sentence(s, f"{idx}.sentences[{i}]"))

    # framed_sentences — can be empty, but must be array
    framed = p.get("framed_sentences", [])
    if not isinstance(framed, list):
        errors.append(f"{idx}.framed_sentences: must be an array (can be empty)")
    else:
        for i, s in enumerate(framed):
            errors.extend(validate_sentence(s, f"{idx}.framed_sentences[{i}]"))

    # questions — at least 1 required
    questions = p.get("questions", [])
    if not isinstance(questions, list) or len(questions) == 0:
        errors.append(f"{idx}.questions: must be a non-empty array")
    else:
        for i, q in enumerate(questions):
            errors.extend(validate_question(q, f"{idx}.questions[{i}]"))

    # question_count consistency
    qc = p.get("question_count")
    if isinstance(questions, list) and isinstance(qc, int) and qc != len(questions):
        errors.append(
            f"{idx}.question_count: declared {qc} but found {len(questions)} questions"
        )

    return errors


def validate(data):
    results = {"passed": 0, "failed": 0, "passages": []}

    if not isinstance(data, dict) or "passages" not in data:
        return None, ["Top-level JSON must be an object with a 'passages' array"]

    passages = data["passages"]
    if not isinstance(passages, list) or len(passages) == 0:
        return None, ["'passages' must be a non-empty array"]

    for i, p in enumerate(passages):
        errs = validate_passage(p, i)
        pid = p.get("id", f"<no id, index {i}>")
        status = "PASS" if not errs else "FAIL"
        results["passages"].append({"id": pid, "status": status, "errors": errs})
        if errs:
            results["failed"] += 1
        else:
            results["passed"] += 1

    return results, []


def print_report(results):
    total = results["passed"] + results["failed"]
    print(f"\n{'='*60}")
    print("JLPT N5 Reading Passage Tester — Results")
    print(f"{'='*60}")
    print(f"Total : {total}  |  PASS: {results['passed']}  |  FAIL: {results['failed']}")
    print(f"{'='*60}\n")

    for p in results["passages"]:
        mark = "✅" if p["status"] == "PASS" else "❌"
        print(f"{mark}  {p['id']}")
        for err in p["errors"]:
            print(f"     └─ {err}")

    print()
    if results["failed"] == 0:
        print("All passages passed validation.")
    else:
        print(f"{results['failed']} passage(s) failed. See errors above.")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: validate.py <file.json>  |  validate.py --stdin")
        sys.exit(1)

    if sys.argv[1] == "--stdin":
        raw = sys.stdin.read()
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            raw = f.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)

    results, errors = validate(data)
    if results is None:
        for e in errors:
            print(f"❌ {e}")
        sys.exit(1)

    print_report(results)
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()

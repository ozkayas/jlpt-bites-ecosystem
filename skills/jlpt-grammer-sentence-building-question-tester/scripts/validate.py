#!/usr/bin/env python3
"""
JLPT N5 Sentence Building Question Validator
Validates starQuestion JSON for jlpt-n5-grammer-sentence-building-question-creator.

Usage:
    python3 validate.py <path-to-json-file>
    python3 validate.py --stdin
"""

import json
import re
import sys

ID_RE = re.compile(r"^n5_grammer_sentence_building_\d{3}$")


def validate_question(q, index):
    errors = []
    idx = f"questions[{index}]"

    # id
    qid = q.get("id", "")
    if not ID_RE.match(qid):
        errors.append(f"{idx}.id: '{qid}' does not match n5_grammer_sentence_building_XXX")

    # level
    if q.get("level") != "n5":
        errors.append(f"{idx}.level: expected 'n5', got '{q.get('level')}'")

    # type
    if q.get("type") != "starQuestion":
        errors.append(f"{idx}.type: expected 'starQuestion', got '{q.get('type')}'")

    # sentencePrefix
    prefix = q.get("sentencePrefix", "")
    if not isinstance(prefix, str) or not prefix.strip():
        errors.append(f"{idx}.sentencePrefix: must be a non-empty string")

    # sentenceSuffix
    suffix = q.get("sentenceSuffix", "")
    if not isinstance(suffix, str) or not suffix.strip():
        errors.append(f"{idx}.sentenceSuffix: must be a non-empty string")

    # scrambledWords — exactly 4 non-empty strings
    words = q.get("scrambledWords", [])
    if not isinstance(words, list) or len(words) != 4:
        errors.append(
            f"{idx}.scrambledWords: expected array of 4, got "
            f"{len(words) if isinstance(words, list) else type(words).__name__}"
        )
    elif any(not isinstance(w, str) or not w.strip() for w in words):
        errors.append(f"{idx}.scrambledWords: all items must be non-empty strings")

    # starPosition — 0-based index 0–3
    sp = q.get("starPosition")
    if not isinstance(sp, int) or sp < 0 or sp > 3:
        errors.append(f"{idx}.starPosition: expected integer 0-3, got {sp!r}")

    # correctOrder — permutation of [0,1,2,3]
    order = q.get("correctOrder", [])
    if not isinstance(order, list) or len(order) != 4:
        errors.append(
            f"{idx}.correctOrder: expected array of 4, got "
            f"{len(order) if isinstance(order, list) else type(order).__name__}"
        )
    elif sorted(order) != [0, 1, 2, 3]:
        errors.append(
            f"{idx}.correctOrder: must be a permutation of [0,1,2,3], got {order}"
        )

    return errors


def validate(data):
    results = {"passed": 0, "failed": 0, "questions": []}

    if not isinstance(data, dict) or "questions" not in data:
        return None, ["Top-level JSON must be an object with a 'questions' array"]

    questions = data["questions"]
    if not isinstance(questions, list) or len(questions) == 0:
        return None, ["'questions' must be a non-empty array"]

    for i, q in enumerate(questions):
        errs = validate_question(q, i)
        qid = q.get("id", f"<no id, index {i}>")
        status = "PASS" if not errs else "FAIL"
        results["questions"].append({"id": qid, "status": status, "errors": errs})
        if errs:
            results["failed"] += 1
        else:
            results["passed"] += 1

    return results, []


def print_report(results):
    total = results["passed"] + results["failed"]
    print(f"\n{'='*60}")
    print("JLPT N5 Sentence Building Question Tester — Results")
    print(f"{'='*60}")
    print(f"Total : {total}  |  PASS: {results['passed']}  |  FAIL: {results['failed']}")
    print(f"{'='*60}\n")

    for q in results["questions"]:
        mark = "✅" if q["status"] == "PASS" else "❌"
        print(f"{mark}  {q['id']}")
        for err in q["errors"]:
            print(f"     └─ {err}")

    print()
    if results["failed"] == 0:
        print("All questions passed validation.")
    else:
        print(f"{results['failed']} question(s) failed. See errors above.")
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

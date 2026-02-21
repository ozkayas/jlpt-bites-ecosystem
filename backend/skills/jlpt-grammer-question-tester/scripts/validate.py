#!/usr/bin/env python3
"""
JLPT Grammar Question Tester
Validates JSON produced by jlpt-n5-grammer-essential-grammer-question-creator.

Usage:
    python3 validate.py <path-to-json-file>
    python3 validate.py --stdin   (reads JSON from stdin)
"""

import json
import re
import sys

ID_RE = re.compile(r"^n5_essential_grammar_\d{3}$")
BLANK_RE = re.compile(r"（　　）")
RUBY_RE = re.compile(r"<ruby>.+?<rt>.+?</rt></ruby>")


def validate_question(q, index):
    errors = []
    idx = f"questions[{index}]"

    # id
    qid = q.get("id", "")
    if not ID_RE.match(qid):
        errors.append(f"{idx}.id: '{qid}' does not match n5_essential_grammar_XXX")

    # level
    if q.get("level") != "n5":
        errors.append(f"{idx}.level: expected 'n5', got '{q.get('level')}'")

    # type
    if q.get("type") != "sentenceCompletion":
        errors.append(f"{idx}.type: expected 'sentenceCompletion', got '{q.get('type')}'")

    # sentence — must contain blank marker
    sentence = q.get("sentence", "")
    if not BLANK_RE.search(sentence):
        errors.append(f"{idx}.sentence: missing blank marker （　　）")

    # furigana — must contain at least one <ruby> tag
    furigana = q.get("furigana", "")
    if not RUBY_RE.search(furigana):
        errors.append(f"{idx}.furigana: no <ruby> tags found")

    # blankPosition — positive integer
    bp = q.get("blankPosition")
    if not isinstance(bp, int) or bp < 1:
        errors.append(f"{idx}.blankPosition: expected positive integer, got {bp!r}")

    # options — exactly 4 non-empty strings
    options = q.get("options", [])
    if not isinstance(options, list) or len(options) != 4:
        errors.append(f"{idx}.options: expected array of 4, got {len(options) if isinstance(options, list) else type(options).__name__}")
    elif any(not isinstance(o, str) or not o.strip() for o in options):
        errors.append(f"{idx}.options: all options must be non-empty strings")

    # correctAnswer — 0-based index within options
    ca = q.get("correctAnswer")
    if not isinstance(ca, int) or ca < 0 or ca > 3:
        errors.append(f"{idx}.correctAnswer: expected integer 0-3, got {ca!r}")

    return errors


def validate(data):
    results = {"passed": 0, "failed": 0, "questions": []}

    if not isinstance(data, dict) or "questions" not in data:
        return None, ["Top-level JSON must be an object with a 'questions' array"]

    questions = data["questions"]
    if not isinstance(questions, list) or len(questions) == 0:
        return None, ["'questions' must be a non-empty array"]

    all_errors = []
    for i, q in enumerate(questions):
        errs = validate_question(q, i)
        qid = q.get("id", f"<no id, index {i}>")
        status = "PASS" if not errs else "FAIL"
        results["questions"].append({"id": qid, "status": status, "errors": errs})
        if errs:
            results["failed"] += 1
            all_errors.extend(errs)
        else:
            results["passed"] += 1

    return results, all_errors


def print_report(results, all_errors):
    total = results["passed"] + results["failed"]
    print(f"\n{'='*60}")
    print(f"JLPT Grammar Question Tester — Results")
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

    print_report(results, errors)
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()

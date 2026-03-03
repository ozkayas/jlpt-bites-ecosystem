#!/usr/bin/env python3
"""
Batch viewer for kanji_reading_drill.json — prints items in a readable format
for LLM semantic review.

Usage:
    python3 batch_viewer.py <path/to/kanji_reading_drill.json> [start_index] [count]

Defaults: start_index=0, count=5
"""
import json
import re
import sys
import os

TAG_RE = re.compile(r'<t>(.*?)</t>')


def extract_kanji(sentence):
    m = TAG_RE.search(sentence)
    return m.group(1) if m else '?'


def plain_sentence(sentence):
    """Return sentence with <t>…</t> replaced by 【…】 for readability."""
    return TAG_RE.sub(lambda m: f'【{m.group(1)}】', sentence)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch_viewer.py <path/to/json> [start] [count]")
        sys.exit(1)

    path = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    if not os.path.exists(path):
        print(f"Error: file not found: {path}")
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get('items', [])
    total = len(items)
    end = min(start + count, total)

    print(f"=== {os.path.basename(path)} — items {start}–{end - 1} of {total} ===\n")

    for i in range(start, end):
        item = items[i]
        item_id   = item[0]
        sentence  = item[1]
        trans     = item[2] if len(item) > 2 else {}
        options   = item[3] if len(item) > 3 else []

        kanji   = extract_kanji(sentence)
        correct = options[0] if options else '—'
        distractors = options[1:] if len(options) > 1 else []

        print(f"[{i}] ID: {item_id}")
        print(f"  Sentence  : {plain_sentence(sentence)}")
        print(f"  Kanji     : {kanji}")
        print(f"  ✅ Reading : {correct}")
        print(f"  ❌ Distract: {' / '.join(distractors)}")
        for lang in ('tr', 'en', 'de', 'es'):
            if lang in trans:
                print(f"  [{lang}]       : {trans[lang]}")
        print()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Upload script for N5 vocabulary words to Firestore.

Firestore structure:
  n5_vocabulary/{word_id}/
    - id: string
    - word: string          (e.g. "食べる")
    - reading: string       (e.g. "たべる")
    - romaji: string        (e.g. "taberu")
    - tag: string           (名詞 | 動詞 | 形容詞 | 副詞 | 表現)
    - translations: map     ({en, tr, de, es, fr})
    - audioUrl: string|null
    - sentences: list of 3  ({ja, romaji, translations: {en,tr,de,es,fr}})
    - uploaded_at: string   (ISO 8601 timestamp)

Usage:
    python3 upload_n5_vocabulary.py              # upload all words
    python3 upload_n5_vocabulary.py --tag 動詞   # upload only verb words
    python3 upload_n5_vocabulary.py --dry-run    # preview without uploading
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import argparse
from typing import Optional, List, Dict, Any


COLLECTION_NAME = 'n5_vocabulary'
BATCH_LIMIT = 400

VALID_TAGS = ['名詞', '動詞', '形容詞', '副詞', '表現', '接尾辞', '代名詞']


def initialize_firebase():
    """Initialize Firebase Admin SDK using shared service-account-key.json"""
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent / 'service-account-key.json'

    if key_path.exists():
        try:
            cred = credentials.Certificate(str(key_path))
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized (service-account-key.json)")
            return
        except Exception as e:
            print(f"⚠️  Found service-account-key.json but failed to load: {e}")

    # Fallback to Application Default Credentials
    try:
        print("⚠️  service-account-key.json not found. Using Application Default Credentials...")
        firebase_admin.initialize_app()
        print("✅ Firebase Admin SDK initialized (ADC)")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print(f"   Place 'service-account-key.json' at: {key_path}")
        print("   OR configure Google Application Default Credentials.")
        sys.exit(1)


def load_words(tag_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load words from JSON file, optionally filtering by tag."""
    data_path = Path(__file__).parent.parent / 'data' / 'n5_vocabulary.json'

    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        sys.exit(1)

    print(f"📖 Reading data from {data_path}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    words = data.get('words', [])
    if not words:
        print("⚠️  No words found in data file.")
        return []

    if tag_filter:
        words = [w for w in words if w.get('tag') == tag_filter]
        print(f"🔖 Filter applied: tag='{tag_filter}' → {len(words)} words")

    return words


def upload_words(db, words: List[Dict[str, Any]], dry_run: bool = False) -> int:
    """
    Upload words to Firestore n5_vocabulary collection.

    Returns the number of words uploaded (or that would be uploaded in dry-run).
    """
    if not words:
        print("ℹ️  Nothing to upload.")
        return 0

    collection_ref = db.collection(COLLECTION_NAME) if not dry_run else None
    batch = db.batch() if not dry_run else None
    count = 0
    total = 0
    timestamp = datetime.now(timezone.utc).isoformat()

    print(f"\n📚 Uploading {len(words)} word(s) to '{COLLECTION_NAME}'...\n")

    for word in words:
        word_id = word.get('id')
        if not word_id:
            print(f"  ⚠️  Skipping word without 'id' field: {word.get('word', '?')}")
            continue

        word_data = word.copy()
        word_data['uploaded_at'] = timestamp

        if dry_run:
            sentences_count = len(word_data.get('sentences', []))
            print(f"  [DRY-RUN] Would upload: {word_id} | {word_data.get('word')} "
                  f"({word_data.get('tag')}) | {sentences_count} sentences")
        else:
            doc_ref = collection_ref.document(word_id)
            batch.set(doc_ref, word_data)
            count += 1

            # Commit batch before hitting the limit
            if count >= BATCH_LIMIT:
                batch.commit()
                print(f"   ✓ Committed batch ({count} operations)")
                batch = db.batch()
                count = 0

        total += 1

    if not dry_run and count > 0 and batch is not None:
        batch.commit()
        print(f"   ✓ Committed final batch ({count} operations)")

    return total


def print_summary(words: List[Dict[str, Any]]):
    """Print a breakdown of words by tag."""
    from collections import Counter
    tag_counts = Counter(w.get('tag', 'unknown') for w in words)
    print("\n📊 Word breakdown by tag:")
    for tag in VALID_TAGS:
        count = tag_counts.get(tag, 0)
        print(f"   {tag}: {count} words")
    other = sum(v for k, v in tag_counts.items() if k not in VALID_TAGS)
    if other:
        print(f"   other: {other} words")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Upload N5 vocabulary words to Firestore.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 upload_n5_vocabulary.py                      Upload all words
  python3 upload_n5_vocabulary.py --tag 動詞            Upload only verbs
  python3 upload_n5_vocabulary.py --dry-run            Preview without uploading
  python3 upload_n5_vocabulary.py --tag 名詞 --dry-run  Preview nouns only
        """
    )
    parser.add_argument(
        '--tag',
        choices=VALID_TAGS,
        default=None,
        help='Upload only words with this tag (default: all tags)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be uploaded without writing to Firestore'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  N5 Vocabulary — Firestore Upload")
    print("=" * 60)

    if args.dry_run:
        print("🔍 DRY-RUN mode: no data will be written to Firestore\n")

    # Load data
    words = load_words(tag_filter=args.tag)
    if not words:
        print("No words to process. Exiting.")
        sys.exit(0)

    print_summary(words)

    # Initialize Firebase (skip in dry-run to avoid auth issues during testing)
    if not args.dry_run:
        initialize_firebase()
        db = firestore.client()
    else:
        db = None  # not used in dry-run

    # Upload
    try:
        uploaded = upload_words(db, words, dry_run=args.dry_run)

        print()
        print("=" * 60)
        if args.dry_run:
            print(f"🔍 DRY-RUN complete: {uploaded} word(s) would be uploaded")
        else:
            print(f"🎉 Upload complete: {uploaded} word(s) uploaded to '{COLLECTION_NAME}'")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\n💥 Upload failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

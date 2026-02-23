#!/usr/bin/env python3
"""
Upload script for JLPT N5 kanji list to Firestore.

Firestore structure:
  n5_kanji_list/{kanji_char}/
    - id: number
    - kanji: string          (e.g. "日")
    - meaning: map           ({en, tr, de, es, fr})
    - uploaded_at: string   (ISO 8601 timestamp)

Usage:
    python3 upload_n5_kanji.py              # upload all kanji
    python3 upload_n5_kanji.py --dry-run    # preview without uploading
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import argparse
from typing import Optional, List, Dict, Any


COLLECTION_NAME = 'n5_kanji_list'
BATCH_LIMIT = 400


def initialize_firebase():
    """Initialize Firebase Admin SDK using shared service-account-key.json"""
    script_dir = Path(__file__).parent
    # Look for service-account-key.json in project root
    key_path = script_dir.parent.parent.parent / 'service-account-key.json'

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


def load_kanji() -> List[Dict[str, Any]]:
    """Load kanji from JSON file."""
    data_path = Path(__file__).parent.parent / 'data' / 'n5_kanji_list.json'

    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        sys.exit(1)

    print(f"📖 Reading data from {data_path}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    kanji_list = data.get('data', [])
    if not kanji_list:
        print("⚠️  No kanji found in data file.")
        return []

    return kanji_list


def upload_kanji(db, kanji_list: List[Dict[str, Any]], dry_run: bool = False) -> int:
    """
    Upload kanji to Firestore n5_kanji_list collection.
    """
    if not kanji_list:
        print("ℹ️  Nothing to upload.")
        return 0

    collection_ref = db.collection(COLLECTION_NAME) if not dry_run else None
    batch = db.batch() if not dry_run else None
    count = 0
    total = 0
    timestamp = datetime.now(timezone.utc).isoformat()

    print(f"\n📚 Uploading {len(kanji_list)} kanji to '{COLLECTION_NAME}'...\n")

    for entry in kanji_list:
        kanji_char = entry.get('kanji')
        if not kanji_char:
            print(f"  ⚠️  Skipping entry without 'kanji' field: {entry}")
            continue

        doc_data = entry.copy()
        doc_data['uploaded_at'] = timestamp

        if dry_run:
            print(f"  [DRY-RUN] Would upload: {kanji_char} | ID: {doc_data.get('id')}")
        else:
            # Using the kanji character as the document ID for uniqueness and easy lookup
            doc_ref = collection_ref.document(kanji_char)
            batch.set(doc_ref, doc_data)
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


def main():
    parser = argparse.ArgumentParser(
        description='Upload N5 kanji list to Firestore.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be uploaded without writing to Firestore'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  N5 Kanji — Firestore Upload")
    print("=" * 60)

    if args.dry_run:
        print("🔍 DRY-RUN mode: no data will be written to Firestore\n")

    # Load data
    kanji_list = load_kanji()
    if not kanji_list:
        print("No kanji to process. Exiting.")
        sys.exit(0)

    # Initialize Firebase
    if not args.dry_run:
        initialize_firebase()
        db = firestore.client()
    else:
        db = None

    # Upload
    try:
        uploaded = upload_kanji(db, kanji_list, dry_run=args.dry_run)

        print()
        print("=" * 60)
        if args.dry_run:
            print(f"🔍 DRY-RUN complete: {uploaded} kanji would be uploaded")
        else:
            print(f"🎉 Upload complete: {uploaded} kanji uploaded to '{COLLECTION_NAME}'")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\n💥 Upload failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

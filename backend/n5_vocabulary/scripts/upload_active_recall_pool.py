#!/usr/bin/env python3
"""
Upload script for N5 Active Recall Pool checkpoints to Firestore.

Firestore structure:
  n5_active_recall_pool/{checkpoint_id}/
    - id: string              (e.g. "cp_15")
    - learned_word_count: int (e.g. 15)
    - sentences: list         (list of sentence objects)
    - uploaded_at: string     (ISO 8601 timestamp)

Each sentence object:
    - id: string
    - prompts: map            ({tr, en, de, es, fr, ko})
    - japanese_target: string
    - grammar_hints: map      ({tr, en, de, es, fr, ko})

Usage:
    python3 upload_active_recall_pool.py                             # upload all checkpoints
    python3 upload_active_recall_pool.py --file active_recall_pool.json
    python3 upload_active_recall_pool.py --checkpoint cp_15         # single checkpoint
    python3 upload_active_recall_pool.py --clear                    # delete all existing docs first
    python3 upload_active_recall_pool.py --dry-run                  # preview without uploading
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import argparse
from typing import Optional, List, Dict, Any


COLLECTION_NAME = 'n5_active_recall_pool'
BATCH_LIMIT = 400


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


def clear_collection(db, dry_run: bool = False):
    """Delete all documents in the n5_active_recall_pool collection."""
    print(f"\n🗑️  Clearing existing '{COLLECTION_NAME}' collection...")
    if dry_run:
        print("   [DRY-RUN] Would delete all documents.")
        return

    collection_ref = db.collection(COLLECTION_NAME)
    batch_size = 400
    deleted_total = 0

    while True:
        docs = collection_ref.limit(batch_size).stream()
        batch = db.batch()
        count = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
        if count == 0:
            break
        batch.commit()
        deleted_total += count
        print(f"   ✓ Deleted {deleted_total} documents so far...")

    print(f"   ✅ Collection cleared ({deleted_total} documents deleted).\n")


def load_checkpoints(
    filename: str = 'active_recall_pool.json',
    checkpoint_filter: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Load checkpoints from JSON file, optionally filtering by checkpoint id or limit."""
    data_path = Path(__file__).parent.parent / 'data' / filename

    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        sys.exit(1)

    print(f"📖 Reading data from {data_path}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    checkpoints = data.get('checkpoints', [])
    if not checkpoints:
        print("⚠️  No checkpoints found in data file.")
        return []

    if checkpoint_filter:
        checkpoints = [cp for cp in checkpoints if cp.get('id') == checkpoint_filter]
        if not checkpoints:
            print(f"❌ Checkpoint '{checkpoint_filter}' not found in data file.")
            sys.exit(1)
        print(f"🔖 Filter applied: checkpoint='{checkpoint_filter}' → 1 checkpoint")

    if limit is not None:
        checkpoints = checkpoints[:limit]
        print(f"🔢 Limit applied: first {len(checkpoints)} checkpoint(s)")

    return checkpoints


def upload_checkpoints(db, checkpoints: List[Dict[str, Any]], dry_run: bool = False) -> int:
    """
    Upload checkpoints to Firestore n5_active_recall_pool collection.

    Uses batch.set() — idempotent, safe to re-run.
    Returns the number of checkpoints uploaded (or that would be in dry-run).
    """
    if not checkpoints:
        print("ℹ️  Nothing to upload.")
        return 0

    collection_ref = db.collection(COLLECTION_NAME) if not dry_run else None
    batch = db.batch() if not dry_run else None
    count = 0
    total = 0
    timestamp = datetime.now(timezone.utc).isoformat()

    print(f"\n📚 Uploading {len(checkpoints)} checkpoint(s) to '{COLLECTION_NAME}'...\n")

    for cp in checkpoints:
        cp_id = cp.get('id')
        if not cp_id:
            print(f"  ⚠️  Skipping checkpoint without 'id' field (learned_word_count={cp.get('learned_word_count', '?')})")
            continue

        sentences = cp.get('sentences', [])

        if dry_run:
            print(f"  [DRY-RUN] Would upload: {cp_id} | {cp.get('learned_word_count')} words | {len(sentences)} sentences")
        else:
            doc_data = dict(cp)
            doc_data['uploaded_at'] = timestamp

            doc_ref = collection_ref.document(cp_id)
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


def print_summary(checkpoints: List[Dict[str, Any]]):
    """Print a summary of checkpoints to be uploaded."""
    total_sentences = sum(len(cp.get('sentences', [])) for cp in checkpoints)
    word_counts = [cp.get('learned_word_count', 0) for cp in checkpoints]
    print(f"\n📊 Summary:")
    print(f"   Checkpoints : {len(checkpoints)}")
    print(f"   Total sentences: {total_sentences}")
    if word_counts:
        print(f"   Word count range: cp_{min(word_counts)} → cp_{max(word_counts)}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Upload N5 Active Recall Pool checkpoints to Firestore.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 upload_active_recall_pool.py                         Upload all checkpoints
  python3 upload_active_recall_pool.py --dry-run               Preview without uploading
  python3 upload_active_recall_pool.py --checkpoint cp_15      Upload single checkpoint
  python3 upload_active_recall_pool.py --clear                 Clear collection then upload all
        """
    )
    parser.add_argument(
        '--file',
        default='active_recall_pool.json',
        help='JSON filename in data/ directory to upload (default: active_recall_pool.json)'
    )
    parser.add_argument(
        '--checkpoint',
        default=None,
        metavar='CP_ID',
        help='Upload only this checkpoint ID (e.g. cp_15)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Delete all existing documents in the collection before uploading'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        metavar='N',
        help='Upload only the first N checkpoints (in file order)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be uploaded without writing to Firestore'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  N5 Active Recall Pool — Firestore Upload")
    print("=" * 60)

    if args.dry_run:
        print("🔍 DRY-RUN mode: no data will be written to Firestore\n")

    # Load data
    checkpoints = load_checkpoints(filename=args.file, checkpoint_filter=args.checkpoint, limit=args.limit)
    if not checkpoints:
        print("No checkpoints to process. Exiting.")
        sys.exit(0)

    print_summary(checkpoints)

    # Initialize Firebase (skip in dry-run to avoid auth issues during testing)
    if not args.dry_run:
        initialize_firebase()
        db = firestore.client()
    else:
        db = None  # not used in dry-run

    # Clear collection if requested
    if args.clear:
        clear_collection(db, dry_run=args.dry_run)

    # Upload
    try:
        uploaded = upload_checkpoints(db, checkpoints, dry_run=args.dry_run)

        print()
        print("=" * 60)
        if args.dry_run:
            print(f"🔍 DRY-RUN complete: {uploaded} checkpoint(s) would be uploaded")
        else:
            print(f"🎉 Upload complete: {uploaded} checkpoint(s) uploaded to '{COLLECTION_NAME}'")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\n💥 Upload failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

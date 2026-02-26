#!/usr/bin/env python3
"""
Upload a lightweight vocabulary index to Firestore.

Creates/updates: vocabulary_meta/{collection_name}
  items: [ {id, word, reading, tag}, ... ]

This single document (~20 KB) lets the Flutter app bootstrap the SRS system
without fetching all 712 full word documents (485 KB). Full word content is
fetched on-demand per word, then cached locally in ObjectBox.

Usage:
    python3 upload_vocabulary_index.py                        # n5_vocabulary (default)
    python3 upload_vocabulary_index.py --collection n4_vocabulary
    python3 upload_vocabulary_index.py --dry-run
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

META_COLLECTION = 'vocabulary_meta'
BATCH_SIZE = 1  # We write a single document


def initialize_firebase():
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent / 'service-account-key.json'

    if key_path.exists():
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)
        print('✅ Firebase initialized')
    else:
        print(f'❌ service-account-key.json not found at {key_path}')
        raise FileNotFoundError(f'Missing key: {key_path}')


def load_vocabulary(json_path: Path) -> list[dict]:
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    words = data.get('words', data) if isinstance(data, dict) else data
    if not isinstance(words, list):
        raise ValueError(f'Unexpected JSON structure in {json_path}')
    return words


def build_index(words: list[dict]) -> list[dict]:
    return [
        {
            'id': w['id'],
            'word': w.get('word', ''),
            'reading': w.get('reading', ''),
            'tag': w.get('tag', ''),
        }
        for w in words
        if w.get('id')
    ]


def upload_index(collection_name: str, index: list[dict], dry_run: bool) -> None:
    doc = {
        'items': index,
        'count': len(index),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }

    if dry_run:
        print(f'[DRY-RUN] Would write {META_COLLECTION}/{collection_name}')
        print(f'  count: {len(index)}')
        print(f'  first item: {index[0] if index else "—"}')
        size_kb = len(json.dumps(doc).encode()) / 1024
        print(f'  estimated size: {size_kb:.1f} KB')
        return

    db = firestore.client()
    db.collection(META_COLLECTION).document(collection_name).set(doc)
    print(f'✅ Uploaded {META_COLLECTION}/{collection_name} ({len(index)} items)')


def main():
    parser = argparse.ArgumentParser(description='Upload vocabulary index to Firestore')
    parser.add_argument('--collection', default='n5_vocabulary',
                        help='Firestore collection name (default: n5_vocabulary)')
    parser.add_argument('--json', default=None,
                        help='Path to vocabulary JSON file (auto-detected if omitted)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without uploading')
    args = parser.parse_args()

    # Auto-detect JSON path relative to this script
    if args.json:
        json_path = Path(args.json)
    else:
        script_dir = Path(__file__).parent
        json_path = script_dir.parent / 'data' / 'n5_vocabulary.json'

    if not json_path.exists():
        print(f'❌ JSON not found: {json_path}')
        return

    print(f'📖 Loading {json_path}...')
    words = load_vocabulary(json_path)
    print(f'   {len(words)} words found')

    index = build_index(words)
    size_kb = len(json.dumps({'items': index}).encode()) / 1024
    print(f'   Index size: {size_kb:.1f} KB (was ~485 KB for full collection)')

    if not args.dry_run:
        initialize_firebase()

    upload_index(args.collection, index, dry_run=args.dry_run)


if __name__ == '__main__':
    main()

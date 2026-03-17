#!/usr/bin/env python3
"""
Add a new UI language to all checkpoints in the n5_active_recall_pool Firestore collection.

For each checkpoint document, this script updates every sentence's:
  - prompts.{lang}       — translation of the prompt
  - grammar_hints.{lang} — grammar hint in the new language

Uses Firestore update() (not set()), so existing fields are preserved.
The translations are sourced from a local JSON file (same format as active_recall_pool.json)
that must already contain the new language data.

Usage:
    python3 add_language_to_pool.py --lang ja_romanized --file active_recall_pool_ja_romanized.json
    python3 add_language_to_pool.py --lang pt --file active_recall_pool_pt.json --dry-run
    python3 add_language_to_pool.py --lang zh --file active_recall_pool.json --checkpoint cp_15
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

    try:
        print("⚠️  service-account-key.json not found. Using Application Default Credentials...")
        firebase_admin.initialize_app()
        print("✅ Firebase Admin SDK initialized (ADC)")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print(f"   Place 'service-account-key.json' at: {key_path}")
        print("   OR configure Google Application Default Credentials.")
        sys.exit(1)


def load_source_checkpoints(filename: str, checkpoint_filter: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Load checkpoints from local JSON file.
    Returns a dict keyed by checkpoint id for fast lookup.
    """
    data_path = Path(__file__).parent.parent / 'data' / filename

    if not data_path.exists():
        print(f"❌ Source file not found: {data_path}")
        sys.exit(1)

    print(f"📖 Reading source data from {data_path}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    checkpoints = data.get('checkpoints', [])
    if not checkpoints:
        print("❌ No checkpoints found in source file.")
        sys.exit(1)

    result = {}
    for cp in checkpoints:
        cp_id = cp.get('id')
        if cp_id:
            if checkpoint_filter is None or cp_id == checkpoint_filter:
                result[cp_id] = cp

    if checkpoint_filter and checkpoint_filter not in result:
        print(f"❌ Checkpoint '{checkpoint_filter}' not found in source file.")
        sys.exit(1)

    return result


def build_sentence_index(checkpoint: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Return a dict of sentence_id → sentence for a checkpoint."""
    return {s['id']: s for s in checkpoint.get('sentences', []) if 'id' in s}


def add_language(
    db,
    lang: str,
    source_checkpoints: Dict[str, Dict[str, Any]],
    dry_run: bool = False
) -> int:
    """
    For each checkpoint in source_checkpoints, update Firestore documents
    by merging the new language into prompts.{lang} and grammar_hints.{lang}
    for each sentence.

    Uses update() with dot-notation paths to avoid overwriting sibling fields.
    Returns number of checkpoints updated.
    """
    if not source_checkpoints:
        print("ℹ️  Nothing to update.")
        return 0

    collection_ref = db.collection(COLLECTION_NAME) if not dry_run else None
    batch = db.batch() if not dry_run else None
    op_count = 0
    updated_cp_count = 0
    timestamp = datetime.now(timezone.utc).isoformat()

    print(f"\n🌐 Adding language '{lang}' to {len(source_checkpoints)} checkpoint(s)...\n")

    for cp_id, source_cp in source_checkpoints.items():
        sentence_index = build_sentence_index(source_cp)
        sentences_updated = 0

        if dry_run:
            for s_id, sentence in sentence_index.items():
                prompt_val = sentence.get('prompts', {}).get(lang)
                hint_val = sentence.get('grammar_hints', {}).get(lang)
                has_prompt = prompt_val is not None
                has_hint = hint_val is not None
                status = []
                if has_prompt:
                    status.append(f"prompts.{lang}='{str(prompt_val)[:30]}'")
                if has_hint:
                    status.append(f"grammar_hints.{lang}='{str(hint_val)[:30]}'")
                if status:
                    print(f"  [DRY-RUN] {cp_id}/{s_id}: {' | '.join(status)}")
                    sentences_updated += 1
            print(f"  → {cp_id}: {sentences_updated} sentence(s) would be updated")
        else:
            # Fetch the Firestore document to get current sentences array
            doc_ref = collection_ref.document(cp_id)
            doc_snap = doc_ref.get()

            if not doc_snap.exists:
                print(f"  ⚠️  Document '{cp_id}' not found in Firestore — skipping")
                continue

            firestore_data = doc_snap.to_dict()
            firestore_sentences = firestore_data.get('sentences', [])

            # Rebuild sentences list with new language fields merged in
            updated_sentences = []
            for fs_sentence in firestore_sentences:
                s_id = fs_sentence.get('id')
                merged = dict(fs_sentence)

                if s_id and s_id in sentence_index:
                    source_sentence = sentence_index[s_id]

                    # Merge prompts
                    new_prompt = source_sentence.get('prompts', {}).get(lang)
                    if new_prompt is not None:
                        prompts = dict(merged.get('prompts', {}))
                        prompts[lang] = new_prompt
                        merged['prompts'] = prompts
                        sentences_updated += 1

                    # Merge grammar_hints
                    new_hint = source_sentence.get('grammar_hints', {}).get(lang)
                    if new_hint is not None:
                        hints = dict(merged.get('grammar_hints', {}))
                        hints[lang] = new_hint
                        merged['grammar_hints'] = hints

                updated_sentences.append(merged)

            # Update the document with the merged sentences array
            update_data = {
                'sentences': updated_sentences,
                f'language_added_{lang}_at': timestamp,
            }
            batch.update(doc_ref, update_data)
            op_count += 1

            print(f"  ✓ Queued update for {cp_id} ({sentences_updated} sentence(s) enriched)")

            # Commit before hitting limit
            if op_count >= BATCH_LIMIT:
                batch.commit()
                print(f"   ✓ Committed batch ({op_count} operations)")
                batch = db.batch()
                op_count = 0

        updated_cp_count += 1

    if not dry_run and op_count > 0 and batch is not None:
        batch.commit()
        print(f"   ✓ Committed final batch ({op_count} operations)")

    return updated_cp_count


def main():
    parser = argparse.ArgumentParser(
        description='Add a new UI language to n5_active_recall_pool Firestore documents.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 add_language_to_pool.py --lang ja_romanized --file active_recall_pool_ja.json
  python3 add_language_to_pool.py --lang pt --file active_recall_pool_pt.json --dry-run
  python3 add_language_to_pool.py --lang zh --file active_recall_pool.json --checkpoint cp_15
        """
    )
    parser.add_argument(
        '--lang',
        required=True,
        metavar='LANG_CODE',
        help='Language code to add (e.g. ja_romanized, pt, zh, ar)'
    )
    parser.add_argument(
        '--file',
        required=True,
        metavar='FILENAME',
        help='JSON filename in data/ directory containing the new language translations'
    )
    parser.add_argument(
        '--checkpoint',
        default=None,
        metavar='CP_ID',
        help='Update only this checkpoint ID (e.g. cp_15). Default: all checkpoints.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be updated without writing to Firestore'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  N5 Active Recall Pool — Add Language")
    print("=" * 60)

    if args.dry_run:
        print("🔍 DRY-RUN mode: no data will be written to Firestore\n")

    # Load source data
    source_checkpoints = load_source_checkpoints(
        filename=args.file,
        checkpoint_filter=args.checkpoint
    )
    print(f"   Loaded {len(source_checkpoints)} checkpoint(s) from source file.")

    # Initialize Firebase
    if not args.dry_run:
        initialize_firebase()
        db = firestore.client()
    else:
        db = None

    # Add language
    try:
        updated = add_language(
            db=db,
            lang=args.lang,
            source_checkpoints=source_checkpoints,
            dry_run=args.dry_run
        )

        print()
        print("=" * 60)
        if args.dry_run:
            print(f"🔍 DRY-RUN complete: '{args.lang}' would be added to {updated} checkpoint(s)")
        else:
            print(f"🎉 Done: language '{args.lang}' added to {updated} checkpoint(s) in '{COLLECTION_NAME}'")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\n💥 Update failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

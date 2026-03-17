#!/usr/bin/env python3
"""
Migrate audio files in Firebase Storage from old IDs to new IDs.

Background:
    n5_vocabulary_v01.json reordered words pedagogically and reassigned IDs.
    Storage audio files still use old IDs. This script copies them to new paths
    and updates audioUrl fields in v01.json.

What it does:
    1. Builds word → old_id mapping from n5_vocabulary.json (old file)
    2. For each word in v01.json, finds old_id → new_id pairs
    3. Copies Storage files: words/{old_id}.mp3 → words/{new_id}.mp3
                             sentences/{old_id}_sN.mp3 → sentences/{new_id}_sN.mp3
    4. Updates audioUrl fields in v01.json
    5. Saves updated v01.json (in-place)

Special cases:
    - Words only in old file (removed in v01): skipped, orphan audio left in Storage
    - Words where sentence content changed: sentence audioUrl set to null
    - Words where ID didn't change: skipped (no copy needed)

Usage:
    python3 migrate_audio_ids.py --dry-run   # preview, no changes
    python3 migrate_audio_ids.py             # run migration
    python3 migrate_audio_ids.py --bucket jlpt-bites.firebasestorage.app
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, storage

BUCKET_NAME = 'jlpt-bites.firebasestorage.app'
WORDS_PREFIX = 'sounds/n5_vocabulary/words'
SENTENCES_PREFIX = 'sounds/n5_vocabulary/sentences'

# Words whose sentence content changed between old and v01 — sentence audio needs regeneration
SENTENCES_CHANGED = {'～かい'}


def initialize_firebase(bucket_name: str):
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent / 'service-account-key.json'
    cred = credentials.Certificate(str(key_path))
    firebase_admin.initialize_app(cred, {'storageBucket': bucket_name})
    print(f'✅ Firebase initialized (bucket: {bucket_name})')


def load_json(path: Path) -> dict:
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def build_mapping(old_words: list, new_words: list) -> list[dict]:
    """
    Returns list of:
      { word, old_id, new_id, sentence_count, sentences_changed }
    Only includes words where old_id != new_id.
    """
    old_map = {w['word']: w for w in old_words}
    mapping = []
    for w in new_words:
        word = w['word']
        if word not in old_map:
            continue  # new word added in v01, no old audio to migrate
        old_id = old_map[word]['id']
        new_id = w['id']
        if old_id == new_id:
            continue  # no change needed
        mapping.append({
            'word': word,
            'old_id': old_id,
            'new_id': new_id,
            'sentence_count': len(w.get('sentences', [])),
            'sentences_changed': word in SENTENCES_CHANGED,
        })
    return mapping


def copy_blob(bucket, src_path: str, dst_path: str, dry_run: bool) -> bool:
    """Copy a blob in Storage and make it public. Returns True if successful (or would be in dry-run)."""
    if dry_run:
        return True  # assume exists in dry-run
    src_blob = bucket.blob(src_path)
    if not src_blob.exists():
        return False
    new_blob = bucket.copy_blob(src_blob, bucket, dst_path)
    new_blob.make_public()
    return True


def migrate_storage(bucket, mapping: list[dict], dry_run: bool):
    """Copy all audio files from old IDs to new IDs."""
    print(f'\n📦 Migrating {len(mapping)} words in Storage...\n')
    ok = skipped_word = skipped_sentence = 0

    for entry in mapping:
        old_id = entry['old_id']
        new_id = entry['new_id']
        word = entry['word']

        # Word audio
        src = f'{WORDS_PREFIX}/{old_id}.mp3'
        dst = f'{WORDS_PREFIX}/{new_id}.mp3'
        if copy_blob(bucket, src, dst, dry_run):
            if dry_run:
                print(f'  [DRY] {old_id}.mp3 → {new_id}.mp3  ({word})')
            ok += 1
        else:
            print(f'  ⚠️  Missing word audio: {src}  ({word})')
            skipped_word += 1

        # Sentence audio
        if entry['sentences_changed']:
            print(f'  ⚠️  Sentences changed for "{word}" — sentence audio will be cleared (needs regeneration)')
            skipped_sentence += entry['sentence_count']
            continue

        for i in range(1, entry['sentence_count'] + 1):
            src = f'{SENTENCES_PREFIX}/{old_id}_s{i}.mp3'
            dst = f'{SENTENCES_PREFIX}/{new_id}_s{i}.mp3'
            if copy_blob(bucket, src, dst, dry_run):
                ok += 1
            else:
                print(f'  ⚠️  Missing sentence audio: {src}')
                skipped_sentence += 1

    print(f'\n  ✅ Copied: {ok} files')
    if skipped_word:
        print(f'  ⚠️  Missing word audio: {skipped_word} files')
    if skipped_sentence:
        print(f'  ⚠️  Missing/skipped sentence audio: {skipped_sentence} files')


def update_json(v01_path: Path, new_words: list, mapping: list[dict], bucket_name: str, dry_run: bool):
    """Update audioUrl fields in v01.json to use new ID paths."""
    print(f'\n✏️  Updating audioUrl fields in v01.json...')

    base_url = f'https://storage.googleapis.com/{bucket_name}'

    # Build lookup: new_id → mapping entry
    migration_map = {entry['new_id']: entry for entry in mapping}

    updated_words = 0
    updated_sentences = 0
    cleared_sentences = 0

    for word in new_words:
        new_id = word['id']
        if new_id not in migration_map:
            continue  # ID didn't change, audioUrl already correct

        entry = migration_map[new_id]

        # Update word audioUrl
        word['audioUrl'] = f'{base_url}/{WORDS_PREFIX}/{new_id}.mp3'
        updated_words += 1

        # Update sentence audioUrls
        for i, sentence in enumerate(word.get('sentences', []), start=1):
            if entry['sentences_changed']:
                sentence['audioUrl'] = None
                cleared_sentences += 1
            else:
                sentence['audioUrl'] = f'{base_url}/{SENTENCES_PREFIX}/{new_id}_s{i}.mp3'
                updated_sentences += 1

    print(f'  Word audioUrls updated: {updated_words}')
    print(f'  Sentence audioUrls updated: {updated_sentences}')
    if cleared_sentences:
        print(f'  Sentence audioUrls cleared (needs regen): {cleared_sentences}')

    if not dry_run:
        data = load_json(v01_path)
        data['words'] = new_words
        with open(v01_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'  💾 Saved: {v01_path}')
    else:
        print(f'  [DRY] Would save: {v01_path}')


def main():
    parser = argparse.ArgumentParser(description='Migrate vocabulary audio IDs in Storage')
    parser.add_argument('--bucket', default=BUCKET_NAME, help='Firebase Storage bucket name')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    data_dir = Path(__file__).parent.parent / 'data'
    old_path = data_dir / 'n5_vocabulary.json'
    v01_path = data_dir / 'n5_vocabulary_v01.json'

    print('=' * 60)
    print('  N5 Vocabulary — Audio ID Migration')
    print('=' * 60)
    if args.dry_run:
        print('🔍 DRY-RUN: no changes will be made\n')

    old_data = load_json(old_path)
    v01_data = load_json(v01_path)
    old_words = old_data['words']
    new_words = v01_data['words']

    print(f'📖 Old file: {len(old_words)} words')
    print(f'📖 New file (v01): {len(new_words)} words')

    mapping = build_mapping(old_words, new_words)
    print(f'🔀 Words needing migration: {len(mapping)}')

    if not mapping:
        print('ℹ️  Nothing to migrate.')
        sys.exit(0)

    if not args.dry_run:
        initialize_firebase(args.bucket)
        bucket = storage.bucket()
    else:
        bucket = None

    migrate_storage(bucket, mapping, dry_run=args.dry_run)
    update_json(v01_path, new_words, mapping, args.bucket, dry_run=args.dry_run)

    print()
    print('=' * 60)
    if args.dry_run:
        print('🔍 DRY-RUN complete. Run without --dry-run to apply changes.')
    else:
        print('🎉 Migration complete!')
        print('   Next steps:')
        print('   1. python3 upload_n5_vocabulary.py --file n5_vocabulary_v01.json --clear')
        print('   2. python3 upload_vocabulary_index.py --json data/n5_vocabulary_v01.json')
        print('   3. Re-generate audio for "～かい" sentences (1 word)')
    print('=' * 60)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Generate TTS audio for N5 vocabulary words and sentences,
upload them to Firebase Storage, and update audioUrl fields
in the local n5_vocabulary.json file.

Storage paths:
  sounds/n5_vocabulary/words/{word_id}.mp3
  sounds/n5_vocabulary/sentences/{word_id}_s1.mp3
                                 {word_id}_s2.mp3
                                 {word_id}_s3.mp3

JSON fields updated (in-place):
  words[i].audioUrl
  words[i].sentences[j].audioUrl

Firestore is NOT touched by this script.
Run upload_n5_vocabulary.py afterwards to sync the updated JSON to Firestore.

Usage:
  python3 generate_and_upload_audio.py
  python3 generate_and_upload_audio.py --dry-run
  python3 generate_and_upload_audio.py --force     # overwrite existing files
  python3 generate_and_upload_audio.py --words-only
  python3 generate_and_upload_audio.py --sentences-only
"""

import firebase_admin
from firebase_admin import credentials, storage
import json
import sys
import os
import tempfile
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

BUCKET_NAME = 'jlpt-bites.firebasestorage.app'
STORAGE_WORDS_PREFIX = 'sounds/n5_vocabulary/words'
STORAGE_SENTENCES_PREFIX = 'sounds/n5_vocabulary/sentences'


def initialize_firebase():
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent / 'service-account-key.json'

    options = {'storageBucket': BUCKET_NAME}

    if key_path.exists():
        try:
            cred = credentials.Certificate(str(key_path))
            firebase_admin.initialize_app(cred, options)
            print('✅ Firebase initialized (service-account-key.json)')
            return
        except Exception as e:
            print(f'⚠️  service-account-key.json failed: {e}')

    try:
        firebase_admin.initialize_app(options=options)
        print('✅ Firebase initialized (ADC)')
    except Exception as e:
        print(f'❌ Firebase init failed: {e}')
        sys.exit(1)


def generate_tts(text: str, output_path: str) -> bool:
    """Generate TTS audio using gTTS and save to output_path."""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='ja', slow=False)
        tts.save(output_path)
        return True
    except ImportError:
        print('❌ gTTS not installed. Run: pip3 install gTTS')
        sys.exit(1)
    except Exception as e:
        print(f'   ⚠️  TTS failed for "{text}": {e}')
        return False


def upload_to_storage(bucket, local_path: str, remote_path: str) -> Optional[str]:
    """Upload file to Firebase Storage and return public URL."""
    try:
        blob = bucket.blob(remote_path)
        blob.upload_from_filename(local_path)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f'   ❌ Upload failed for {remote_path}: {e}')
        return None


def get_blob_url(bucket, remote_path: str) -> Optional[str]:
    """Return the public URL if the blob already exists, otherwise None."""
    blob = bucket.blob(remote_path)
    if blob.exists():
        blob.make_public()
        return blob.public_url
    return None


def load_data() -> Dict[str, Any]:
    data_path = Path(__file__).parent.parent / 'data' / 'n5_vocabulary.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data: Dict[str, Any]) -> None:
    data_path = Path(__file__).parent.parent / 'data' / 'n5_vocabulary.json'
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'\n💾 JSON updated: {data_path}')


def process_words(bucket, words: List[Dict[str, Any]],
                  do_words: bool, do_sentences: bool,
                  force: bool, dry_run: bool) -> int:
    """
    Generate and upload audio for each word/sentence.
    Updates audioUrl fields directly in the word dicts (in-place).
    Returns total number of audio files processed.
    """
    total = 0

    for word in words:
        word_id = word['id']
        word_text = word['word']
        sentences = word.get('sentences', [])

        print(f'\n📖 {word_id} | {word_text}')

        # ── Word audio ──────────────────────────────────────────────────────
        if do_words:
            remote_word = f'{STORAGE_WORDS_PREFIX}/{word_id}.mp3'

            if dry_run:
                print(f'   [DRY-RUN] Would generate & upload word audio: {remote_word}')
                total += 1
            elif not force:
                existing_url = get_blob_url(bucket, remote_word)
                if existing_url:
                    word['audioUrl'] = existing_url
                    print(f'   ✅ Word audio already exists → JSON updated')
                    total += 1
                else:
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                        tmp_path = tmp.name
                    try:
                        if generate_tts(word_text, tmp_path):
                            url = upload_to_storage(bucket, tmp_path, remote_word)
                            if url:
                                word['audioUrl'] = url
                                print(f'   ✅ Word audio uploaded → JSON updated')
                                total += 1
                            else:
                                print(f'   ❌ Word audio upload failed')
                    finally:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
            else:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                    tmp_path = tmp.name
                try:
                    if generate_tts(word_text, tmp_path):
                        url = upload_to_storage(bucket, tmp_path, remote_word)
                        if url:
                            word['audioUrl'] = url
                            print(f'   ✅ Word audio uploaded (forced) → JSON updated')
                            total += 1
                        else:
                            print(f'   ❌ Word audio upload failed')
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

        # ── Sentence audio ───────────────────────────────────────────────────
        if do_sentences:
            for idx, sentence in enumerate(sentences, start=1):
                sentence_text = sentence['ja']
                remote_sent = f'{STORAGE_SENTENCES_PREFIX}/{word_id}_s{idx}.mp3'

                if dry_run:
                    print(f'   [DRY-RUN] Would generate sentence {idx}: {remote_sent}')
                    total += 1
                    continue

                if not force:
                    existing_url = get_blob_url(bucket, remote_sent)
                    if existing_url:
                        sentence['audioUrl'] = existing_url
                        print(f'   ✅ Sentence {idx} audio already exists → JSON updated')
                        total += 1
                        continue

                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                    tmp_path = tmp.name

                try:
                    if generate_tts(sentence_text, tmp_path):
                        url = upload_to_storage(bucket, tmp_path, remote_sent)
                        if url:
                            sentence['audioUrl'] = url
                            label = '(forced) ' if force else ''
                            print(f'   ✅ Sentence {idx} audio uploaded {label}→ JSON updated')
                            total += 1
                        else:
                            print(f'   ❌ Sentence {idx} upload failed')
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

    return total


def main():
    parser = argparse.ArgumentParser(
        description='Generate TTS audio for N5 vocabulary and upload to Firebase Storage.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without generating or uploading')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite existing audio files in Storage')
    parser.add_argument('--words-only', action='store_true',
                        help='Only generate word audio')
    parser.add_argument('--sentences-only', action='store_true',
                        help='Only generate sentence audio')
    args = parser.parse_args()

    do_words = not args.sentences_only
    do_sentences = not args.words_only

    print('='*60)
    print('  N5 Vocabulary — Audio Generation & Upload')
    print('='*60)
    if args.dry_run:
        print('🔍 DRY-RUN mode\n')

    data = load_data()
    words = data['words']
    print(f'📚 Loaded {len(words)} words from JSON\n')

    if not args.dry_run:
        initialize_firebase()
        bucket = storage.bucket()
        print(f'🪣 Storage bucket: {bucket.name}\n')
    else:
        bucket = None

    total = process_words(bucket, words,
                          do_words=do_words,
                          do_sentences=do_sentences,
                          force=args.force,
                          dry_run=args.dry_run)

    print(f'\n{"="*60}')
    if args.dry_run:
        print(f'🔍 DRY-RUN: {total} audio file(s) would be generated')
    else:
        if total > 0:
            save_data(data)
        print(f'🎉 Done! {total} audio file(s) uploaded, JSON updated')
    print('='*60)


if __name__ == '__main__':
    main()

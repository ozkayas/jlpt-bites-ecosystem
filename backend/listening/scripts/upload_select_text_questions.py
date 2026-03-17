import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
import re
import sys
from pathlib import Path
import argparse

COLLECTION = 'n5_listening_select_text_questions'
STORAGE_PREFIX = 'listening/selectText'

def initialize_firebase(bucket_name=None):
    """Initialize Firebase Admin SDK"""
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent / 'service-account-key.json'

    options = {}
    if bucket_name:
        options['storageBucket'] = bucket_name

    if key_path.exists():
        try:
            cred = credentials.Certificate(str(key_path))
            firebase_admin.initialize_app(cred, options)
            print("Firebase initialized (service-account-key.json)")
            return
        except Exception as e:
            print(f"Failed to load service-account-key.json: {e}")

    try:
        firebase_admin.initialize_app(options=options)
        print("Firebase initialized (ADC)")
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        sys.exit(1)

def upload_file(bucket, local_path, remote_path):
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(str(local_path))
    blob.make_public()
    return blob.public_url

def process_select_text_folders(db, bucket, base_dir, folder_filter=None, force=False):
    select_text_dir = base_dir / 'data' / 'selectText'
    if not select_text_dir.exists():
        print(f"Directory not found: {select_text_dir}")
        return

    # Only process numbered folders (001, 002, ...)
    folders = sorted([
        d for d in select_text_dir.iterdir()
        if d.is_dir() and re.match(r'^\d{3}$', d.name)
    ])

    if folder_filter:
        folders = [d for d in folders if d.name == folder_filter]
        if not folders:
            print(f"Folder '{folder_filter}' not found.")
            return

    uploaded = 0
    skipped = 0
    errors = 0

    for question_dir in folders:
        question_id = question_dir.name

        # Prefer question.json (Fat JSON), fallback to question_data.json
        json_path = question_dir / 'question.json'
        if not json_path.exists():
            json_path = question_dir / 'question_data.json'
        if not json_path.exists():
            print(f"  {question_id}: question.json missing, skipping")
            errors += 1
            continue

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Idempotency: skip if audio_url already set (unless --force)
        existing_url = data.get('audio_url')
        if existing_url and not force:
            print(f"  {question_id}: already uploaded, skipping (use --force to re-upload)")
            skipped += 1
            continue

        # 1. Upload Audio
        audio_path = question_dir / 'audio.mp3'
        if audio_path.exists():
            remote_audio_path = f"{STORAGE_PREFIX}/{question_id}/audio.mp3"
            audio_url = upload_file(bucket, audio_path, remote_audio_path)
            data['audio_url'] = audio_url
            print(f"  {question_id}: audio uploaded")
        else:
            print(f"  {question_id}: audio.mp3 missing, uploading data only")

        # 2. Update JSON locally
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # 3. Upload to Firestore
        doc_ref = db.collection(COLLECTION).document(question_id)
        doc_ref.set(data)
        print(f"  {question_id}: Firestore OK")
        uploaded += 1

    print(f"\nDone: {uploaded} uploaded, {skipped} skipped, {errors} errors (total {len(folders)})")

def main():
    parser = argparse.ArgumentParser(description='Upload selectText questions to Firebase')
    parser.add_argument('--bucket', default='jlpt-bites.firebasestorage.app',
                        help='Firebase Storage bucket (default: jlpt-bites.firebasestorage.app)')
    parser.add_argument('--folder', help='Specific folder to upload (e.g. 001)')
    parser.add_argument('--force', action='store_true',
                        help='Re-upload even if audio_url already set')
    args = parser.parse_args()

    base_dir = Path(__file__).parent.parent
    initialize_firebase(args.bucket)

    db = firestore.client()
    bucket = storage.bucket()
    print(f"Bucket: {bucket.name}")
    print(f"Collection: {COLLECTION}")
    print(f"Data dir: {base_dir / 'data' / 'selectText'}\n")

    process_select_text_folders(db, bucket, base_dir,
                                folder_filter=args.folder,
                                force=args.force)

if __name__ == "__main__":
    main()

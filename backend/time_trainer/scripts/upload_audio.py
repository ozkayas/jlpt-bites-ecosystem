# Usage (listening venv has firebase-admin installed):
#   PYTHONPATH=backend/listening/scripts/venv/lib/python3.13/site-packages \
#   python3.13 backend/time_trainer/scripts/upload_audio.py --bucket jlpt-bites.firebasestorage.app
#
# Options: --force (overwrite existing), --dry-run (list only)

import firebase_admin
from firebase_admin import credentials, storage
import sys
from pathlib import Path
import argparse


def initialize_firebase(bucket_name):
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent / 'service-account-key.json'

    options = {'storageBucket': bucket_name}

    if key_path.exists():
        try:
            cred = credentials.Certificate(str(key_path))
            firebase_admin.initialize_app(cred, options)
            print(f"Firebase initialized (service-account-key.json)")
            return storage.bucket()
        except Exception as e:
            print(f"Found service-account-key.json but failed to load: {e}")

    try:
        print("service-account-key.json not found. Trying Application Default Credentials...")
        firebase_admin.initialize_app(options=options)
        return storage.bucket()
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        print(f"Place 'service-account-key.json' in {key_path.parent} or set up ADC.")
        sys.exit(1)


def upload_mp3(bucket, local_path, remote_path, force=False):
    blob = bucket.blob(remote_path)
    if blob.exists() and not force:
        return None  # skip
    blob.upload_from_filename(str(local_path), content_type='audio/mpeg')
    blob.make_public()
    return blob.public_url


def main():
    parser = argparse.ArgumentParser(description='Upload time trainer MP3s to Firebase Storage')
    parser.add_argument('--bucket', required=True, help='Firebase Storage bucket (e.g. jlpt-bites.firebasestorage.app)')
    parser.add_argument('--force', action='store_true', help='Overwrite existing blobs')
    parser.add_argument('--dry-run', action='store_true', help='List files without uploading')
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    verified_dir = script_dir.parent / 'output_verified'

    mp3_files = sorted(verified_dir.glob('*.mp3'))
    if not mp3_files:
        print(f"No MP3 files found in {verified_dir}")
        sys.exit(1)

    print(f"Found {len(mp3_files)} MP3 files in {verified_dir}\n")

    if args.dry_run:
        for f in mp3_files:
            remote = f"time_trainer/audio/{f.name}"
            print(f"  {f.name} -> {remote}")
        print(f"\n[dry-run] {len(mp3_files)} files would be uploaded.")
        return

    bucket = initialize_firebase(args.bucket)
    print(f"Storage bucket: {bucket.name}\n")

    uploaded = 0
    skipped = 0

    for f in mp3_files:
        remote = f"time_trainer/audio/{f.name}"
        url = upload_mp3(bucket, f, remote, force=args.force)
        if url is None:
            print(f"  [skip] {f.name}")
            skipped += 1
        else:
            print(f"  [ok]   {f.name} -> {url}")
            uploaded += 1

    print(f"\nDone. Uploaded: {uploaded}, Skipped: {skipped}")


if __name__ == "__main__":
    main()

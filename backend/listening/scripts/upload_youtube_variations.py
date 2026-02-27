import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import argparse
from PIL import Image


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
            print("✅ Firebase Admin SDK initialized (using service-account-key.json)")
            return
        except Exception as e:
            print(f"⚠️ Found service-account-key.json but failed to load: {e}")

    try:
        print("⚠️ service-account-key.json not found. Attempting to use Application Default Credentials...")
        firebase_admin.initialize_app(options=options)
        print("✅ Firebase Admin SDK initialized (using ADC)")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print(f"   Please place 'service-account-key.json' in {script_dir.parent.parent}")
        print("   OR ensure you have Google Application Default Credentials set up.")
        sys.exit(1)


def upload_file(bucket, local_path, remote_path):
    print(f"   ⬆️ Uploading {Path(local_path).name} to {remote_path}...")
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(str(local_path))
    blob.make_public()
    return blob.public_url


def get_next_firestore_id(db):
    """Return the next sequential doc ID (zero-padded 3 digits) by querying Firestore."""
    collection_ref = db.collection('n5_listening_select_image_questions')
    docs = collection_ref.stream()
    max_id = 0
    for doc in docs:
        try:
            doc_id = int(doc.id)
            if doc_id > max_id:
                max_id = doc_id
        except ValueError:
            pass
    return str(max_id + 1).zfill(3)


def compress_image(src_path, max_size=1024):
    """Compress and optionally resize an image before upload."""
    img = Image.open(src_path)
    original_size = img.size
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        print(f"   📐 Image resized: {original_size} → {img.size}")
    else:
        print(f"   📐 Image size OK ({img.size}), optimizing only")
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(tmp.name, 'PNG', optimize=True)
    return Path(tmp.name)


def convert_wav_to_mp3(wav_path, mp3_path):
    """Convert a WAV file to MP3 using ffmpeg."""
    result = subprocess.run(
        ['ffmpeg', '-y', '-i', str(wav_path), '-codec:a', 'libmp3lame', '-qscale:a', '2', str(mp3_path)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")


def process_youtube_variations(db, bucket, processed_dir):
    if not processed_dir.exists():
        print(f"❌ Directory not found: {processed_dir}")
        return

    clip_dirs = sorted([d for d in processed_dir.iterdir() if d.is_dir()])
    if not clip_dirs:
        print("⚠️ No clip folders found in processed/")
        return

    for clip_dir in clip_dirs:
        clip_name = clip_dir.name
        print(f"\n📂 Processing: {clip_name}")

        # Check question.json
        question_path = clip_dir / 'question.json'
        if not question_path.exists():
            print("   ⚠️ question.json missing — skipping")
            continue

        with open(question_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Skip if already uploaded (idempotent)
        if data.get('audio_url') is not None:
            print("   ✅ Already uploaded — skipping")
            continue

        # Determine next Firestore document ID
        next_id = get_next_firestore_id(db)
        print(f"   🆔 Assigned document ID: {next_id}")

        # Convert variation.wav → /tmp/{clip_name}.mp3
        wav_path = clip_dir / 'variation.wav'
        if not wav_path.exists():
            print("   ❌ variation.wav missing — skipping")
            continue

        mp3_path = Path(tempfile.gettempdir()) / f"{clip_name}.mp3"
        print(f"   🔄 Converting {wav_path.name} → {mp3_path.name} ...")
        try:
            convert_wav_to_mp3(wav_path, mp3_path)
        except RuntimeError as e:
            print(f"   ❌ ffmpeg conversion failed: {e}")
            continue

        # Upload audio
        remote_audio = f"n5_listening/selectImage/{next_id}/audio.mp3"
        audio_url = upload_file(bucket, mp3_path, remote_audio)
        print("   ✅ Audio uploaded")

        # Delete temp mp3
        mp3_path.unlink(missing_ok=True)

        # Upload image (compressed)
        image_path = clip_dir / 'image.png'
        if not image_path.exists():
            print("   ❌ image.png missing — Firestore save skipped")
            continue

        compressed_path = compress_image(image_path)
        try:
            remote_image = f"n5_listening/selectImage/{next_id}/image.png"
            image_url = upload_file(bucket, compressed_path, remote_image)
            print("   ✅ Image uploaded")
        finally:
            compressed_path.unlink(missing_ok=True)

        # Update question.json with URLs
        data['audio_url'] = audio_url
        data['image_url'] = image_url

        with open(question_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("   ✅ question.json updated locally")

        # Save to Firestore
        doc_ref = db.collection('n5_listening_select_image_questions').document(next_id)
        doc_ref.set(data)
        print("   ✅ Firestore saved")


def main():
    parser = argparse.ArgumentParser(description='Upload YouTube listening variation questions to Firebase')
    parser.add_argument('--bucket', help='Firebase Storage bucket name (e.g. your-project.firebasestorage.app)')
    args = parser.parse_args()

    # processed/ is at backend/listening/data/selectImage/listening-youtube-data/processed/
    script_dir = Path(__file__).parent
    processed_dir = script_dir.parent / 'data' / 'selectImage' / 'listening-youtube-data' / 'processed'

    initialize_firebase(args.bucket)

    db = firestore.client()
    bucket = storage.bucket()
    print(f"Using storage bucket: {bucket.name}")

    process_youtube_variations(db, bucket, processed_dir)
    print("\n🎉 All Done!")


if __name__ == "__main__":
    main()

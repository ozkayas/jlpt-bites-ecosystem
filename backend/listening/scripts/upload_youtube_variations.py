import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import argparse

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
            print(f"⚠️ Failed to load service-account-key.json: {e}")

    firebase_admin.initialize_app(options=options)
    print("✅ Firebase Admin SDK initialized (Default)")

def upload_file(bucket, local_path, remote_path):
    print(f"   ⬆️ Uploading {Path(local_path).name} to {remote_path}...")
    blob = bucket.blob(remote_path)
    # Cache-control can be set to 0 during development to see changes immediately
    blob.cache_control = 'no-cache'
    blob.upload_from_filename(str(local_path))
    blob.make_public()
    return blob.public_url

def get_existing_doc_id(db, clip_name):
    """Find existing doc ID for this clip to avoid duplicates."""
    docs = db.collection('n5_listening_select_image_questions').where('source_clip', '==', clip_name).get()
    if docs:
        return docs[0].id
    return None

def get_next_firestore_id(db):
    """Return next sequential ID."""
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

def convert_wav_to_mp3(wav_path, mp3_path):
    """Convert WAV to MP3."""
    subprocess.run(
        ['ffmpeg', '-y', '-i', str(wav_path), '-codec:a', 'libmp3lame', '-qscale:a', '2', str(mp3_path)],
        capture_output=True
    )

def process_youtube_variations(db, bucket, processed_dir, clip_filter=None):
    clip_dirs = sorted([d for d in processed_dir.iterdir() if d.is_dir()])
    
    if clip_filter:
        clip_dirs = [d for d in clip_dirs if d.name == clip_filter]
        if not clip_dirs:
            print(f"❌ Clip folder '{clip_filter}' not found in processed directory.")
            return

    for clip_dir in clip_dirs:
        clip_name = clip_dir.name
        print(f"\n📂 Processing: {clip_name}")

        question_path = clip_dir / 'question.json'
        if not question_path.exists():
            print("   ⚠️ question.json missing — skipping")
            continue

        with open(question_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Determine ID
        doc_id = get_existing_doc_id(db, clip_name)
        if doc_id:
            print(f"   🆔 Existing document found: {doc_id} (Will Update)")
        else:
            doc_id = get_next_firestore_id(db)
            print(f"   🆔 New ID assigned: {doc_id}")

        data['source_clip'] = clip_name

        # 2. Handle Audio
        audio_url = data.get('audio_url')
        wav_path = clip_dir / 'variation.wav'
        if not wav_path.exists():
            wav_path = clip_dir / 'variation-audio.wav'
        
        if wav_path.exists():
            mp3_path = Path(tempfile.gettempdir()) / f"{clip_name}.mp3"
            convert_wav_to_mp3(wav_path, mp3_path)
            remote_audio = f"n5_listening/selectImage/{doc_id}/audio.mp3"
            audio_url = upload_file(bucket, mp3_path, remote_audio)
            mp3_path.unlink(missing_ok=True)
            print("   ✅ Audio updated")
        elif audio_url:
            print("   ℹ️ Local audio missing, keeping existing URL")
        
        # 3. Handle Image
        image_url = data.get('image_url')
        img_p = clip_dir / 'image.webp'
        if not img_p.exists():
            img_p = clip_dir / 'image.png'
        
        if img_p.exists():
            remote_img = f"n5_listening/selectImage/{doc_id}/{img_p.name}"
            image_url = upload_file(bucket, img_p, remote_img)
            print("   ✅ Image updated")
        elif image_url:
            print("   ℹ️ Local image missing, keeping existing URL")

        # 4. Save
        data['audio_url'] = audio_url
        data['image_url'] = image_url

        with open(question_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        db.collection('n5_listening_select_image_questions').document(doc_id).set(data)
        print(f"   ✅ Firestore document {doc_id} synchronized")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', default='jlpt-bites.firebasestorage.app')
    parser.add_argument('--clip', help='Specific clip folder name to process (optional)')
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    processed_dir = script_dir.parent / 'data' / 'selectImage' / 'listening-youtube-data' / 'processed'

    initialize_firebase(args.bucket)
    process_youtube_variations(firestore.client(), storage.bucket(), processed_dir, clip_filter=args.clip)
    print("\n🎉 Done!")

if __name__ == "__main__":
    main()

import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
import os
import sys
from pathlib import Path
import argparse

def initialize_firebase(bucket_name=None):
    """Initialize Firebase Admin SDK"""
    # Use shared service account key from firestore root
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent / 'service-account-key.json'
    
    options = {}
    if bucket_name:
        options['storageBucket'] = bucket_name
    
    # Try service account key first
    if key_path.exists():
        try:
            cred = credentials.Certificate(str(key_path))
            firebase_admin.initialize_app(cred, options)
            print("✅ Firebase Admin SDK initialized (using service-account-key.json)")
            return
        except Exception as e:
            print(f"⚠️ Found service-account-key.json but failed to load: {e}")
    
    # Fallback to Application Default Credentials
    try:
        print("⚠️ service-account-key.json not found. Attempting to use Application Default Credentials...")
        firebase_admin.initialize_app(options=options)
        print("✅ Firebase Admin SDK initialized (using ADC)")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print(f"   Please place 'service-account-key.json' in {script_dir}")
        print("   OR ensure you have Google Application Default Credentials set up.")
        sys.exit(1)

def upload_file(bucket, local_path, remote_path):
    print(f"   ⬆️ Uploading {local_path.name} to {remote_path}...")
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(str(local_path))
    blob.make_public()
    return blob.public_url

def process_select_audio_folders(db, bucket, base_dir):
    select_audio_dir = base_dir / 'data' / 'selectAudio'
    if not select_audio_dir.exists():
        print(f"❌ Directory not found: {select_audio_dir}")
        return

    # Iterate over question folders (e.g., 001, 002)
    for question_dir in sorted(select_audio_dir.iterdir()):
        if not question_dir.is_dir():
            continue
            
        question_id = question_dir.name
        print(f"\n📂 Processing select audio question: {question_id}")
        
        json_path = question_dir / 'question_data.json'
        if not json_path.exists():
            print(f"   ⚠️ question_data.json missing in {question_dir}")
            continue
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 1. Upload Audio
        audio_path = question_dir / 'audio.mp3'
        if audio_path.exists():
            remote_audio_path = f"listening/selectAudio/{question_id}/audio.mp3"
            audio_url = upload_file(bucket, audio_path, remote_audio_path)
            data['metadata']['audio_url'] = audio_url
            print(f"   ✅ Audio URL updated")
        else:
            print(f"   ⚠️ audio.mp3 missing")

        # 2. Upload Image (if exists)
        image_path = question_dir / 'image.png'
        if image_path.exists():
            remote_image_path = f"listening/selectAudio/{question_id}/image.png"
            image_url = upload_file(bucket, image_path, remote_image_path)
            data['image'] = image_url
            print(f"   ✅ Image URL updated")
        else:
            print(f"   ℹ️ No image.png found (optional)")
            data['image'] = None

        # 3. Update JSON locally
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("   ✅ question_data.json updated locally")

        # 4. Upload Data to Firestore
        # Collection: listening_select_audio_questions
        doc_ref = db.collection('listening_select_audio_questions').document(question_id)
        doc_ref.set(data)
        print("   ✅ Data saved to Firestore")

def main():
    parser = argparse.ArgumentParser(description='Upload Listening Select Audio Questions')
    parser.add_argument('--bucket', help='Firebase Storage Bucket Name (e.g. your-project.appspot.com)')
    args = parser.parse_args()

    # Determine base path (../..) relative to script location
    base_dir = Path(__file__).parent.parent 
    
    initialize_firebase(args.bucket)
    
    db = firestore.client()
    bucket = storage.bucket()
    print(f"Using storage bucket: {bucket.name}")
    
    process_select_audio_folders(db, bucket, base_dir)
    print("\n🎉 All Done!")

if __name__ == "__main__":
    main()

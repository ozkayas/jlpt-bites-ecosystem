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
        # Note: For ADC and Storage to work together without a key, 
        # the bucket name usually needs to be explicit or the project config inferred correctly.
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

def process_select_image_folders(db, bucket, base_dir):
    select_image_dir = base_dir / 'data' / 'selectImage'
    if not select_image_dir.exists():
        print(f"❌ Directory not found: {select_image_dir}")
        return

    # Iterate over question folders (e.g., 001, 002)
    for question_dir in sorted(select_image_dir.iterdir()):
        if not question_dir.is_dir():
            continue
            
        question_id = question_dir.name
        print(f"\n📂 Processing select image question: {question_id}")
        
        json_path = question_dir / 'question_data.json'
        if not json_path.exists():
            print(f"   ⚠️ question_data.json missing in {question_dir}")
            continue
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 1. Upload Audio
        audio_path = question_dir / 'audio.mp3'
        if audio_path.exists():
            remote_audio_path = f"n5_listening/selectImage/{question_id}/audio.mp3"
            audio_url = upload_file(bucket, audio_path, remote_audio_path)
            data['metadata']['audio_url'] = audio_url
            print(f"   ✅ Audio URL updated")
        else:
            print(f"   ⚠️ audio.mp3 missing")

        # 2. Upload Images (1.png, 2.png, 3.png, 4.png)
        images_dir = question_dir / 'images'
        if images_dir.exists():
            options = data.get('options', [None, None, None, None])
            # Ensure options list has 4 slots
            while len(options) < 4:
                options.append(None)
                
            for i in range(1, 5): # 1 to 4
                img_name = f"{i}.png"
                img_path = images_dir / img_name
                if img_path.exists():
                    remote_img_path = f"n5_listening/selectImage/{question_id}/images/{img_name}"
                    img_url = upload_file(bucket, img_path, remote_img_path)
                    # Index 0 corresponds to 1.png
                    options[i-1] = img_url
                    print(f"   ✅ Image {i} URL updated")
                else:
                    print(f"   ⚠️ Image {img_name} missing")
            
            data['options'] = options
        else:
            print("   ⚠️ images directory missing")

        # 3. Update JSON locally
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("   ✅ question_data.json updated locally")

        # 4. Upload Data to Firestore
        # Collection: n5_listening_select_image_questions
        # Using ID from folder name
        doc_ref = db.collection('n5_listening_select_image_questions').document(question_id)
        doc_ref.set(data)
        print("   ✅ Data saved to Firestore")

def main():
    parser = argparse.ArgumentParser(description='Upload Listening Select Image Questions')
    parser.add_argument('--bucket', help='Firebase Storage Bucket Name (e.g. your-project.appspot.com)')
    args = parser.parse_args()

    # Determine base path (../..) relative to script location
    # script at firestore/listening/scripts/upload_questions.py
    # data at firestore/listening/data
    base_dir = Path(__file__).parent.parent 
    
    initialize_firebase(args.bucket)
    
    db = firestore.client()
    bucket = storage.bucket()
    print(f"Using storage bucket: {bucket.name}")
    
    process_select_image_folders(db, bucket, base_dir)
    print("\n🎉 All Done!")

if __name__ == "__main__":
    main()

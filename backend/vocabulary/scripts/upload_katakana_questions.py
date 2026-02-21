import firebase_admin
from firebase_admin import credentials, firestore
import json
import sys
from pathlib import Path

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    script_dir = Path(__file__).parent
    # Use shared service account key from firestore root
    key_path = script_dir.parent.parent / 'service-account-key.json'
    
    # Also check in the parent firestore directory shared key if local one is missing
    # (Just a fallback assumption, strict check is safer)
    
    if key_path.exists():
        try:
            cred = credentials.Certificate(str(key_path))
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized (using service-account-key.json)")
            return
        except Exception as e:
            print(f"⚠️ Found service-account-key.json but failed to load: {e}")
    
    # Fallback to Application Default Credentials
    try:
        print("⚠️ service-account-key.json not found in script dir. Attempting to use Application Default Credentials...")
        firebase_admin.initialize_app()
        print("✅ Firebase Admin SDK initialized (using ADC)")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print(f"   Please place 'service-account-key.json' in {script_dir}")
        print("   OR ensure you have Google Application Default Credentials set up.")
        sys.exit(1)

def upload_data(db):
    # Path to data.json: ../data/data.json relative to this script
    data_path = Path(__file__).parent.parent / 'data' / 'data.json'
    
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        return

    print(f"📖 Reading data from {data_path}...")
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read JSON file: {e}")
        return

    # Validate data structure roughly
    if 'questions' not in data:
        print("⚠️ Warning: JSON does not contain 'questions' key. Is this correct?")
    
    # Upload to Firestore
    # Collection: katakana_identification
    # Document: n5_v1
    collection_name = 'katakana_identification'
    document_id = 'n5_v1'
    
    print(f"⬆️ Uploading data to Firestore: {collection_name}/{document_id}...")
    
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc_ref.set(data)
        print(f"✅ Data successfully uploaded to {collection_name}/{document_id}!")
        print(f"   Uploaded {len(data.get('questions', []))} questions.")
    except Exception as e:
        print(f"❌ Failed to upload data: {e}")

def main():
    initialize_firebase()
    db = firestore.client()
    upload_data(db)

if __name__ == "__main__":
    main()

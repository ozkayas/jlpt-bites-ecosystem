#!/usr/bin/env python3
"""
Cleanup script for JLPT N5 kanji list in Firebase.
Deletes all documents from the 'n5_kanji_list' collection.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import sys
from pathlib import Path

COLLECTION_NAME = 'n5_kanji_list'

def initialize_firebase():
    """Initialize Firebase Admin SDK using shared service-account-key.json"""
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent.parent / 'service-account-key.json'

    if not key_path.exists():
        print(f"❌ service-account-key.json not found at: {key_path}")
        return False

    try:
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        return False

def delete_collection(db, collection_name, batch_size=400):
    """Delete all documents in a collection in batches."""
    collection_ref = db.collection(collection_name)
    docs = collection_ref.limit(batch_size).stream()
    deleted = 0

    batch = db.batch()
    for doc in docs:
        batch.delete(doc.reference)
        deleted += 1

    if deleted > 0:
        batch.commit()
        print(f"  ✓ Deleted {deleted} document(s) from '{collection_name}'")
        # Recursive call to delete next batch
        return deleted + delete_collection(db, collection_name, batch_size)
    else:
        return 0

def main():
    print("=" * 60)
    print(f"  Cleanup: Firestore Collection '{COLLECTION_NAME}'")
    print("=" * 60)

    if not initialize_firebase():
        sys.exit(1)

    db = firestore.client()

    print(f"\n🗑️  Cleaning up all documents in '{COLLECTION_NAME}'...")
    total_deleted = delete_collection(db, COLLECTION_NAME)

    if total_deleted > 0:
        print(f"✅ Cleanup complete: Total {total_deleted} document(s) deleted.")
    else:
        print(f"ℹ️  No documents found in '{COLLECTION_NAME}' to delete.")

    print("=" * 60)

if __name__ == '__main__':
    main()

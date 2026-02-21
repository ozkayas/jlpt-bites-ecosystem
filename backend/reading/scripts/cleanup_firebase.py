#!/usr/bin/env python3
"""
Cleanup script for reading passages in Firebase.
Deletes all passages from reading_contents/{level}_reading/passages/ collection.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import sys

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    script_dir = Path(__file__).parent
    key_path = script_dir.parent.parent / 'service-account-key.json'

    try:
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        return False

def delete_passages(db, level: str):
    """Delete all passages for a given level"""
    collection_path = f'reading_contents/{level}_reading/passages'
    print(f"\n🗑️  Cleaning up {collection_path}...")

    passages_ref = db.collection(collection_path)
    docs = passages_ref.stream()

    passage_ids = [doc.id for doc in docs]

    if not passage_ids:
        print(f"  - No passages found to delete")
        return 0

    print(f"  Found {len(passage_ids)} passage(s) to delete:")
    for pid in passage_ids:
        print(f"    - {pid}")

    # Delete each passage and its subcollections
    batch = db.batch()
    batch_count = 0

    for passage_id in passage_ids:
        passage_ref = passages_ref.document(passage_id)

        # Delete subcollections: sentences, questions, translations
        for subcollection in ['sentences', 'questions']:
            docs = passage_ref.collection(subcollection).stream()
            for doc in docs:
                batch.delete(doc.reference)
                batch_count += 1

        # Delete translations subcollection
        trans_ref = passage_ref.collection('translations')
        for lang_doc in trans_ref.stream():
            lang_ref = lang_doc.reference
            # Delete sentence and question subcollections within each language
            for sub in ['sentences', 'questions']:
                for sub_doc in lang_ref.collection(sub).stream():
                    batch.delete(sub_doc.reference)
                    batch_count += 1
            # Delete the language document itself
            batch.delete(lang_ref)
            batch_count += 1

        # Delete the passage document itself
        batch.delete(passage_ref)
        batch_count += 1

        # Commit every 500 operations
        if batch_count >= 500:
            batch.commit()
            print(f"  ✓ Committed {batch_count} delete operations")
            batch = db.batch()
            batch_count = 0

    # Final commit
    if batch_count > 0:
        batch.commit()
        print(f"  ✓ Committed {batch_count} delete operations")

    print(f"✅ Deleted all passages from {collection_path}")

def main():
    if not initialize_firebase():
        sys.exit(1)

    db = firestore.client()

    # Clean N5 passages
    delete_passages(db, 'n5')

    print("\n✅ Firebase cleanup complete!")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Upload script for new separated passage structure.
Uploads core Japanese content and translations as separate subcollections.

New Firestore structure:
reading_contents/{level}_reading/passages/{passage_id}/
  - metadata fields (id, title, visual_type, etc.)
  - framed_sentences (array field)
  - sentences/ (subcollection - Japanese only)
  - questions/ (subcollection - Japanese only)  
  - translations/ (subcollection)
    - {lang}/
      - sentences/{sentence_id}/ (translation, mining_text)
      - questions/{question_id}/ (text, options)
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
import argparse
import uuid

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    # Use shared service account key from firestore root
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

PASSAGE_TYPES = ['short', 'mid']

def upload_core_passages(db, level: str) -> int:
    """
    Upload core Japanese content (sentences and questions subcollections).
    Reads from {level}_passages_{type}_core.json for each passage type.

    Returns:
        Number of passages uploaded
    """
    data_dir = Path(__file__).parent.parent / 'data'
    total_passages = []

    for ptype in PASSAGE_TYPES:
        data_path = data_dir / f'{level}_passages_{ptype}_core.json'
        if not data_path.exists():
            print(f"⚠️  Core file not found: {data_path.name}")
            continue
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        passages = data.get('passages', [])
        print(f"  → {data_path.name}: {len(passages)} passages")
        total_passages.extend(passages)

    passages = total_passages
    if not passages:
        print(f"ℹ️  No passages found for {level}")
        return 0

    try:
        collection_ref = db.collection('reading_contents').document(f'{level}_reading').collection('passages')

        batch = db.batch()
        count = 0
        BATCH_LIMIT = 400

        print(f"📚 Uploading {len(passages)} core passages for {level}...")
        
        for passage in passages:
            passage_id = passage.get('id')
            if not passage_id:
                passage_id = f"n5_passage_{uuid.uuid4()}"
                print(f"  Generated ID for passage: {passage_id}")
            
            doc_ref = collection_ref.document(passage_id)
            
            # 1. Main document metadata (with framed_sentences array)
            passage_data = {
                'id': passage_id,
                'title': passage['title'],
                'visual_type': passage.get('visual_type'),
                'framed_sentences': passage.get('framed_sentences', []),
                'sentence_count': len(passage.get('sentences', [])),
                'question_count': len(passage.get('questions', [])),
                'type': passage.get('type', 'short'),
                'created_at': passage.get('created_at', datetime.now(timezone.utc).isoformat())
            }
            batch.set(doc_ref, passage_data)
            count += 1
            
            # 2. Sentences subcollection (Japanese only)
            sentences = passage.get('sentences', [])
            for i, sentence in enumerate(sentences):
                sent_id = sentence.get('id', f"s{str(i+1).zfill(3)}")
                sentence_data = {
                    'id': sent_id,
                    'original': sentence['original'],
                    'furigana': sentence['furigana'],
                    'romaji': sentence.get('romaji'),
                    'order': i
                }
                sent_ref = doc_ref.collection('sentences').document(sent_id)
                batch.set(sent_ref, sentence_data)
                count += 1
            
            # 3. Questions subcollection (Japanese only)
            questions = passage.get('questions', [])
            for i, question in enumerate(questions):
                que_id = question.get('id', f"q{str(i+1).zfill(3)}")
                question_data = {
                    'id': que_id,
                    'text': question['text'],
                    'furigana': question.get('furigana'),
                    'romaji': question.get('romaji'),
                    'options': question.get('options', []),
                    'order': i
                }
                que_ref = doc_ref.collection('questions').document(que_id)
                batch.set(que_ref, question_data)
                count += 1
            
            # Commit batch if getting full
            if count >= BATCH_LIMIT:
                batch.commit()
                print(f"   ✓ Committed batch ({count} operations)")
                batch = db.batch()
                count = 0
        
        # Commit remaining operations
        if count > 0:
            batch.commit()
            print(f"   ✓ Committed final batch ({count} operations)")
        
        print(f"✅ Core content uploaded: {len(passages)} passages")
        return len(passages)
        
    except Exception as e:
        print(f"❌ Error uploading core passages: {e}")
        return 0

def upload_translations(db, level: str, language: str) -> int:
    """
    Upload translations for a specific language.
    Reads from {level}_passages_{type}_translations_{language}.json for each passage type.
    Creates translations/{lang}/sentences and translations/{lang}/questions subcollections.

    Returns:
        Number of passages with translations uploaded
    """
    data_dir = Path(__file__).parent.parent / 'data'
    total_passages = []

    for ptype in PASSAGE_TYPES:
        data_path = data_dir / f'{level}_passages_{ptype}_translations_{language}.json'
        if not data_path.exists():
            continue
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_passages.extend(data.get('passages', []))

    passages = total_passages
    if not passages:
        print(f"ℹ️  No translation passages found")
        return 0
    
    try:
        collection_ref = db.collection('reading_contents').document(f'{level}_reading').collection('passages')
        
        batch = db.batch()
        count = 0
        BATCH_LIMIT = 400
        
        print(f"🌐 Uploading {language.upper()} translations for {len(passages)} passages...")
        
        for passage in passages:
            passage_id = passage['id']
            doc_ref = collection_ref.document(passage_id)
            
            # Upload sentence translations
            sentences = passage.get('sentences', {})
            for sent_id, trans_data in sentences.items():
                trans_ref = doc_ref.collection('translations').document(language).collection('sentences').document(sent_id)
                trans_doc = {
                    'id': sent_id,
                    'translation': trans_data.get('translation', ''),
                    'mining_text': trans_data.get('mining_text', '')
                }
                batch.set(trans_ref, trans_doc)
                count += 1
                
                if count >= BATCH_LIMIT:
                    batch.commit()
                    batch = db.batch()
                    count = 0
            
            # Upload question translations
            questions = passage.get('questions', {})
            for que_id, trans_data in questions.items():
                trans_ref = doc_ref.collection('translations').document(language).collection('questions').document(que_id)
                trans_doc = {
                    'id': que_id,
                    'text': trans_data.get('text', ''),
                    'options': trans_data.get('options', {})
                }
                batch.set(trans_ref, trans_doc)
                count += 1
                
                if count >= BATCH_LIMIT:
                    batch.commit()
                    batch = db.batch()
                    count = 0
        
        # Commit remaining operations
        if count > 0:
            batch.commit()
        
        print(f"✅ {language.upper()} translations uploaded")
        return len(passages)
        
    except Exception as e:
        print(f"❌ Error uploading {language} translations: {e}")
        return 0

def update_timestamps(levels: list):
    """Update created_at timestamps in core JSON files"""
    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f"🕒 Updating timestamps to: {current_time} (timezone.utc)")
    
    for level in levels:
        data_path = Path(__file__).parent.parent / 'data' / f'{level}_passages_core.json'
        if not data_path.exists():
            continue
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            passages = data.get('passages', [])
            if not passages:
                continue
            
            for passage in passages:
                passage['created_at'] = current_time
            
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Updated {level}_passages_core.json")
            
        except Exception as e:
            print(f"⚠️ Error updating {level}_passages_core.json: {e}")

def main():
    """Main upload process"""
    parser = argparse.ArgumentParser(
        description='Upload separated passage data to Firestore with new structure.'
    )
    parser.add_argument(
        'level',
        nargs='?',
        help='JLPT level to upload (n1, n2, n3, n4, n5). If omitted, uploads all.'
    )
    parser.add_argument(
        '--languages',
        nargs='+',
        default=['en', 'tr', 'de', 'fr', 'es'],
        help='Languages to upload (default: all)'
    )
    parser.add_argument(
        '--core-only',
        action='store_true',
        help='Upload only core content, skip translations'
    )
    parser.add_argument(
        '--translations-only',
        action='store_true',
        help='Upload only translations, skip core content'
    )
    
    args = parser.parse_args()
    
    all_levels = ['n5', 'n4', 'n3', 'n2', 'n1']
    
    if args.level:
        level_input = args.level.lower()
        if level_input not in all_levels:
            print(f"❌ Invalid level '{args.level}'. Supported: {', '.join(all_levels)}")
            sys.exit(1)
        levels = [level_input]
        print(f"🎯 Target level: {level_input.upper()}")
    else:
        levels = all_levels
        print("🎯 Target: ALL levels")
    
    print(f"🌍 Languages: {', '.join(args.languages)}\n")
    
    # Update timestamps
    if not args.translations_only:
        update_timestamps(levels)
        print()
    
    # Initialize Firebase
    if not initialize_firebase():
        sys.exit(1)
    
    db = firestore.client()
    
    total_core = 0
    total_translations = 0
    
    try:
        for level in levels:
            print(f"\n{'='*60}")
            print(f"Processing {level.upper()}")
            print('='*60)
            
            # Upload core content
            if not args.translations_only:
                count = upload_core_passages(db, level)
                total_core += count
            
            # Upload translations
            if not args.core_only:
                for lang in args.languages:
                    count = upload_translations(db, level, lang)
                    if count > 0:
                        total_translations += count
        
        print(f"\n{'='*60}")
        print("🎉 Upload Complete!")
        if not args.translations_only:
            print(f"   Core passages: {total_core}")
        if not args.core_only:
            print(f"   Translation sets: {total_translations}")
        print('='*60)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n💥 Upload failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

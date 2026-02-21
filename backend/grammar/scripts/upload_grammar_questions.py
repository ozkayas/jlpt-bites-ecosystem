#!/usr/bin/env python3
"""
Upload script for grammar questions to Firestore.

Firestore structure:
grammar_questions/{question_id}/
  - id: string (UUID)
  - level: string (n5, n4, n3, n2, n1)
  - type: string (sentenceCompletion, starQuestion, textFlow)
  - correctAnswer: number
  - ... (type-specific fields)
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
import argparse

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

def upload_questions(db, level: str, question_type: str) -> int:
    """
    Upload grammar questions of a specific type.
    
    Args:
        db: Firestore client
        level: JLPT level (n5, n4, etc.)
        question_type: mondai1, mondai2, or mondai3
    
    Returns:
        Number of questions uploaded
    """
    # Map question type to file name
    file_map = {
        'essential-grammar': f'{level}_essential_grammar.json',
        'sentence-building': f'{level}_sentence_building.json',
        'text-integration': f'{level}_text_integration.json'
    }
    
    data_path = Path(__file__).parent.parent / 'data' / file_map[question_type]
    
    if not data_path.exists():
        print(f"⚠️  File not found: {data_path}")
        return 0
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    if not questions:
        print(f"ℹ️  No questions found in {file_map[question_type]}")
        return 0
    
    try:
        collection_ref = db.collection('grammar_questions')
        
        batch = db.batch()
        count = 0
        BATCH_LIMIT = 400
        
        print(f"📚 Uploading {len(questions)} {question_type} questions for {level}...")
        
        for question in questions:
            question_id = question.get('id')
            if not question_id:
                print(f"  ⚠️ Skipping question without ID")
                continue
            
            doc_ref = collection_ref.document(question_id)
            
            # Add timestamp
            question_data = question.copy()
            question_data['uploaded_at'] = datetime.now(timezone.utc).isoformat()
            
            batch.set(doc_ref, question_data)
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
        
        print(f"✅ {question_type.upper()} uploaded: {len(questions)} questions")
        return len(questions)
        
    except Exception as e:
        print(f"❌ Error uploading {question_type}: {e}")
        return 0

def delete_existing_questions(db, level: str, question_type: str):
    """Delete existing questions of a specific level and type from Firestore."""
    # Map CLI type to Firestore type
    type_map = {
        'essential-grammar': 'sentenceCompletion',
        'sentence-building': 'starQuestion',
        'text-integration': 'textFlow'
    }
    
    fs_type = type_map.get(question_type)
    if not fs_type:
        return

    print(f"🗑️  Deleting existing {fs_type} questions for {level}...")
    
    collection_ref = db.collection('grammar_questions')
    # Query for documents matching level AND type
    docs = collection_ref.where('level', '==', level).where('type', '==', fs_type).stream()
    
    batch = db.batch()
    count = 0
    BATCH_LIMIT = 400
    
    for doc in docs:
        batch.delete(doc.reference)
        count += 1
        if count >= BATCH_LIMIT:
            batch.commit()
            batch = db.batch()
            count = 0
            
    if count > 0:
        batch.commit()
    
    print(f"   ✓ Deleted {count} documents")

def main():
    """Main upload process"""
    parser = argparse.ArgumentParser(
        description='Upload grammar questions to Firestore.'
    )
    parser.add_argument(
        'level',
        nargs='?',
        help='JLPT level to upload (n1, n2, n3, n4, n5). If omitted, uploads all.'
    )
    parser.add_argument(
        '--type',
        choices=['essential-grammar', 'sentence-building', 'text-integration', 'all'],
        default='all',
        help='Question type to upload (default: all)'
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete existing questions for the level/type before uploading'
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
    
    # Determine question types to upload
    if args.type == 'all':
        question_types = ['essential-grammar', 'sentence-building', 'text-integration']
    else:
        question_types = [args.type]
    
    print(f"📝 Question types: {', '.join(question_types)}\n")
    
    # Initialize Firebase
    if not initialize_firebase():
        sys.exit(1)
    
    db = firestore.client()
    
    total_uploaded = 0
    
    try:
        for level in levels:
            print(f"\n{'='*60}")
            print(f"Processing {level.upper()}")
            print('='*60)
            
            for q_type in question_types:
                if args.delete:
                    delete_existing_questions(db, level, q_type)
                count = upload_questions(db, level, q_type)
                total_uploaded += count
        
        print(f"\n{'='*60}")
        print("🎉 Upload Complete!")
        print(f"   Total questions uploaded: {total_uploaded}")
        print('='*60)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n💥 Upload failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

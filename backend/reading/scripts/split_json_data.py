#!/usr/bin/env python3
"""
Script to split monolithic n5_passages.json into separate files:
- Core file with Japanese content only
- Individual translation files per language

This enables more efficient data transfer and better scalability.
"""

import json
from pathlib import Path
import sys
from typing import Dict, List, Any

# Supported languages
LANGUAGES = ['en', 'tr', 'de', 'fr', 'es']

def split_passage_data(passage: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Split a passage into core Japanese content and translations.
    
    Returns:
        (core_passage, translations_by_lang)
        
        core_passage: passage with only Japanese content (no analysis/translations)
        translations_by_lang: {lang: [sentence_trans, question_trans]}
    """
    # 1. Create core passage with metadata and Japanese-only content
    core_passage = {
        'id': passage['id'],
        'title': passage['title'],
        'visual_type': passage.get('visual_type'),
        'question_count': passage.get('question_count', 0),
        'created_at': passage.get('created_at'),
        'sentences': [],
        'framed_sentences': [],
        'questions': []
    }
    
    # 2. Extract translations by language
    translations_by_lang: Dict[str, Any] = {lang: {'sentences': {}, 'questions': {}} for lang in LANGUAGES}
    
    # 3. Process sentences - separate Japanese from translations
    for sentence in passage.get('sentences', []):
        # Core Japanese content
        core_sentence = {
            'id': sentence['id'],
            'original': sentence['original'],
            'furigana': sentence['furigana'],
            'romaji': sentence.get('romaji')
        }
        core_passage['sentences'].append(core_sentence)
        
        # Extract translations
        analysis = sentence.get('analysis', {})
        for lang in LANGUAGES:
            if lang in analysis:
                translations_by_lang[lang]['sentences'][sentence['id']] = {
                    'translation': analysis[lang].get('translation', ''),
                    'mining_text': analysis[lang].get('mining_text', '')
                }
    
    # 4. Process framed_sentences similarly
    for sentence in passage.get('framed_sentences', []):
        core_sentence = {
            'id': sentence['id'],
            'original': sentence['original'],
            'furigana': sentence['furigana'],
            'romaji': sentence.get('romaji')
        }
        core_passage['framed_sentences'].append(core_sentence)
        
        # Extract translations for framed sentences
        analysis = sentence.get('analysis', {})
        for lang in LANGUAGES:
            if lang in analysis:
                translations_by_lang[lang]['sentences'][sentence['id']] = {
                    'translation': analysis[lang].get('translation', ''),
                    'mining_text': analysis[lang].get('mining_text', '')
                }
    
    # 5. Process questions - separate Japanese from translations
    for question in passage.get('questions', []):
        # Core Japanese content
        core_question = {
            'id': question['id'],
            'text': question['text'],
            'furigana': question.get('furigana'),
            'romaji': question.get('romaji'),
            'options': []
        }
        
        # Process options
        question_translations = {lang: {'text': '', 'options': {}} for lang in LANGUAGES}
        
        for option in question.get('options', []):
            core_option = {
                'id': option['id'],
                'text': option['text'],
                'furigana': option.get('furigana'),
                'is_correct': option['is_correct'],
                'romaji': option.get('romaji')
            }
            core_question['options'].append(core_option)
            
            # Extract option translations
            opt_translations = option.get('translations', {})
            for lang in LANGUAGES:
                if lang in opt_translations:
                    question_translations[lang]['options'][option['id']] = opt_translations[lang]
        
        core_passage['questions'].append(core_question)
        
        # Extract question text translations
        q_translations = question.get('translations', {})
        for lang in LANGUAGES:
            if lang in q_translations:
                question_translations[lang]['text'] = q_translations[lang]
            
            # Store question translations
            if question_translations[lang]['text'] or question_translations[lang]['options']:
                translations_by_lang[lang]['questions'][question['id']] = question_translations[lang]
    
    return core_passage, translations_by_lang


def split_json_file(level: str) -> bool:
    """
    Split a level's passages.json file into core + translation files.
    
    Args:
        level: JLPT level (e.g., 'n5', 'n4', etc.)
        
    Returns:
        True if successful, False otherwise
    """
    data_dir = Path(__file__).parent.parent / 'data'
    input_file = data_dir / f'{level}_passages.json'
    
    if not input_file.exists():
        print(f"⚠️  Input file not found: {input_file}")
        return False
    
    print(f"📖 Reading {input_file.name}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read {input_file.name}: {e}")
        return False
    
    passages = data.get('passages', [])
    if not passages:
        print(f"⚠️  No passages found in {input_file.name}")
        return False
    
    print(f"✅ Found {len(passages)} passages")
    
    # Initialize output structures
    core_data = {'passages': []}
    translations_data = {lang: {'passages': []} for lang in LANGUAGES}
    
    # Process each passage
    for passage in passages:
        core_passage, translations_by_lang = split_passage_data(passage)
        core_data['passages'].append(core_passage)
        
        for lang in LANGUAGES:
            passage_translation = {
                'id': passage['id'],
                'sentences': translations_by_lang[lang]['sentences'],
                'questions': translations_by_lang[lang]['questions']
            }
            translations_data[lang]['passages'].append(passage_translation)
    
    # Write core file
    core_file = data_dir / f'{level}_passages_core.json'
    print(f"💾 Writing core file: {core_file.name}...")
    try:
        with open(core_file, 'w', encoding='utf-8') as f:
            json.dump(core_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Core file created: {core_file.name}")
    except Exception as e:
        print(f"❌ Failed to write core file: {e}")
        return False
    
    # Write translation files
    for lang in LANGUAGES:
        trans_file = data_dir / f'{level}_passages_translations_{lang}.json'
        print(f"💾 Writing translation file: {trans_file.name}...")
        try:
            with open(trans_file, 'w', encoding='utf-8') as f:
                json.dump(translations_data[lang], f, ensure_ascii=False, indent=2)
            print(f"✅ Translation file created: {trans_file.name}")
        except Exception as e:
            print(f"❌ Failed to write translation file for {lang}: {e}")
            return False
    
    # Calculate and report size reduction
    import os
    original_size = os.path.getsize(input_file)
    core_size = os.path.getsize(core_file)
    one_lang_size = core_size + os.path.getsize(data_dir / f'{level}_passages_translations_en.json')
    
    print(f"\n📊 Size Analysis:")
    print(f"   Original file: {original_size:,} bytes")
    print(f"   Core only: {core_size:,} bytes ({core_size/original_size*100:.1f}%)")
    print(f"   Core + 1 language: {one_lang_size:,} bytes ({one_lang_size/original_size*100:.1f}%)")
    print(f"   Reduction: {original_size - one_lang_size:,} bytes ({(1-one_lang_size/original_size)*100:.1f}% smaller)")
    
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Split passage JSON files into core and translation files.')
    parser.add_argument('level', nargs='?', help='JLPT level to process (n1, n2, n3, n4, n5). If omitted, processes all.')
    args = parser.parse_args()
    
    all_levels = ['n5', 'n4', 'n3', 'n2', 'n1']
    
    if args.level:
        level_input = args.level.lower()
        if level_input not in all_levels:
            print(f"❌ Error: Invalid level '{args.level}'. Supported levels: {', '.join(all_levels)}")
            sys.exit(1)
        levels = [level_input]
        print(f"🎯 Processing level: {level_input.upper()}\n")
    else:
        levels = all_levels
        print(f"🎯 Processing ALL levels\n")
    
    success_count = 0
    for level in levels:
        print(f"\n{'='*60}")
        print(f"Processing {level.upper()}")
        print('='*60)
        if split_json_file(level):
            success_count += 1
        print()
    
    print(f"\n{'='*60}")
    print(f"✅ Completed: {success_count}/{len(levels)} levels processed successfully")
    print('='*60)
    
    sys.exit(0 if success_count == len(levels) else 1)


if __name__ == '__main__':
    main()

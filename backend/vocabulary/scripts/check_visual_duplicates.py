import json
from collections import Counter
import sys

def check_and_fix_visual_duplicates(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    questions = data.get('questions', [])
    updated_count = 0

    print(f"Scanning {len(questions)} questions for visually confusing options...\n")

    # Mapping of characters that are visually very dangerously similar for N5
    # The key is the 'unsafe' usage (often intended as a tricky distractor but maybe too tricky)
    # The value is a 'normalized' form for checking.
    # But better logic is: if an option contains one char, and another option contains the confused char
    # AND the rest is identical, FLAGG IT.
    
    # Confusing pairs:
    # Katakana 'ー' (long vowel) vs Kanji '一' (one)
    # Katakana 'ソ' (so) vs 'ン' (n)
    # Katakana 'シ' (shi) vs 'ツ' (tsu)
    # Katakana 'ロ' (ro) vs Kanji '口' (mouth)
    # Katakana 'カ' (ka) vs Kanji '力' (power)
    # Katakana 'ニ' (ni) vs Kanji '二' (two)
    # Katakana 'タ' (ta) vs Kanji '夕' (evening)
    # Katakana 'ト' (to) vs Kanji '卜' (divination)

    confusing_pairs = [
        ('ー', '一'),
        ('ソ', 'ン'),
        ('シ', 'ツ'),
        ('ロ', '口'),
        ('カ', '力'),
        ('ニ', '二'),
        ('タ', '夕'),
        ('ト', '卜'),
        ('ベ', 'ペ'), # Be vs Pe (small circle vs dots hard to see sometimes?)
    ]
    
    # Specific logic for "ー" vs "一" which is the user complaint.
    # If any option has "一" (Kanji One) and another has "ー" (Long vowel) 
    # it's likely too hard.
    
    def is_visually_too_similar(opt1, opt2):
        # Check specifically for the long vowel / ichi issue first as requested
        if 'ー' in opt1 and '一' in opt2:
            trans = opt2.replace('一', 'ー')
            if trans == opt1: return True
        if '一' in opt1 and 'ー' in opt2:
            trans = opt1.replace('一', 'ー')
            if trans == opt2: return True
            
        # We can extend this logic to other pairs if needed, but let's stick to the user's main point
        # about "ichi and long vowel" being indistinguishable.
        return False

    for q in questions:
        options = q.get('options', [])
        original_options = list(options)
        modified = False
        
        # Check all pairs
        for i in range(len(options)):
            for j in range(len(options)):
                if i == j: continue
                
                opt1 = options[i]
                opt2 = options[j]
                
                if is_visually_too_similar(opt1, opt2):
                    print(f"⚠️  Question ID: {q.get('id')} has confusing options!")
                    print(f"   Sentence: {q.get('sentence')}")
                    print(f"   Conflict: '{opt1}' vs '{opt2}'")
                    
                    # Fix: Replace the one with the Kanji 'One' (assumed to be the distractor)
                    # We assume indices 1, 2, 3 are distractors usually (index 0 implies correct in our prompt gen usually?)
                    # but let's just target the one with '一'
                    
                    target_idx = -1
                    if '一' in opt1: target_idx = i
                    elif '一' in opt2: target_idx = j
                    
                    if target_idx != -1:
                        bad_opt = options[target_idx]
                        # Create a safer replacement
                        # Replace '一' with something clearly different like 'イ' or 'ア' or change the char entirely
                        # Heuristic: Change the char with '一' to 'イ' (visual hint but distinct) or 'リ'
                        
                        # Better approach: Modify the character completely to be a valid katakana distractor
                        # e.g. ノ一ト -> ヌート (Nu-to)
                        
                        replacements_map = {
                            "ノ一ト": "ヌート", # Nu-to
                            "カレ一": "カレーー", # Curry-y?
                            "コ一ヒ一": "コーヒ", # Coffe
                        }
                        
                        new_val = replacements_map.get(bad_opt)
                        if not new_val:
                            # Generic fallback: replace 一 with イ
                            new_val = bad_opt.replace('一', 'イ')
                        
                        print(f"   🛠️  Replacing confusing '{bad_opt}' with '{new_val}'")
                        options[target_idx] = new_val
                        modified = True

        if modified:
            q['options'] = options
            updated_count += 1
            print(f"   ✅ Fixed Options: {q['options']}\n")

    if updated_count > 0:
        print(f"Fixed {updated_count} questions.")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Saved changes to {file_path}")
    else:
        print("No visually confusing options (specifically 'ー' vs '一') found.")

if __name__ == "__main__":
    file_path = "firestore/vocabulary/data/data.json"
    check_and_fix_visual_duplicates(file_path)

import json
from collections import Counter
import sys

def check_and_fix_options(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    questions = data.get('questions', [])
    updated_count = 0

    print(f"Scanning {len(questions)} questions for duplicate options...\n")

    for q in questions:
        options = q.get('options', [])
        # Normalization for check (strip whitespace)
        normalized_options = [o.strip() for o in options]
        
        # Check for duplicates
        if len(set(normalized_options)) != len(normalized_options):
            print(f"⚠️  Question ID: {q.get('id')} has duplicate options!")
            print(f"   Sentence: {q.get('sentence')}")
            print(f"   Current Options: {options}")
            
            # Identify duplicates
            counts = Counter(normalized_options)
            duplicates = [item for item, count in counts.items() if count > 1]
            print(f"   Duplicates found: {duplicates}")

            # Prepare alternatives (manual mapping for now based on typical visual lookalikes)
            # This logic tries to find a replacement for the duplicate.
            # Since we need 4 unique options, we will keep the first occurrence and replace subsequent ones.
            
            seen = set()
            new_options = []
            for i, opt in enumerate(options):
                if opt in seen:
                    # Generate alternative
                    # Simple heuristic: modify the last char if it's Katakana, or replace duplicate
                    # For Q59 specifically (implied context of user request):
                    # "ノート", "ノト", "メート", "ノ一ト" -> if duplicate exists, replace it.
                    # Let's generate a fallback visual distractor if we don't have a specific map.
                    
                    # Common lookalikes map for replacement
                    replacements = {
                        "ノート": ["ノード", "ソート", "ノ一卜"],
                        "トイレ": ["トイし", "ドイレ", "トィレ", "トイL"],
                        "シャツ": ["シヤツ", "ジャツ", "シャッ", "シ+ツ"],
                         # Add more if needed generic fallback
                    }
                    
                    replacement_candidates = replacements.get(opt, [opt + "ー", opt[:-1] + "ア", "XX"])
                    
                    # Find a candidate that isn't already in the new_options or original set
                    chosen = None
                    for cand in replacement_candidates:
                        if cand not in seen and cand not in [o for o in options if options.index(o) != i]: 
                             chosen = cand
                             break
                    
                    if not chosen:
                        chosen = f"{opt}?" # Visual marker if we really can't find one, user must edit manual
                        
                    print(f"   🛠️  Replacing duplicate '{opt}' with '{chosen}'")
                    new_options.append(chosen)
                    seen.add(chosen)
                else:
                    new_options.append(opt)
                    seen.add(opt)
            
            q['options'] = new_options
            updated_count += 1
            print(f"   ✅ New Options: {q['options']}\n")

    if updated_count > 0:
        print(f"Fixed {updated_count} questions.")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Saved changes to {file_path}")
    else:
        print("No duplicate options found.")

if __name__ == "__main__":
    file_path = "firestore/vocabulary/data/data.json"
    check_and_fix_options(file_path)

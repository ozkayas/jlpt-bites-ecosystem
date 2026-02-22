import json
import sys
import re
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mechanical_tester.py <path/to/json/file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        sys.exit(1)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: Failed to parse JSON. {e}")
        sys.exit(1)

    if 'items' not in data or not isinstance(data['items'], list):
        print('Error: Root JSON must have an "items" array.')
        sys.exit(1)
        
    items = data['items']
    errors = 0

    for i, item in enumerate(items):
        if not isinstance(item, list) or len(item) != 4:
            print(f"Error at index {i}: Item must be an array of length 4.")
            errors += 1
            continue

        item_id = str(item[0])
        sentence = str(item[1])
        translations = item[2]
        options = item[3]

        matches = re.findall(r'<t>(.*?)</t>', sentence)

        if len(matches) != 1:
            print(f"Error in ID {item_id}: Sentence must contain exactly one <t>...</t> tag.")
            errors += 1
            continue

        tagged_text = matches[0]
        correct_answer = str(options[0]) if options else ''

        if tagged_text != correct_answer:
            print(f'Error in ID {item_id}: Tagged text "<{tagged_text}>" does not match correct answer "<{correct_answer}>".')
            errors += 1

        if len(options) < 2:
            print(f"Error in ID {item_id}: Options array must have at least 2 items (1 correct, 1+ distractors).")
            errors += 1

        if not isinstance(translations, dict) or 'tr' not in translations:
            print(f"Error in ID {item_id}: Translations object missing Turkish ('tr').")
            errors += 1

    if errors > 0:
        print(f"Mechanical testing failed with {errors} errors.")
        sys.exit(1)
    else:
        print(f"✅ Mechanical testing passed for all {len(items)} items!")

if __name__ == "__main__":
    main()

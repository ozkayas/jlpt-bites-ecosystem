import json
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch_viewer.py <path/to/json/file> <start_index> <count_optional>")
        sys.exit(1)

    file_path = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get('items', [])
    end = min(start + count, len(items))
    
    print(f"--- Showing items {start} to {end - 1} out of {len(items)} ---")

    for i in range(start, end):
        item = items[i]
        options = item[3]
        item_id = item[0]
        sentence = item[1]
        translations = item[2]
        
        print(f"\nIndex {i} [ID: {item_id}]")
        print(f"Sentence : {sentence}")
        print(f"Ans (Opt0): {options[0]}")
        print(f"Distract : {', '.join(map(str, options[1:]))}")
        
        for key, value in translations.items():
            print(f"Tra ({key}) : {value}")

if __name__ == "__main__":
    main()

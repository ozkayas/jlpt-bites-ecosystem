# Grammar Questions Data

This directory contains JSON data files for JLPT N5 grammar questions, organized by question type (Mondai).

## Directory Structure

```
firestore/grammar/
├── data/                           # JSON data files
│   ├── n5_mondai1_essential_grammar.json
│   ├── n5_mondai2_sentence_building.json
│   └── n5_mondai3_text_integration.json
├── scripts/                        # Upload scripts
│   └── upload_grammar_questions.py
└── README.md                       # This file
```

## Question Types

### Mondai 1: Essential Grammar (文の文法1)
Tests basic grammar particles and verb forms by filling in blanks in sentences.

**Fields:**
- `id`: Unique identifier (e.g., "n5_grammar_mondai1_001")
- `level`: JLPT level (n5, n4, n3, n2, n1)
- `type`: "sentenceCompletion"
- `sentence`: Japanese sentence with blank marker (　　)
- `blankPosition`: Position of blank in sentence (0-indexed)
- `options`: Array of 4 possible answers
- `correctAnswer`: Index of correct option (0-indexed)

### Mondai 2: Sentence Building (文の文法2)
Tests sentence structure by arranging scrambled words in correct order, with one word marked with a star.

**Fields:**
- `id`: Unique identifier (e.g., "n5_grammar_mondai2_001")
- `level`: JLPT level
- `type`: "starQuestion"
- `sentencePrefix`: Text before the blank
- `sentenceSuffix`: Text after the blank
- `scrambledWords`: Array of 4 words to arrange
- `starPosition`: Position where star marker appears (0-3)
- `correctOrder`: Array of indices showing correct word order

### Mondai 3: Text Integration (文章の文法)
Tests grammar in context by completing blanks in a paragraph.

**Fields:**
- `id`: Unique identifier (e.g., "n5_grammar_mondai3_001")
- `level`: JLPT level
- `type`: "textFlow"
- `title`: Passage title
- `textSegments`: Array of text segments (blanks go between segments)
- `blanks`: Array of blank objects:
  - `blankNumber`: Question number shown to user
  - `position`: Which text segment this blank follows (0-indexed)
  - `options`: Array of 4 possible answers
  - `correctAnswer`: Index of correct option (0-indexed)

## Data Format

All files follow this structure:
```json
{
  "questions": [
    { /* question object */ },
    { /* question object */ },
    ...
  ]
}
```

## Upload Process

See the workflow documentation: `.agent/workflows/upload_grammar_questions.md`

Quick upload:
```bash
cd firestore/grammar/scripts
python3 upload_grammar_questions.py n5
```

## Firestore Collection

Questions are uploaded to: `grammar_questions/{question_id}`

Each document contains all fields from the JSON, plus:
- `uploaded_at`: ISO timestamp of upload

## Adding New Questions

1. Edit the appropriate JSON file in `data/`
2. Follow the existing format exactly
3. Use sequential IDs: `n5_grammar_mondai{X}_{number}`
4. Ensure `correctAnswer` is 0-indexed
5. Test locally before uploading
6. Run upload script
7. Verify in Firebase Console

## Sample Questions

Current data includes:
- **Mondai 1**: 5 essential grammar questions (particles)
- **Mondai 2**: 5 sentence building questions (word order)
- **Mondai 3**: 3 text integration passages (grammar in context)

All questions are N5 level and test fundamental grammar concepts.

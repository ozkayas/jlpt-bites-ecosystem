# Reading Passages Upload Tool

This tool uploads JLPT reading passages from JSON files to Firestore.

## Files

- `upload_passages.py`: Main Python script.
- `upload.sh`: Helper shell script to activate venv and run the uploader.
- `requirements.txt`: Python dependencies.

## Data Source
The script reads from `firestore/reading/data/{level}_passages.json`.

## Usage

1. **Setup Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Upload**:
   - To upload a specific level:
     ```bash
     python3 upload_passages.py n5
     ```
   - To upload all levels:
     ```bash
     python3 upload_passages.py
     ```

## Firestore Structure
Data is uploaded to:
- Collection: `reading_contents`
- Document: `{level}_reading`
- Sub-collection: `passages`
  - Sub-collection: `sentences`
  - Sub-collection: `questions`

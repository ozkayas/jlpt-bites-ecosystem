# Listening Select Image Upload Tool

This tool uploads "Select Image" type listening questions to Firebase. It handles audio files, image options, and question metadata.

## Execution Flow

1. **Upload Audio**: Uploads `audio.mp3` to Cloud Storage.
2. **Upload Images**: Uploads `1.png`, `2.png`, `3.png`, `4.png` from `images/` folder to Cloud Storage.
3. **Order Preservation**: Ensures images are mapped to the correct `options` index based on their filenames.
4. **Update Metadata**: Updates the local `question_data.json` with the new public Download URLs.
5. **Firestore Sync**: Saves the entire question object to the `n5_listening_select_image_questions` collection.

## Files

- `upload_select_image_questions.py`: Main Python script.
- `requirements.txt`: Python dependencies.

## Usage

1. **Setup Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Upload**:
   ```bash
   python3 upload_select_image_questions.py --bucket jlpt-bites.firebasestorage.app
   ```

## Folder Structure Requirement
The script expects folders under `firestore/listening/data/selectImage/`:
```text
001/
├── audio.mp3
├── question_data.json
└── images/
    ├── 1.png
    ├── 2.png
    ├── 3.png
    ├── 4.png
```

## Collections
- **Storage Path**: `listening/selectImage/{question_id}/`
- **Firestore Collection**: `n5_listening_select_image_questions`

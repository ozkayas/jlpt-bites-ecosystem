# Firestore Content Management

This directory contains the source data and Python scripts for managing JLPT content in Firestore. The structure reflects the application's feature modules.

## 🔑 Authentication

All upload scripts require a Firebase Admin SDK service account key.

1.  Download a new private key from **Firebase Console -> Project Settings -> Service Accounts**.
2.  Save it as `service-account-key.json` in the **root** of this `firestore/` directory.

> **Note:** Do NOT place copies of the key in subdirectories. All scripts are configured to look for the key in the root `firestore/` folder.

## 📂 Directory Structure

### 1. Grammar (`firestore/grammar/`)
Manages grammar question data.
- **Data**: `data/` contains JSON files for different question types (Essential Grammar, Sentence Building, Text Integration).
- **Scripts**: `scripts/upload_grammar_questions.py` uploads questions based on JLPT level and type.

### 2. Listening (`firestore/listening/`)
Manages listening exercises.
- **Data**: `data/` contains JSON definitions for audio, image, and text-based listening questions.
- **Scripts**: Individual scripts for each question type (e.g., `upload_select_audio_questions.py`).

### 3. Reading (`firestore/reading/`)
Manages reading passages and translations.
- **Data**: `data/` contains split JSON files:
    - `*_passages_core.json`: Japanese text only.
    - `*_passages_translations_*.json`: Separate files for each supported language.
- **Scripts**: `scripts/upload_passages_v2.py` handles the upload of core content and translations to their respective subcollections.

### 4. Vocabulary (`firestore/vocabulary/`)
Manages vocabulary and kana data.
- **Data**: `data/n5_katakana_identification.json` for Kana training.
- **Scripts**: `scripts/upload_katakana_questions.py` for uploading data, plus utility scripts for checking duplicates.

## 🚀 Usage

Ensure you have a Python environment set up with `firebase-admin`.

```bash
# Example: Upload Grammar Questions
python3 firestore/grammar/scripts/upload_grammar_questions.py n5 --type all

# Example: Upload Reading Passages
python3 firestore/reading/scripts/upload_passages_v2.py n5 --languages en tr

# Example: Upload Listening Questions
python3 firestore/listening/scripts/upload_select_audio_questions.py
```

## 🛠 Maintenance

- **Normalization**: Ensure JSON filenames match the expected patterns (e.g., `n5_essential_grammar.json`).
- **Validation**: Run validation scripts (where available) before uploading large datasets.

#!/usr/bin/env python3
"""
Migrate selectText question_data.json files to Fat JSON (question.json) format.

Reads each question_data.json, translates content to 6 languages using Gemini,
and outputs question.json in the same folder.

Usage:
    python3 migrate_to_fat_json.py [--folder 002] [--all]
"""
import json
import sys
import os
import glob
import time
import re
import argparse

try:
    from dotenv import load_dotenv
    # Try multiple possible .env locations
    for env_path in [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            break
except ImportError:
    pass

from google import genai
from google.genai import types

# ─── Speaker Label Translations ──────────────────────────────────────────────
SPEAKER_MAP = {
    "おとこのひと":     {"tr": "Erkek",          "en": "Man",            "de": "Mann",         "fr": "Homme",      "es": "Hombre",     "ko": "남자"},
    "おんなのひと":     {"tr": "Kadın",          "en": "Woman",          "de": "Frau",         "fr": "Femme",      "es": "Mujer",      "ko": "여자"},
    "男の人":          {"tr": "Erkek",          "en": "Man",            "de": "Mann",         "fr": "Homme",      "es": "Hombre",     "ko": "남자"},
    "女の人":          {"tr": "Kadın",          "en": "Woman",          "de": "Frau",         "fr": "Femme",      "es": "Mujer",      "ko": "여자"},
    "おとこのがくせい": {"tr": "Erkek Öğrenci",  "en": "Male Student",   "de": "Student",      "fr": "Étudiant",   "es": "Estudiante", "ko": "남학생"},
    "おんなのがくせい": {"tr": "Kız Öğrenci",    "en": "Female Student", "de": "Studentin",    "fr": "Étudiante",  "es": "Estudiante", "ko": "여학생"},
    "せんせい":        {"tr": "Öğretmen",       "en": "Teacher",        "de": "Lehrer/in",    "fr": "Professeur", "es": "Profesor/a", "ko": "선생님"},
    "がくせい":        {"tr": "Öğrenci",        "en": "Student",        "de": "Schüler/in",   "fr": "Étudiant/e", "es": "Estudiante", "ko": "학생"},
    "てんいん":        {"tr": "Görevli",        "en": "Staff",          "de": "Angestellte/r","fr": "Employé/e",  "es": "Empleado/a", "ko": "직원"},
    "おみせのひと":    {"tr": "Mağaza Görevlisi","en": "Shop Staff",    "de": "Verkäufer/in", "fr": "Vendeur/se", "es": "Vendedor/a", "ko": "가게 직원"},
    "いしゃ":          {"tr": "Doktor",         "en": "Doctor",         "de": "Arzt/Ärztin",  "fr": "Médecin",    "es": "Médico/a",   "ko": "의사"},
}

LANGS = ["tr", "en", "de", "fr", "es", "ko"]
LANG_NAMES = {"tr": "Turkish", "en": "English", "de": "German", "fr": "French", "es": "Spanish", "ko": "Korean"}

MODEL = "gemini-2.5-flash"


def load_api_keys():
    keys_str = os.environ.get("GEMINI_API_KEYS", "")
    if keys_str:
        return [k.strip() for k in keys_str.split(",") if k.strip()]
    key = os.environ.get("GEMINI_API_KEY", "")
    return [key] if key else []


def translate_question(clients, question_data):
    """Send question content to Gemini for multi-language translation.
    clients is a list of genai.Client objects for key rotation."""
    trans = question_data["transcription"]
    analysis = question_data["analysis"]
    logic = question_data["logic"]
    topic_str = question_data["metadata"]["topic"]

    # Build translation prompt
    prompt = f"""You are translating a JLPT N5 Japanese listening question into 6 languages.
The content is educational and should be translated clearly at a beginner level.

IMPORTANT: Return ONLY valid JSON, no markdown fences, no explanation.

Source content:

TOPIC: {topic_str}

INTRO (Japanese): {trans["intro"]}
QUESTION (Japanese): {trans["question"]}

DIALOGUE:
{json.dumps(trans["dialogue"], ensure_ascii=False, indent=2)}

VOCABULARY:
{json.dumps(analysis["vocabulary"], ensure_ascii=False, indent=2)}

GRAMMAR:
{json.dumps(analysis["grammar"], ensure_ascii=False, indent=2)}

LOGIC:
tr: {logic["tr"]}
en: {logic["en"]}

Translate ALL of the above into these 6 languages: Turkish (tr), English (en), German (de), French (fr), Spanish (es), Korean (ko).

Return a JSON object with this exact structure:
{{
  "topic": {{ "ja": "Japanese topic", "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." }},
  "transcriptions": {{
    "tr": {{ "intro": "...", "question": "...", "dialogue_texts": ["line1", "line2", ...] }},
    "en": {{ "intro": "...", "question": "...", "dialogue_texts": ["line1", "line2", ...] }},
    "de": {{ "intro": "...", "question": "...", "dialogue_texts": ["line1", "line2", ...] }},
    "fr": {{ "intro": "...", "question": "...", "dialogue_texts": ["line1", "line2", ...] }},
    "es": {{ "intro": "...", "question": "...", "dialogue_texts": ["line1", "line2", ...] }},
    "ko": {{ "intro": "...", "question": "...", "dialogue_texts": ["line1", "line2", ...] }}
  }},
  "vocabulary": [
    {{ "reading": "hiragana reading", "meanings": {{ "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." }} }}
  ],
  "grammar": [
    {{ "meanings": {{ "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." }} }}
  ],
  "logic": {{ "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." }}
}}

RULES:
- dialogue_texts must have exactly {len(trans["dialogue"])} items (one per dialogue turn), in order.
- vocabulary array must have exactly {len(analysis["vocabulary"])} items, in the same order.
- grammar array must have exactly {len(analysis["grammar"])} items, in the same order.
- For "reading", provide the hiragana reading of the vocabulary word. If the word is already in hiragana, use the same text.
- Keep the existing tr and en translations if they are good, but improve if needed.
- For topic.ja, extract just the Japanese part from: {topic_str}
- All translations must be natural and appropriate for language learners.
"""

    for attempt in range(len(clients) * 2):
        client = clients[attempt % len(clients)]
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            text = response.text.strip()
            # Remove markdown fences if present
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\n?", "", text)
                text = re.sub(r"\n?```$", "", text)
            return json.loads(text)
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                print(f"    Key {attempt % len(clients) + 1} exhausted, trying next...")
                continue
            print(f"    Attempt {attempt+1} failed: {e}")
            if attempt < len(clients) * 2 - 1:
                time.sleep(5)
    return None


def build_fat_json(question_data, translations):
    """Build Fat JSON from original data + translations."""
    trans = question_data["transcription"]
    analysis = question_data["analysis"]

    # Build transcriptions
    transcriptions = {
        "ja": {
            "intro": trans["intro"],
            "dialogue": trans["dialogue"],
            "question": trans["question"],
        }
    }

    for lang in LANGS:
        t = translations["transcriptions"][lang]
        dialogue_translated = []
        for i, turn in enumerate(trans["dialogue"]):
            speaker_ja = turn["speaker"]
            speaker_labels = SPEAKER_MAP.get(speaker_ja, {})
            speaker_translated = speaker_labels.get(lang, speaker_ja)
            text_translated = t["dialogue_texts"][i] if i < len(t["dialogue_texts"]) else ""
            dialogue_translated.append({
                "speaker": speaker_translated,
                "text": text_translated,
            })
        transcriptions[lang] = {
            "intro": t["intro"],
            "dialogue": dialogue_translated,
            "question": t["question"],
        }

    # Build vocabulary
    vocabulary = []
    for i, v in enumerate(analysis["vocabulary"]):
        tv = translations["vocabulary"][i] if i < len(translations["vocabulary"]) else {}
        meanings = tv.get("meanings", {})
        # Ensure existing tr/en are preserved if Gemini didn't improve them
        if "tr" not in meanings:
            meanings["tr"] = v.get("tr", "")
        if "en" not in meanings:
            meanings["en"] = v.get("en", "")
        vocabulary.append({
            "word": v["word"],
            "reading": tv.get("reading", v["word"]),
            "meanings": {lang: meanings.get(lang, "") for lang in LANGS},
        })

    # Build grammar
    grammar = []
    for i, g in enumerate(analysis["grammar"]):
        tg = translations["grammar"][i] if i < len(translations["grammar"]) else {}
        meanings = tg.get("meanings", {})
        if "tr" not in meanings:
            meanings["tr"] = g.get("tr", "")
        if "en" not in meanings:
            meanings["en"] = g.get("en", "")
        grammar.append({
            "point": g["point"],
            "meanings": {lang: meanings.get(lang, "") for lang in LANGS},
        })

    # Build logic
    logic = {}
    for lang in LANGS:
        logic[lang] = translations["logic"].get(lang, "")

    # Build final Fat JSON
    fat = {
        "metadata": {
            "level": "N5",
            "topic": translations["topic"],
        },
        "audio_url": question_data["metadata"].get("audio_url"),
        "options": question_data["options"],
        "correct_option": question_data["correct_option"],
        "transcriptions": transcriptions,
        "analysis": {
            "vocabulary": vocabulary,
            "grammar": grammar,
        },
        "logic": logic,
    }

    return fat


def process_folder(folder_path, clients):
    """Process a single folder: read question_data.json, translate, write question.json."""
    folder_id = os.path.basename(folder_path)
    qd_path = os.path.join(folder_path, "question_data.json")
    out_path = os.path.join(folder_path, "question.json")

    if not os.path.exists(qd_path):
        print(f"  ⚠️  {folder_id}: question_data.json not found")
        return False

    if os.path.exists(out_path):
        print(f"  ⏭️  {folder_id}: question.json already exists")
        return True

    print(f"  📝 {folder_id}: Translating...")

    with open(qd_path, "r", encoding="utf-8") as f:
        question_data = json.load(f)

    translations = translate_question(clients, question_data)
    if not translations:
        print(f"  ❌ {folder_id}: Translation failed")
        return False

    fat_json = build_fat_json(question_data, translations)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fat_json, f, ensure_ascii=False, indent=4)

    print(f"  ✅ {folder_id}: question.json saved")
    return True


def main():
    parser = argparse.ArgumentParser(description="Migrate selectText to Fat JSON")
    parser.add_argument("--folder", help="Specific folder ID (e.g., 002)")
    parser.add_argument("--all", action="store_true", help="Process all folders")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    api_keys = load_api_keys()
    if not api_keys:
        print("No GEMINI_API_KEYS found in environment or .env")
        sys.exit(1)

    clients = [genai.Client(api_key=k) for k in api_keys]
    print(f"Using Gemini model: {MODEL}, {len(clients)} API keys")

    if args.folder:
        folder_path = os.path.join(base_dir, args.folder)
        process_folder(folder_path, clients)
    elif args.all:
        folders = sorted(glob.glob(os.path.join(base_dir, "[0-9][0-9][0-9]")))
        success = 0
        failed = 0
        for folder in folders:
            if process_folder(folder, clients):
                success += 1
            else:
                failed += 1
            time.sleep(2)  # Rate limiting
        print(f"\nDone: {success} success, {failed} failed out of {len(folders)} total")
    else:
        print("Usage: python3 migrate_to_fat_json.py --folder 002")
        print("       python3 migrate_to_fat_json.py --all")
        sys.exit(1)


if __name__ == "__main__":
    main()

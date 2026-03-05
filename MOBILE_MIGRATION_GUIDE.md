# Mobile App Migration Prompt: Fat JSON Schema Support

This document provides a specialized prompt to refactor the mobile application's data models and UI logic to support the new 6-language "Fat JSON" architecture.

---

## The Prompt for AI Coding Agent

**Role:** Expert Flutter/Dart Developer specializing in Data Modeling and i18n.

**Context:** 
We have migrated our JLPT N5 Listening data in Firebase from a single-language structure to a multi-language "Fat JSON" structure. The app is currently crashing with the error: `type Map<string, dynamic> is not a subtype of the type String in type cast` because the models still expect `String` values for fields that are now `Map` objects.

**Your Task:**
Refactor the Listening Question models, factory constructors, and UI components to support the following JSON changes.

### 1. JSON Schema Changes (Before vs. After)

#### A. Metadata Topic
- **Old:** `"metadata": { "topic": "Waiting at school" }` (String)
- **New:** `"metadata": { "topic": { "ja": "...", "en": "...", "tr": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." } }` (Map)

#### B. Transcriptions (Pluralized)
- **Old:** `"transcription": { "intro": "...", "dialogue": [...], "question": "..." }`
- **New:** `"transcriptions": { "en": { ... }, "tr": { ... }, "ja": { ... }, ... }` (Nested Map)

#### C. Vocabulary & Grammar Analysis
- **Old:** `{ "word": "...", "tr": "...", "en": "..." }`
- **New:** `{ "word": "...", "meanings": { "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." } }`

#### D. Logic Section
- **Old:** `"logic": { "tr": "...", "en": "..." }`
- **New:** `"logic": { "tr": "...", "en": "...", "de": "...", "fr": "...", "es": "...", "ko": "..." }`

### 2. Implementation Requirements

1.  **Language Handling:** Introduce a way to determine the `activeLanguage` (e.g., from a Locale provider or settings).
2.  **Model Refactoring:**
    -   Update `fromJson` factories to handle `Map<String, dynamic>` for translated fields.
    -   Implement a fallback mechanism: If the user's language is not found, default to `en`.
3.  **UI Updates:** Ensure widgets that display the topic, transcription, and vocabulary use the correct language key from the new nested structures.
4.  **Type Safety:** Remove all direct `as String` casts on fields that are now maps. Use `Map<String, dynamic>.from(json['field'])` safely.

**Example Logic for Model:**
```dart
String getLocalizedTopic(String lang) {
  return metadata.topic[lang] ?? metadata.topic['en'] ?? '';
}
```

Please scan the project for classes like `Question`, `Transcription`, `Vocabulary` and apply these changes.

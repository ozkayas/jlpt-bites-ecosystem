---
name: jlpt-listening-multi-language-expander
description: Transform a JLPT N5 Listening 'question.json' into a 'Fat JSON' architecture supporting 6 UI languages: TR, EN, DE, FR, ES, and KO. This skill extracts the Japanese core content and generates high-quality, N5-appropriate translations for all fields (transcription, vocabulary, grammar, and logic). Use when the user wants to add international support to a listening question or migrate to the multi-language schema.
---

# Multi-Language Expansion Skill

This skill converts a standard 1 or 2-language `question.json` into a comprehensive 6-language "Fat JSON" for the JLPT Bites mobile app.

## Target Languages
- **Source:** Japanese (`ja`)
- **Target 1:** English (`en`)
- **Target 2:** Turkish (`tr`)
- **Target 3:** German (`de`)
- **Target 4:** French (`fr`)
- **Target 5:** Spanish (`es`)
- **Target 6:** Korean (`ko`)

## Core Workflow

### 1. Extract and Verify
Read the source `question.json`. Identify the Japanese `ja` content as the master reference. Ensure the `level` is N5.

### 2. Expert Translation Guidelines
Act as an expert polyglot linguist specializing in Japanese language education.
- **N5 Simplicity:** Keep target language translations clear and straightforward. Avoid complex literary terms.
- **Tone:** Use a polite, educational tone appropriate for a language learning app.
- **Consistency:** If a word appears in both the dialogue and the vocabulary list, ensure the translations are identical.
- **Logic Section:** Explain the reasoning/answer clearly in all languages, emphasizing the "why" as much as the "what".

### 3. JSON Transformation (Fat Schema)
Restructure the JSON following the schema in `references/json-schema.md`.
- **Transcriptions:** Map each language under `transcriptions[lang]`.
- **Vocabulary/Grammar:** Convert existing language keys (e.g., `tr`, `en`) into a unified `meanings` object within each list item.
- **Metadata:** Translate the `topic` into all 6 languages.

## Validation Checklist
1. All 6 target languages + `ja` must be present in `transcriptions`.
2. Every vocabulary word and grammar point must have 6 entries in `meanings`.
3. The `logic` object must have 6 language keys.
4. JSON must remain valid and machine-readable.

## Example Transformation Prompt (Internal)
"I will now take this JLPT N5 Listening question about [TOPIC] and expand it into a 6-language Fat JSON. I will ensure the French, German, Spanish, and Korean translations are as natural and accurate as the Turkish and English originals, following N5 pedagogical standards."

---
name: vocabulary-sentence-drill-tester
description: A two-step validation skill (mechanical + LLM-based) for the Vocabulary Sentence Drill module. Use when the user requests to test, evaluate, review, or fix issues with "vocabulary-sentence-drill.json" or when adding brand new Sentence Drill questions.
---
# Vocabulary Sentence Drill Tester

This skill ensures that questions inside translation-oriented arrays (.json files such as `vocabulary-sentence-drill.json`) are both mechanically sound and semantically correct.

## Overview 

The validation consists of two phases:
1. **Mechanical Validation**: A deterministic test verifying the JSON schema, the `<t>` tag rules, and the options format.
2. **Semantic Review**: An AI-driven check evaluating the pedagogic quality, the correctness of the translations, and the validity of the distractors.

## Step 1: Mechanical Validation

Run the provided Python script to execute a mechanical check on all questions.

```bash
python3 .agent/skills/vocabulary-sentence-drill-tester/scripts/mechanical_tester.py <path/to/json/file>
```

This script will quickly ensure that:
- Every question array has length 4.
- The sentence has exactly one `<t>...</t>` tag.
- The string inside `<t>...</t>` EXACTLY matches the first option in the options array (the correct answer).
- There is at least 1 correct answer and 1 distractor.
- The `tr` (Turkish) translation property exists.

If there are any errors, use `replace_file_content` or `multi_replace_file_content` on the tested JSON file to fix them mechanically before proceeding to the Semantic Review.

## Step 2: Semantic (LLM) Review

Because the JSON file can contain hundreds of questions, use the `batch_viewer.py` script to chunk through questions. 
Unless the user specifies an ID or range, ask the user which chunk or specific IDs they want to review, or evaluate a sample of 5-10 questions to ensure the module works flawlessly.

```bash
# Example: Review 5 questions starting from index 0
python3 .agent/skills/vocabulary-sentence-drill-tester/scripts/batch_viewer.py <path/to/json/file> 0 5
```

For each question, evaluate the following:
1. **Target Accuracy (`<t>` tag)**: Does the word inside the `<t>` tag logically belong in that sentence? Is it the correct part of speech compared to the rest of the sentence?
2. **Translation Validity**: Do the provided translations accurately reflect the original Japanese sentence with the correct answer injected? Is the grammar in the translated text natural?
3. **Distractor Quality**: Are the distractors (options 1, 2, 3) realistic? 
   - **CRITICAL**: None of the distractors should be synonymous or alternate valid answers that could accidentally make the sentence correct.

If you find anything confusing or incorrect, report it to the user or fix it directly if you are certain.

## References & Data Structure

The `vocabulary-sentence-drill.json` format is strict. If you edit the file, ensure the format matches precisely:
```json
[
  "ID",
  "Sentence with target inside <t>...</t>",
  {
    "tr": "Turkish translation",
    "en": "English translation"
  },
  [
    "Correct Answer (must exactly match text inside <t>)",
    "Distractor 1",
    "Distractor 2",
    "Distractor 3"
  ]
]
```

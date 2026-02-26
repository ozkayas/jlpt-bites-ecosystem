# TTS (Text-to-Speech) Formatting Guidelines

To ensure professional audio generation, the output must include a `tts_script` field formatted for high-end TTS services (like OpenAI, ElevenLabs, or Amazon Polly).

## Voice Mapping
- **Male_1:** Neutral, young-to-middle-aged Japanese male voice (Standard for JLPT).
- **Female_1:** Clear, polite, young Japanese female voice (Standard for JLPT).
- **Intro_Voice:** Formal, slightly slower narration voice.

## Timing & SSML Tags
- **Intro Pause:** After the intro sentence (e.g., "Question 1"), add a `<break time="1s"/>`.
- **Turn-taking Pause:** Between different speakers, add a `<break time="0.5s"/>`.
- **Question Repeat:** After the dialogue, add a `<break time="1s"/>` then repeat the question.

## Formatting Example
```json
{
  "tts_script": [
    { "voice": "Intro_Voice", "text": "おとこのひとと おんなのひとが はなしています。ふたりは どのしゃしんを みていますか。" },
    { "break": "1s" },
    { "voice": "Male_1", "text": "やまださん、このしゃしんは？" },
    { "break": "0.5s" },
    { "voice": "Female_1", "text": "ああ、これは きょねんのはるに うみへ いったときの しゃしんです。" },
    { "break": "1s" },
    { "voice": "Intro_Voice", "text": "ふたりは どのしゃしんを みていますか。" }
  ]
}
```

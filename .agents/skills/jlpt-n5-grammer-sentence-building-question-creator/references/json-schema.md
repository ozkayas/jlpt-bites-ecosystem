# JSON Output Schema — Sentence Building (starQuestion)

## Top-level structure

```json
{
  "questions": [ ...Question[] ]
}
```

## Question object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `n5_grammer_sentence_building_XXX` — zero-padded sequential number (e.g., 001, 002) |
| `level` | string | Always `"n5"` |
| `type` | string | Always `"starQuestion"` |
| `sentencePrefix` | string | Text before the scrambled section |
| `sentenceSuffix` | string | Text after the scrambled section |
| `scrambledWords` | string[4] | Exactly 4 words/particles in scrambled order |
| `starPosition` | number | 0-based index of which position in the correct order is the "star" answer (0–3) |
| `correctOrder` | number[4] | Array of 4 indices mapping scrambled positions to correct order |

## How starPosition and correctOrder work

The student must arrange the 4 `scrambledWords` into the correct sentence order. `correctOrder` is an array of indices into `scrambledWords` showing the right sequence. `starPosition` marks which position (0-based) in the correct order the student must identify as the answer.

## Example

```json
{
  "id": "n5_grammer_sentence_building_001",
  "level": "n5",
  "type": "starQuestion",
  "sentencePrefix": "昨日",
  "sentenceSuffix": "買いました。",
  "scrambledWords": ["で", "を", "デパート", "かばん"],
  "starPosition": 3,
  "correctOrder": [2, 0, 3, 1]
}
```

Correct sentence: 昨日 **デパート** **で** **かばん** **を** 買いました。
- correctOrder[0] = 2 → scrambledWords[2] = "デパート"
- correctOrder[1] = 0 → scrambledWords[0] = "で"
- correctOrder[2] = 3 → scrambledWords[3] = "かばん" ← star (starPosition=2 would mark this)
- correctOrder[3] = 1 → scrambledWords[1] = "を"

## Rules

- `correctOrder` must be a permutation of [0, 1, 2, 3].
- `starPosition` is 0-indexed (0–3), indicating which slot in `correctOrder` is the answer.
- `scrambledWords` must contain exactly 4 items.
- All vocabulary must be N5 level.
- The reconstructed sentence (prefix + ordered words + suffix) must be grammatically correct.

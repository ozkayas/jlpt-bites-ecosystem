# Imagen 3 (Nano Banana) Prompt Engineering Guide

This guide defines how to write image generation prompts for the 4 visual options in each listening variation question. The target model is **Imagen 3** (Nano Banana tier).

---

## Model Strengths

- **Natural language:** Responds to flowing descriptive sentences, not tag lists.
- **Typography:** If text must appear in the image, specify it in quotes inside the prompt.
- **Photorealism:** Responds well to lighting sources, camera angles, and texture descriptions.
- **Color:** Full-color output — use color as a distinguishing attribute when appropriate.

---

## Prompt Structure Hierarchy

Every prompt must follow this 5-part order:

1. **Main Subject** — What is at the center of the image?
2. **Action/State** — What is the subject doing or what condition is it in?
3. **Environment** — Where does the scene take place? What background details are visible?
4. **Style and Atmosphere** — Lighting (soft light, cinematic, warm afternoon, etc.), color tone, art direction.
5. **Technical Details** — Descriptive quality indicators (avoid generic terms like "high quality"; use descriptive specifics instead).

---

## Writing Rules

- **Do NOT use comma-separated tag lists.** Write fluent, descriptive sentences instead.
- **If text must appear in the image**, write it as: `a sign reading "..."` or `a label saying "..."`.
- **Keep scene context consistent across all 4 options** — only the delta element should change.
- **Match JLPT context:** Scenes should depict ordinary Japanese daily life (café, classroom, station, market, home, etc.).
- **Color is fully usable** as a distinguishing attribute between options.

---

## 4-Option Structure (Delta Principle)

Each option shares the same scene setup. Only the distinguishing element(s) differ:

| Option | Role | Delta |
|--------|------|-------|
| Option A | Correct | Correct delta-A + Correct delta-B |
| Option B | Distractor_A | Wrong delta-A + Correct delta-B |
| Option C | Distractor_B | Correct delta-A + Wrong delta-B |
| Option D | Distractor_C | Wrong delta-A + Wrong delta-B |

**Example — Attribute Filter (size × color):**
- Correct: "A large red umbrella standing upright in a wooden rack near the entrance of a shop..."
- Distractor_A: "A small red umbrella standing upright in a wooden rack near the entrance of a shop..."
- Distractor_B: "A large blue umbrella standing upright in a wooden rack near the entrance of a shop..."
- Distractor_C: "A small blue umbrella standing upright in a wooden rack near the entrance of a shop..."

---

## Style Anchor

All 4 prompts for a single question must use the **same style anchor** at the end of each prompt to ensure visual consistency:

> "...clean illustration style, soft even lighting, muted warm tones, Japanese everyday life setting, no text overlays."

Adjust the style anchor to fit the scene type (outdoor market vs. indoor café vs. street map, etc.).

---

## Complete Example (Reconsideration Pattern)

**Scenario:** Woman chooses hot coffee after rejecting orange juice and iced tea.

- **Option 0 (Correct):** "A ceramic mug of hot coffee sitting on a wooden café table, steam rising from the surface, warm ambient lighting, soft focus background with blurred café shelves, clean illustration style, soft even lighting, muted warm tones, Japanese everyday life setting, no text overlays."
- **Option 1 (Distractor_A):** "A glass of orange juice with ice cubes sitting on a wooden café table, condensation on the glass surface, warm ambient lighting, soft focus background with blurred café shelves, clean illustration style, soft even lighting, muted warm tones, Japanese everyday life setting, no text overlays."
- **Option 2 (Distractor_B):** "A tall glass of iced coffee with a straw sitting on a wooden café table, ice cubes visible through the glass, warm ambient lighting, soft focus background with blurred café shelves, clean illustration style, soft even lighting, muted warm tones, Japanese everyday life setting, no text overlays."
- **Option 3 (Distractor_C):** "A glass of cold green tea with ice cubes sitting on a wooden café table, condensation visible, warm ambient lighting, soft focus background with blurred café shelves, clean illustration style, soft even lighting, muted warm tones, Japanese everyday life setting, no text overlays."

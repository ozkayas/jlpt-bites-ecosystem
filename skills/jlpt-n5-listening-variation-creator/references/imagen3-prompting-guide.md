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

## Composite 2×2 Grid Structure (Delta Principle)

All 4 options are generated in a **single Imagen 3 call** as a 2×2 grid image. Each panel contains one option. Only the distinguishing element(s) differ between panels.

### Panel Layout
```
┌─────────┬─────────┐
│ Panel 1 │ Panel 2 │
│ (1)     │ (2)     │
├─────────┼─────────┤
│ Panel 3 │ Panel 4 │
│ (3)     │ (4)     │
└─────────┴─────────┘
```

The `panel_map` in `derived-data.json` records which panel holds which `logic_role`. The correct panel position should be varied across questions (do not always place Correct in Panel 1).

### Delta Table Example (Attribute Filter — size × color)

| Panel | Role | Delta |
|-------|------|-------|
| Panel 1 | Correct | Large + red |
| Panel 2 | Distractor_A | Small + red |
| Panel 3 | Distractor_B | Large + blue |
| Panel 4 | Distractor_C | Small + blue |

---

## Composite Prompt Template

```
A 2×2 grid image divided into four equal square panels with a thin white border between them.
Each panel has a bold number in the top-left corner (1, 2, 3, 4).
[Shared scene context — e.g., "Japanese clothing store, retail shelves in background."]
Panel 1 (top-left): [item/scene description]
Panel 2 (top-right): [item/scene description]
Panel 3 (bottom-left): [item/scene description]
Panel 4 (bottom-right): [item/scene description]
Clean illustration style, soft even lighting, muted warm tones, no text other than panel numbers.
```

---

## Complete Example (Reconsideration Pattern)

**Scenario:** Woman chooses hot coffee after rejecting orange juice and iced tea.
**Correct answer:** Panel 1 (hot coffee) → `correct_option: 0`

```
A 2×2 grid image divided into four equal square panels with a thin white border between them.
Each panel has a bold number in the top-left corner (1, 2, 3, 4).
Japanese café table setting, wooden surface, warm ambient light, blurred café shelves in background.
Panel 1 (top-left): A ceramic mug of hot coffee, steam rising from the surface.
Panel 2 (top-right): A glass of orange juice with ice cubes, condensation on the glass.
Panel 3 (bottom-left): A tall glass of iced coffee with a straw, ice cubes visible through the glass.
Panel 4 (bottom-right): A glass of cold green tea with ice cubes.
Clean illustration style, soft even lighting, muted warm tones, no text other than panel numbers.
```

**Corresponding panel_map:**
```json
[
  { "panel": 1, "logic_role": "Correct" },
  { "panel": 2, "logic_role": "Distractor_A" },
  { "panel": 3, "logic_role": "Distractor_B" },
  { "panel": 4, "logic_role": "Distractor_C" }
]
```

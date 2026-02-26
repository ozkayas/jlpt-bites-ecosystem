# Imagen 3 (Nano Banana) Prompt Engineering Guide

This guide defines how to write image generation prompts for the 4 visual options in each listening variation question. The target model is **Imagen 3** (Nano Banana tier).

---

## Model Strengths

- **Natural language:** Responds to flowing descriptive sentences, not tag lists.
- **Typography:** If text must appear in the image, specify it in quotes inside the prompt.
- **Line art:** Responds well to explicit monochrome and illustration style descriptors.
- **Style anchoring:** A strong style suffix at the end of the prompt locks the visual output.

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
- **Keep scene context consistent across all 4 panels** — only the delta element should change.
- **Match JLPT context:** Scenes should depict ordinary Japanese daily life (café, classroom, station, market, home, etc.).
- **No color references:** Style is monochrome. Differentiate panels by shape, size, quantity, position, or presence/absence of objects — never by color.

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

### Delta Table Example (Attribute Filter — size × quantity)

| Panel | Role | Delta |
|-------|------|-------|
| Panel 1 | Correct | Large + single item |
| Panel 2 | Distractor_A | Small + single item |
| Panel 3 | Distractor_B | Large + two items |
| Panel 4 | Distractor_C | Small + two items |

---

## Composite Prompt Template

```
A 2×2 grid image divided into four equal square panels with thin white borders between them.
[Shared subject context — keep background minimal or white.]
Top-left panel: [item/scene — shape, size, quantity, or presence/absence delta]
Top-right panel: [item/scene]
Bottom-left panel: [item/scene]
Bottom-right panel: [item/scene]
Minimalist black and white line art, Japanese language textbook illustration style, clean monochrome, thick clean outlines, no shading, white background, simple character design, instructional clipart style, high contrast, no text.
```

---

## Complete Example (Reconsideration Pattern)

**Scenario:** Woman chooses hot coffee after rejecting orange juice and iced tea.
**Correct answer:** Panel 1 (hot coffee) → `correct_option: 0`

```
A 2×2 grid image divided into four equal square panels with thin white borders between them.
Japanese café setting, simple white background, line art objects on a table surface.
Top-left panel: A ceramic mug of hot coffee with steam rising from the surface.
Top-right panel: A tall glass with a straw, ice cubes, and a lemon slice on the rim.
Bottom-left panel: A tall glass with a straw and ice cubes, a cherry on top.
Bottom-right panel: A glass with a straw and ice cubes, no garnish.
Minimalist black and white line art, Japanese language textbook illustration style, clean monochrome, thick clean outlines, no shading, white background, simple character design, instructional clipart style, high contrast, no text.
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

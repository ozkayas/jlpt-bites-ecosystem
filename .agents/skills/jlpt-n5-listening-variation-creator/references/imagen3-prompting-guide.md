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
- **Keep scene context minimal:** Use a pure white background. Do NOT describe the environment (e.g., "in a supermarket", "on a wooden table", "inside a room") unless the question logic specifically requires a location (like a Map or Room layout).
- **Focus on the Object:** Only describe the objects or people being discussed.
- **No color references:** Style is monochrome. Differentiate panels by shape, size, quantity, position, or presence/absence of objects — never by color.

---

## Visual Identification of Items (Icons & Labels)

When objects might be ambiguous in monochrome line art (e.g., a coffee can looking like a food can, or a water bottle looking like juice), **use icons and short text labels** to make them immediately recognizable to anyone regardless of language background.

### Rules

- **Specify the physical form explicitly** — don't just write "coffee"; write "disposable paper hot coffee cup with a corrugated cardboard sleeve and a plastic dome lid". The form itself conveys meaning.
- **Add a simple icon on labels** — describe it in the prompt: `a small coffee bean icon printed on the cup`, `a water droplet icon on the label`, `a bread slice icon on the package`.
- **Short single-word text labels are allowed on items** — e.g., a cup with a small "COFFEE" label, a bottle with "WATER". Write it as: `a label reading "COFFEE"`.
- **Update the style suffix** when using icons/labels — change from "no text other than the small panel numbers" to: `no text other than the small panel numbers 1, 2, 3, 4 in the top-left corner of each panel and simple identifying icons or short labels directly on the depicted items`.

### Common Examples

| Item | Ambiguous form | Clear form |
|------|---------------|------------|
| Hot coffee | Short squat cylindrical can | Tall disposable paper cup with corrugated sleeve, dome lid, coffee bean icon |
| Water | Generic PET bottle | Clear PET bottle with a water droplet icon on the label |
| Juice | Generic bottle | Bottle with a fruit slice icon on the label |
| Sandwich | Flat package | Flat package with a sandwich icon showing bread and filling |
| Tea | Generic bottle or can | Tall bottle with a tea leaf icon on the label |
| Milk | Generic bottle | White carton with a cow icon or label reading "MILK" |

---

## Special Case: Calculation Questions

When the question asks the user to **calculate a numerical result** (e.g., "ぜんぶで いくら はらいますか", "なんにん きますか"), the visual logic is fundamentally different from object-based questions.

> **Critical rule:** Do NOT draw the items being purchased or discussed. The dialogue already conveys what the items are. Showing the items in the panels makes the visual redundant and the question incoherent — the user would hear "apples and bananas" and then see apples and bananas, making the image useless.

**The panels must show the 4 possible numerical results**, not the objects. The user listens, performs the mental calculation, and selects the matching number.

### When to apply this rule

| Question phrasing | Dialogue content | Correct visual |
|---|---|---|
| ぜんぶで いくら はらいますか | Item names + unit prices + quantities | 4 yen amounts as price tags |
| なんにん きますか | People joining/leaving | 4 numerals |
| なんじに つきますか | Departure time + travel duration | 4 clock faces or time labels |

### Numerical Options Template (`four_panel_grid`)

```
A 2×2 grid image with four equal square panels.
Each panel contains a single yen amount displayed on a price tag against a white background.
Panel 1 (top-left, number 1): A price tag reading "[amount]円".
Panel 2 (top-right, number 2): A price tag reading "[amount]円".
Panel 3 (bottom-left, number 3): A price tag reading "[amount]円".
Panel 4 (bottom-right, number 4): A price tag reading "[amount]円".
Minimalist black and white line art, Japanese language textbook illustration style, clean monochrome, thick clean outlines, no shading, white background, instructional clipart style, high contrast, no text other than the small panel numbers 1, 2, 3, 4 in the top-left corner of each panel and the yen amounts on the price tags.
```

### Delta Table Example (total price calculation)

Dialogue: 80円 apple × 4 + 120円 banana × 1

| Panel | Role | Amount | Trap logic |
|-------|------|--------|------------|
| Panel 1 | Distractor_A | 80円 | Remembered only the unit price of one item |
| Panel 2 | Distractor_B | 320円 | Totalled first item only (80×4), forgot second |
| Panel 3 | Distractor_C | 560円 | Swapped quantities (120×4 + 80×1) |
| Panel 4 | Correct | 440円 | 80×4 + 120×1 = 440円 ✓ |

---

## Image Type Detection

When a source PNG is available, read it and determine the `image_type` before writing the prompt. Use these criteria:

| PNG characteristic | `image_type` |
|---|---|
| 4 separate equal panels arranged in a 2×2 grid layout | `four_panel_grid` |
| Single scene (room, shop, venue interior) with small numbers 1–4 marking positions | `numbered_scene` |
| Top-down street or area map with small numbers 1–4 on buildings or locations | `map_diagram` |

**Key distinction:** `four_panel_grid` has small numbers 1, 2, 3, 4 in the top-left corner of each panel. `numbered_scene` and `map_diagram` use position numbers within the scene or map itself to mark locations.

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

## Prompt Templates by Image Type

### `four_panel_grid`

Use when the question has 4 independent panels, each showing one option. Each panel has a small number (1, 2, 3, 4) in its top-left corner.

```
A 2×2 grid image with four equal square panels.
[Shared subject context — keep background minimal or white.]
Panel 1 (top-left, number 1): [item/scene — shape, size, quantity, or presence/absence delta]
Panel 2 (top-right, number 2): [item/scene]
Panel 3 (bottom-left, number 3): [item/scene]
Panel 4 (bottom-right, number 4): [item/scene]
Minimalist black and white line art, Japanese language textbook illustration style, clean monochrome, thick clean outlines, no shading, white background, simple character design, instructional clipart style, high contrast, no text other than the small panel numbers 1, 2, 3, 4 in the top-left corner of each panel.
```

### `numbered_scene`

Use when the question shows a single scene (room, shop, park, etc.) with numbered position markers.

```
A single [room/shop/venue type] illustration, isometric line art view.
[Scene description: furniture, shelves, layout.]
Four small number labels (1, 2, 3, 4) mark specific positions within the scene.
Position 1: [what occupies / what is at this location]
Position 2: [...]
Position 3: [...]
Position 4: [...]
Minimalist black and white line art, Japanese language textbook illustration style, clean monochrome, thick clean outlines, no shading, white background, simple character design, instructional clipart style, high contrast, no text other than the position numbers 1, 2, 3, 4.
```

### `map_diagram`

Use when the question shows a top-down street or area map with numbered building/location markers.

```
A simple top-down street map illustration.
[Street/block layout description: main road, intersection, directions.]
Four small number labels (1, 2, 3, 4) mark building or location positions on the map.
Position 1: [building or location]
Position 2: [...]
Position 3: [...]
Position 4: [...]
Two simple line-art characters stand at the starting point looking at the map.
Minimalist black and white line art, Japanese language textbook illustration style, clean monochrome, thick clean outlines, no shading, white background, simple character design, instructional clipart style, high contrast, no text other than the position numbers 1, 2, 3, 4.
```

---

## Complete Example (Reconsideration Pattern)

**Scenario:** Woman chooses hot coffee after rejecting orange juice and iced tea.
**Correct answer:** Panel 1 (hot coffee) → `correct_option: 0`

```
A 2×2 grid image with four equal square panels.
Japanese café setting, simple white background, line art objects on a table surface.
Panel 1 (top-left, number 1): A ceramic mug of hot coffee with steam rising from the surface.
Panel 2 (top-right, number 2): A tall glass with a straw, ice cubes, and a lemon slice on the rim.
Panel 3 (bottom-left, number 3): A tall glass with a straw and ice cubes, a cherry on top.
Panel 4 (bottom-right, number 4): A glass with a straw and ice cubes, no garnish.
Minimalist black and white line art, Japanese language textbook illustration style, clean monochrome, thick clean outlines, no shading, white background, simple character design, instructional clipart style, high contrast, no text other than the small panel numbers 1, 2, 3, 4 in the top-left corner of each panel.
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

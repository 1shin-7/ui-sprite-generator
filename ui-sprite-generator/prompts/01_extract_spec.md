# Prompt 01 - Extract Spec

**Inputs:** `input/effect.png`  
**Output:** `spec.json` in the run directory  

You are a game UI asset pipeline engineer. Analyze the attached effect image and output one valid JSON object matching `schemas/spec.schema.json`. Do not wrap the JSON in markdown.

## Requirements

- Record the source image path, width, and height.
- Describe the global UI style: palette, materials, lighting, ornament language, and negative constraints.
- Extract a complete specification for regenerating UI components as isolated sprites, not for cropping them from the source image.
- Identify the background, including visible regions and UI-occluded regions that must be restored in `background_plate.png`.
- Identify every distinct UI chrome component. Do not include plain text unless the text is a graphical sprite.
- Every component must have a precise `source_bbox` in source image pixels.
- Hollow panels must not treat their center as component fill; their center contributes to background visibility or restoration.
- Each component must include role, visual description, attached decorations, center type, tiling, render pattern, resolution policy, atlas policy, layering, states, and companions.
- `target_px` must be at least the source bbox size. Use 2x by default and 3x for complex materials when practical.
- Atlas policy must group components by type and complexity without forcing oversized components into crowded sheets.

## Component Analysis Rules

- Cover every distinct UI chrome element visible in the mockup.
- Describe each component visually in isolation: border decoration, frame material, trim, bevel, glow, texture, ornaments, and transparent or hollow regions.
- Do not simplify ornate border decoration into plain rectangles.
- If a component has physically attached decorations, list every attached decoration.
- If a component is structurally composite, split it into smaller sprites rather than describing a single rectangular crop.
- If a progress bar has rich interior texture, glow, or pattern, split it into a hollow `bar_track` component and a `bar_fill_texture` companion rendered at 100% fill width.
- If a component tiles or repeats, mark its tiling direction and use `tiled_repeat`.
- If a component has distinct visual states, create one entry per state.
- Use negative constraints to prevent generator drift.

## Output

Output only valid JSON.

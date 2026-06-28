# Prompt 03 - Generate UI Atlases

**Inputs:** `input/effect.png`, `spec.json`  
**Outputs:** one or more `atlas/*.png` files in the run directory  

You are a game UI sprite sheet artist. Generate game-ready UI sprite atlas images from the components in `spec.json`.

## Visual Reference

The attached effect image is the source style reference. Match its material, color tone, border thickness, trim, ornament vocabulary, bevels, glow, transparency, and texture detail. Use `spec.json` for structure and component identity. If the spec and image conflict on visual style, the image wins.

## Redraw Contract

- Do not crop rectangular regions from the source effect image and call them sprites.
- Do not use Pillow, canvas crop, screenshot crop, or any non-generative fallback to create atlas art.
- Each atlas entry must be a newly redrawn isolated sprite that preserves the source UI style.
- Complex UI is not rectangular cutting: border decoration, corner ornaments, bevels, drop shadows, glows, transparent holes, and rich material texture must be reconstructed around the component's actual shape.
- The source `source_bbox` is only a size and placement reference. It is not permission to cut that rectangle out of the effect image.
- If an available tool cannot redraw isolated sprites, stop and ask for an image-generation service instead of silently falling back to crop-based output.

## Atlas Rules

- Use transparent backgrounds for formal atlas files.
- Do not draw id labels, bbox labels, or cell labels into formal atlas files.
- You may produce separate debug/contact sheets for human viewing, but Phase 3 must use only formal atlas files.
- Prefer `1536x1024` or `1024x1536` when suitable, but custom canvas sizes and orientations are allowed.
- Do not reduce sprite resolution to fit a canvas.
- Preserve at least the source component resolution. Use the component's `resolution_policy.target_px`.
- Keep comfortable gutters: use each component's `atlas_policy.minimum_gutter`.
- Do not rotate components.
- Large panels, nine-slice frames, complex ornaments, resource orbs, and detailed bars may be isolated or grouped sparsely.
- Small related components may share sheets by group: slots, buttons, tabs, badges, bars, ornaments.
- Each isolated sprite must include all attached border decoration and ornaments declared in the spec.
- A `hollow` component must have transparent or empty center pixels, not a filled rectangle copied from the effect image.
- A `filled` component must use the source fill material and texture described in the spec.
- A `bar_fill_texture` component must be a full-width 100% fill texture with rich texture, glow, or pattern; a flat color is not acceptable.
- A `bar_track` component must remain hollow where the fill will be clipped in HTML.
- A `nine_slice` component must keep fixed corners in corner regions and produce stretchable edges/center.
- A `tiled_repeat` component must be designed as a seamless tile.

## Component Expansion Template

For each component from `spec.components[]`, expand the generation brief before creating the atlas:

```text
[N] {id} ({role})
  Source bbox : {source_bbox} for size reference only; do not crop it.
  Visual      : {visual_description}
  Decorations : {attached_decorations}
  Center      : {center}
    hollow -> transparent or empty center, zero fill.
    filled -> redraw fill material and texture from style reference.
  Render      : {render_pattern}
  Target px   : {resolution_policy.target_px}
  Atlas group : {atlas_policy.group}
  Notes       : preserve ornate border decoration, trim, bevel, glow, material texture, and silhouette.
```

## Output Naming

Use descriptive atlas filenames such as:

```text
atlas/atlas_panels_01.png
atlas/atlas_slots_01.png
atlas/atlas_buttons_01.png
atlas/atlas_bars_01.png
```

All visible UI components from `spec.components[]` must appear in exactly one formal atlas unless the component intentionally uses companions or states.

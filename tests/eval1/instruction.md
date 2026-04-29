# Web Design Replication

You are given a screenshot of a single-page website. Replicate the design as
faithfully as possible using HTML and CSS.

## Input

- `/app/reference.png` — a full-page screenshot of the target design, rendered
  at a 1280px viewport width. Open it with the `Read` tool to view it as an
  image. You may re-read it at any point if you need to recheck details.

## Output

Write a single file to `/app/output/index.html`. Create the `/app/output/`
directory if it does not yet exist. This is the only file your work will be
graded on; nothing else in `/app/` is read by the verifier.

## Constraints

- **One self-contained file.** All styles go in a single inline `<style>` block
  in the `<head>`. No external `.css` files.
- **No `<script>` tags.** The page must render correctly as static markup —
  the verifier does not execute JavaScript-driven content.
- **No external image URLs.** Use inline SVG, CSS shapes/gradients, or data-URI
  images for visual elements. References to remote `<img src="https://...">`
  will not load at verify time and will hurt your score.
- **Web fonts** are allowed only via a Google Fonts `<link>` in the `<head>`.
  Any other web fonts will not load.
- **Design for a 1280px-wide viewport.** The page may scroll vertically; the
  full page is rendered, not just the first fold.
- **Functionality is not required.** Links, forms, and buttons do not need to
  work — only the visual design matters.

## How your output is graded

Your `index.html` is rendered headlessly with Chromium at 1280px width
(full-page) and compared against the reference screenshot on four axes,
combined into a single continuous reward in `[0, 1]`. There is no pass/fail
threshold — closer to 1.0 is better.

| Weight | Axis | What it measures |
|--------|------|------------------|
| 0.40 | **Visual structural similarity** | Overall pixel-level resemblance (SSIM on grayscale). Rewards getting the broad shapes, contrast, and composition right. |
| 0.25 | **Colour palette match** | Distribution of colours across the page (earth-mover's distance over CIELAB k-means clusters). Match the dominant colours *and* their relative proportions. |
| 0.25 | **Layout block placement** | Bounding-box IoU of major content regions. Rewards correct position and size of headers, hero sections, columns, cards, and footers — even if their content is imperfect. |
| 0.10 | **Page height** | Penalises pages that are substantially taller or shorter than the reference. A page 50% too tall halves this term. |

### What this implies for your approach

- Get the overall **layout skeleton** right before polishing details — block
  placement and SSIM both reward this heavily.
- Match the **colour palette and its proportions**, not just the individual
  hues. A mostly-white page with a teal accent is very different from a
  mostly-teal page with white text, even if both palettes contain the same
  two colours.
- Aim for a **total page height** close to the reference. Avoid huge empty
  sections or aggressive padding that stretches the page.
- Pixel-perfect text fidelity is **not** required — the grader is robust to
  small font-rendering differences. Spend your effort on layout, colour, and
  spacing rather than chasing exact font metrics.

## Suggested workflow

1. `Read` `/app/reference.png` and study it: identify the layout regions
   (header, hero, content sections, footer), the dominant colours, the
   typography pairing, and the visual rhythm.
2. Sketch the structural outline mentally before writing markup.
3. Write `index.html` with inline `<style>`, working top-to-bottom through the
   page.
4. Re-read the reference image as needed to verify details you may have
   missed.
5. After you are satisfied with the result and want to quit, keep running in a loop for 
   2 minutes so that I can copy the html that has been generated

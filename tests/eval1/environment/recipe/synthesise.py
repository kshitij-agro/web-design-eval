"""HTML synthesis via the Anthropic API.

Given an (Archetype, Style, seed) triple, ask Claude Sonnet 4.6 to produce a
single self-contained index.html with the constraints from PLAN.md §5.3.

The generator is the eval-author's tool, so it runs locally (not inside any
Harbor container). The output is consumed by render.py.
"""

from __future__ import annotations

import os
import random
import re
from dataclasses import dataclass

from anthropic import Anthropic

from recipe.archetypes import Archetype, Style

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 900


SYSTEM_PROMPT = """You are a senior product designer and front-end engineer who builds polished, realistic single-page websites in pure HTML and CSS.

Your output MUST be a single self-contained `index.html` file that satisfies every rule below. Treat these as hard constraints — if any one is violated, the output is rejected.

HARD CONSTRAINTS
1. Output exactly one HTML document. No surrounding prose, no markdown fences in the actual response, just the raw HTML starting with `<!DOCTYPE html>`.
2. All CSS goes inside a single `<style>` block in `<head>`. Do not link external CSS files.
3. No `<script>` tags. No JavaScript anywhere. Static markup only.
4. No external images via `<img src="https://...">`. Allowed image sources: inline SVG (`<svg>...</svg>`), CSS gradients/colours, or `data:` URIs (only for tiny icons — keep total HTML well under 200 KB).
5. Web fonts are allowed ONLY via Google Fonts `<link>` in `<head>`. No other external assets.
6. The page is designed for a {viewport_width}x{viewport_height} desktop viewport. Lay it out for that width specifically.
7. The page must look like a real, plausible website — realistic copy, varied section sizes, deliberate visual hierarchy. Do NOT produce a wireframe with placeholder text like "Lorem ipsum" or "Heading 1".
8. The HTML must be valid and parseable. Close all tags.

DESIGN GUIDANCE
- Match the requested archetype's section list precisely; every section listed must be present and recognisable in the rendered output.
- Match the requested style's visual language: palette, typography, spacing, ornamentation.
- Use the random seed in the user prompt to vary palette, copy and minor layout choices, so different seeds produce visibly different pages.
- Include realistic-looking specifics (product names, headlines, prices, names in testimonials, etc.). They do not have to correspond to real entities.
- Use concrete colours — pick a palette and stick to it.
"""


USER_PROMPT_TEMPLATE = """Generate the website now.

Archetype: {archetype_title} ({archetype_slug})
Required sections (in order, top to bottom): {sections}
Archetype description:
{archetype_description}

Style: {style_title} ({style_slug})
Style description:
{style_description}

Random seed: {seed}
Use this seed to vary palette, copy, brand name, and any minor layout choices. Two different seeds with the same archetype+style should produce visibly different pages.

Brand/company name: invent something appropriate to the archetype and style.

Remember:
- Output ONLY the raw HTML document, starting with `<!DOCTYPE html>`.
- No explanations before or after.
- No `<script>` tags.
- No external images. SVG / CSS / data URIs only.
- Designed for a {viewport_width}x{viewport_height} viewport.
"""


@dataclass(frozen=True)
class SynthSpec:
    archetype: Archetype
    style: Style
    seed: int

    @property
    def slug(self) -> str:
        return f"{self.archetype.slug}-{self.style.slug}-{self.seed}"


def _build_messages(spec: SynthSpec) -> tuple[str, list[dict]]:
    rng = random.Random(spec.seed)
    # surface a small palette nudge in the user prompt to encourage variation
    accent_hint = rng.choice(
        [
            "warm",
            "cool",
            "earthy",
            "vivid",
            "monochromatic",
            "pastel",
            "high-contrast",
        ]
    )
    user = USER_PROMPT_TEMPLATE.format(
        archetype_title=spec.archetype.title,
        archetype_slug=spec.archetype.slug,
        archetype_description=spec.archetype.description,
        sections=", ".join(spec.archetype.sections),
        style_title=spec.style.title,
        style_slug=spec.style.slug,
        style_description=spec.style.description,
        seed=spec.seed,
        viewport_width=VIEWPORT_WIDTH,
        viewport_height=VIEWPORT_HEIGHT,
    )
    user += f"\nPalette mood for this seed: {accent_hint}.\n"
    system = SYSTEM_PROMPT.format(
        viewport_width=VIEWPORT_WIDTH, viewport_height=VIEWPORT_HEIGHT
    )
    return system, [{"role": "user", "content": user}]


def _strip_code_fences(text: str) -> str:
    """If the model wrapped the HTML in ``` fences anyway, strip them."""
    text = text.strip()
    if text.startswith("```"):
        # remove first fence line
        text = re.sub(r"^```(?:html)?\s*\n", "", text, count=1)
        if text.endswith("```"):
            text = text[: -len("```")].rstrip()
    return text


def synthesise_html(spec: SynthSpec, *, client: Anthropic | None = None) -> str:
    """Call Claude and return the raw HTML string."""
    if client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set in the environment")
        client = Anthropic(api_key=api_key)

    system, messages = _build_messages(spec)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=messages,
    )
    # join all text blocks (usually one)
    parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    raw = "\n".join(parts)
    return _strip_code_fences(raw)

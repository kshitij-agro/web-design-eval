"""Post-generation validation.

We can't fully trust the LLM to honour every constraint, so we do two passes:

1. **HTML check** — parse with BeautifulSoup, reject `<script>` tags, reject
   external `<img src="http...">`, require non-trivial body content.
2. **PNG check** — open with Pillow, reject blanks/near-monochromes
   (stddev too low), and bound the rendered height to a sane range.

Anything that fails raises `GenerationRejected` with a reason; the pipeline
catches that and re-rolls with a different seed.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image, ImageStat

from recipe.synthesise import VIEWPORT_HEIGHT, VIEWPORT_WIDTH


class GenerationRejected(Exception):
    """Raised when generated artefacts fail a validation check."""


# --- HTML --------------------------------------------------------------------

MIN_BODY_TEXT_CHARS = 200
MAX_HTML_BYTES = 300_000


def validate_html(html: str) -> None:
    """Reject HTML that violates the hard constraints."""
    if not html.lstrip().lower().startswith("<!doctype html"):
        raise GenerationRejected("HTML does not start with <!DOCTYPE html>")

    if len(html.encode("utf-8")) > MAX_HTML_BYTES:
        raise GenerationRejected(
            f"HTML exceeds {MAX_HTML_BYTES} bytes ({len(html.encode('utf-8'))})"
        )

    soup = BeautifulSoup(html, "html.parser")

    if soup.find("script") is not None:
        raise GenerationRejected("HTML contains a <script> tag (forbidden)")

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith(("http://", "https://", "//")):
            raise GenerationRejected(
                f"HTML contains an external image src: {src[:80]}"
            )

    body = soup.find("body")
    if body is None:
        raise GenerationRejected("HTML has no <body>")

    body_text = body.get_text(" ", strip=True)
    if len(body_text) < MIN_BODY_TEXT_CHARS:
        raise GenerationRejected(
            f"Body text is too short ({len(body_text)} < {MIN_BODY_TEXT_CHARS} chars)"
        )


# --- PNG ---------------------------------------------------------------------

MIN_HEIGHT_PX = VIEWPORT_HEIGHT  # full_page must be at least one viewport tall
MAX_HEIGHT_PX = VIEWPORT_HEIGHT * 8  # absurdly tall pages are usually broken
MIN_PIXEL_STDDEV = 12.0  # near-blank/monochrome pages have tiny stddev


def validate_png(png_path: Path) -> None:
    """Reject screenshots that are blank, monochrome, or wrong size."""
    with Image.open(png_path) as img:
        if img.width != VIEWPORT_WIDTH:
            raise GenerationRejected(
                f"PNG width {img.width} != expected {VIEWPORT_WIDTH}"
            )
        if not (MIN_HEIGHT_PX <= img.height <= MAX_HEIGHT_PX):
            raise GenerationRejected(
                f"PNG height {img.height} out of range "
                f"[{MIN_HEIGHT_PX}, {MAX_HEIGHT_PX}]"
            )

        rgb = img.convert("RGB")
        stat = ImageStat.Stat(rgb)
        # stat.stddev is per-channel; use mean across channels.
        avg_stddev = sum(stat.stddev) / len(stat.stddev)
        if avg_stddev < MIN_PIXEL_STDDEV:
            raise GenerationRejected(
                f"PNG appears near-monochrome (avg stddev {avg_stddev:.2f} "
                f"< {MIN_PIXEL_STDDEV})"
            )


def png_summary(png_path: Path) -> dict:
    """Return a small dict of stats for logging/debugging."""
    with Image.open(png_path) as img:
        rgb = img.convert("RGB")
        stat = ImageStat.Stat(rgb)
        return {
            "width": img.width,
            "height": img.height,
            "size_bytes": png_path.stat().st_size,
            "mean_rgb": [round(c, 1) for c in stat.mean],
            "stddev_rgb": [round(c, 1) for c in stat.stddev],
        }


# Useful for tests
__all__ = [
    "GenerationRejected",
    "validate_html",
    "validate_png",
    "png_summary",
]

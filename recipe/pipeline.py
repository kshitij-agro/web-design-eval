"""Generator pipeline: synth → validate HTML → render → validate PNG → write.

Outputs (per call) under <output_dir>/<slug>/:
    index.html         — the LLM-generated reference HTML
    reference.png      — the rendered screenshot
    spec.json          — record of (archetype, style, seed, model, attempt)

On rejection (HTML or PNG validation fails), retry up to MAX_ATTEMPTS times
with successive seeds derived from the original.

This module is the eval-author's tool. It runs locally, not inside any
Harbor container.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

from anthropic import Anthropic

from recipe.archetypes import ARCHETYPE_BY_SLUG, STYLE_BY_SLUG
from recipe.render import render_html_to_png
from recipe.synthesise import MODEL, SynthSpec, synthesise_html
from recipe.validate import (
    GenerationRejected,
    png_summary,
    validate_html,
    validate_png,
)

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 3


@dataclass(frozen=True)
class GenerationResult:
    spec: SynthSpec
    output_dir: Path
    html_path: Path
    png_path: Path
    spec_path: Path
    attempts: int
    png_stats: dict


def _seed_for_attempt(base_seed: int, attempt: int) -> int:
    # deterministic, but distinct, per attempt
    return base_seed * 1000 + attempt


def generate_one(
    archetype_slug: str,
    style_slug: str,
    seed: int,
    output_dir: Path,
    *,
    client: Anthropic | None = None,
) -> GenerationResult:
    """Generate one (archetype, style, seed) task asset.

    Returns paths and metadata. Raises if all attempts fail.
    """
    if archetype_slug not in ARCHETYPE_BY_SLUG:
        raise ValueError(f"Unknown archetype: {archetype_slug}")
    if style_slug not in STYLE_BY_SLUG:
        raise ValueError(f"Unknown style: {style_slug}")

    archetype = ARCHETYPE_BY_SLUG[archetype_slug]
    style = STYLE_BY_SLUG[style_slug]

    spec = SynthSpec(archetype=archetype, style=style, seed=seed)
    target = output_dir / spec.slug
    target.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        attempt_seed = _seed_for_attempt(seed, attempt)
        attempt_spec = SynthSpec(archetype=archetype, style=style, seed=attempt_seed)
        log.info(
            "Attempt %d/%d for %s (seed=%d)",
            attempt,
            MAX_ATTEMPTS,
            spec.slug,
            attempt_seed,
        )

        t0 = time.time()
        try:
            html = synthesise_html(attempt_spec, client=client)
            validate_html(html)

            html_path = target / "index.html"
            png_path = target / "reference.png"
            html_path.write_text(html, encoding="utf-8")
            render_html_to_png(html, png_path)
            validate_png(png_path)
        except GenerationRejected as e:
            log.warning("Rejected: %s", e)
            last_error = e
            continue
        # Don't retry on unexpected errors — that wastes API calls on bugs.
        # Let them bubble up so the caller fixes them.

        elapsed = time.time() - t0
        stats = png_summary(png_path)
        spec_path = target / "spec.json"
        spec_path.write_text(
            json.dumps(
                {
                    "archetype": archetype_slug,
                    "style": style_slug,
                    "base_seed": seed,
                    "attempt": attempt,
                    "attempt_seed": attempt_seed,
                    "model": MODEL,
                    "elapsed_sec": round(elapsed, 2),
                    "png": stats,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        log.info(
            "Generated %s in %.1fs (attempt %d) — %dx%d, %d bytes",
            spec.slug,
            elapsed,
            attempt,
            stats["width"],
            stats["height"],
            stats["size_bytes"],
        )
        return GenerationResult(
            spec=spec,
            output_dir=target,
            html_path=html_path,
            png_path=png_path,
            spec_path=spec_path,
            attempts=attempt,
            png_stats=stats,
        )

    raise RuntimeError(
        f"Failed to generate {spec.slug} after {MAX_ATTEMPTS} attempts: {last_error}"
    )

"""CLI entry point for the generator.

Examples:

    # generate a single (archetype, style, seed)
    uv run python -m recipe.cli \\
        --archetype landing --style minimalist --seed 42 \\
        --output web-design/tasks

    # list known archetypes / styles
    uv run python -m recipe.cli --list
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from recipe.archetypes import ARCHETYPES, STYLES
from recipe.pipeline import generate_one


def _list_catalogue() -> None:
    print("Archetypes:")
    for a in ARCHETYPES:
        print(f"  {a.slug:22s}  {a.title}")
    print("\nStyles:")
    for s in STYLES:
        print(f"  {s.slug:22s}  {s.title}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="recipe",
        description="Generate a reference website asset (HTML + PNG) for a Harbor task.",
    )
    parser.add_argument("--archetype", help="archetype slug (see --list)")
    parser.add_argument("--style", help="style slug (see --list)")
    parser.add_argument("--seed", type=int, help="integer seed for variation")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("web-design/tasks"),
        help="parent directory; per-task slug appended (default: web-design/tasks)",
    )
    parser.add_argument(
        "--list", action="store_true", help="list known archetypes and styles"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="DEBUG-level logging"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    if args.list:
        _list_catalogue()
        return 0

    missing = [
        name for name in ("archetype", "style", "seed") if getattr(args, name) is None
    ]
    if missing:
        parser.error(f"missing required argument(s): {', '.join('--' + m for m in missing)}")

    result = generate_one(
        archetype_slug=args.archetype,
        style_slug=args.style,
        seed=args.seed,
        output_dir=args.output,
    )
    print(f"\nGenerated: {result.output_dir}")
    print(f"  html: {result.html_path}")
    print(f"  png:  {result.png_path}")
    print(f"  spec: {result.spec_path}")
    print(f"  attempts: {result.attempts}")
    print(
        f"  png stats: {result.png_stats['width']}x{result.png_stats['height']}, "
        f"{result.png_stats['size_bytes']} bytes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

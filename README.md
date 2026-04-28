# web-design-eval

Scalable RL-environment recipe that generates Harbor tasks for grading a
coding agent's ability to replicate a website screenshot in HTML+CSS.

See [`PLAN.md`](./PLAN.md) for the full design — Harbor task contract, recipe
flow, screenshot delivery, continuous grader, and open questions.

## What's here so far

- `recipe/` — the generator pipeline (Phase 1 of the recipe).
- `web-design/` — the Harbor task template (still mostly stubs) and
  `web-design/tasks/<slug>/` for generated assets.
- `pyproject.toml` — uv-managed dependencies (`anthropic`, `playwright`,
  `Pillow`, `beautifulsoup4`).

## Setup

Requirements: Python 3.11+, [`uv`](https://docs.astral.sh/uv/), and an
`ANTHROPIC_API_KEY` in your environment.

```bash
# install deps into the existing test/ venv
UV_PROJECT_ENVIRONMENT=test uv sync

# fetch Playwright's bundled Chromium (one-time)
UV_PROJECT_ENVIRONMENT=test uv run playwright install chromium

# from here on, activate the venv so plain `python` works
source test/bin/activate
```

If the venv isn't activated, prefix any command with
`UV_PROJECT_ENVIRONMENT=test uv run` instead.

## Running the generator

The generator takes an `(archetype, style, seed)` triple and produces:

```
web-design/tasks/<archetype>-<style>-<seed>/
├── index.html        # LLM-generated reference HTML
├── reference.png     # full-page screenshot at 1280×900
└── spec.json         # archetype, style, seed, model, render stats
```

### List available archetypes and styles

```bash
python -m recipe.cli --list
```

### Generate one task

```bash
python -m recipe.cli \
    --archetype landing \
    --style minimalist \
    --seed 42 \
    --output web-design/tasks
```

### A few more examples

```bash
# pricing page in glassmorphism
python -m recipe.cli --archetype pricing --style glassmorphism --seed 7 --output web-design/tasks

# news homepage in editorial style
python -m recipe.cli --archetype news --style editorial --seed 13 --output web-design/tasks

# dashboard in dark-mode SaaS
python -m recipe.cli --archetype dashboard --style dark-saas --seed 99 --output web-design/tasks
```

### Verbose logging

```bash
python -m recipe.cli -v --archetype portfolio --style brutalist --seed 1 --output web-design/tasks
```

## What the generator does

1. **Synthesise** — calls Claude Sonnet 4.6 with a constrained prompt
   (`recipe/synthesise.py`); returns one self-contained `index.html` (inline
   CSS, no JS, no external images, optional Google Fonts).
2. **Validate HTML** — parses with BeautifulSoup; rejects forbidden patterns
   (`<script>`, external `<img src>`), enforces minimum body content
   (`recipe/validate.py`).
3. **Render** — Playwright (headless Chromium) opens `index.html`, takes a
   `full_page=True` screenshot at 1280×900 (`recipe/render.py`).
4. **Validate PNG** — Pillow checks dimensions and pixel-stddev to catch
   blank or near-monochrome renders.
5. **Stamp** — writes `index.html`, `reference.png`, `spec.json` into the
   per-task output directory.

If any validation step fails, the pipeline retries up to 3 times with
successive seeds derived from the original.

## Inspecting a generated task

```bash
ls web-design/tasks/landing-minimalist-42/
cat web-design/tasks/landing-minimalist-42/spec.json
xdg-open web-design/tasks/landing-minimalist-42/reference.png   # or: feh / open
```

## Status

Phase 1 (generator) — done. Next: bundling generated assets into the Harbor
task layout, then the verifier/grader. See [`PLAN.md`](./PLAN.md) §11.

"""Archetype and style catalogues used by the generator.

Each entry has a short, generator-facing description that gets injected into
the synthesis prompt. The descriptions are deliberately concrete (concrete
sections, concrete visual language) so the LLM produces something rendered
and not just abstract markup.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Archetype:
    slug: str
    title: str
    description: str
    sections: tuple[str, ...]


@dataclass(frozen=True)
class Style:
    slug: str
    title: str
    description: str


ARCHETYPES: tuple[Archetype, ...] = (
    Archetype(
        slug="landing",
        title="SaaS landing page",
        description=(
            "Marketing landing page for a B2B SaaS product. Strong hero with "
            "headline, subhead and CTA buttons, trust strip with logos, three "
            "feature cards with icons, a testimonial, and a footer."
        ),
        sections=("nav", "hero", "logo strip", "features", "testimonial", "footer"),
    ),
    Archetype(
        slug="pricing",
        title="Pricing page",
        description=(
            "Pricing page with three plan tiers shown side by side, a feature "
            "comparison table below them, and an FAQ list at the bottom."
        ),
        sections=("nav", "page header", "three pricing cards", "comparison table", "FAQ", "footer"),
    ),
    Archetype(
        slug="blog-post",
        title="Long-form blog post",
        description=(
            "An editorial blog post with a centred narrow text column, a "
            "title/byline header, a hero image block, body paragraphs with "
            "occasional H2 subheads and a pull quote, and a related-posts grid."
        ),
        sections=("masthead", "post header", "hero image", "body", "pull quote", "related posts"),
    ),
    Archetype(
        slug="dashboard",
        title="Analytics dashboard",
        description=(
            "Static analytics dashboard with a left sidebar, top bar, four KPI "
            "stat cards in a row, a large chart card, and a smaller table card "
            "next to it. No interactivity."
        ),
        sections=("sidebar", "top bar", "KPI cards", "chart card", "table card"),
    ),
    Archetype(
        slug="portfolio",
        title="Designer portfolio",
        description=(
            "Single-page portfolio for a designer: large name/title hero, "
            "short bio paragraph, a 3-column grid of project cards each with a "
            "thumbnail block and caption, and a contact footer."
        ),
        sections=("intro hero", "bio", "project grid", "contact footer"),
    ),
    Archetype(
        slug="ecommerce-product",
        title="E-commerce product page",
        description=(
            "Single product detail page: large product image on the left, "
            "title/price/buy column on the right, tabs-styled description block "
            "below, and a 'you may also like' grid of four related products."
        ),
        sections=("nav", "product image", "buy column", "description block", "related products"),
    ),
    Archetype(
        slug="login",
        title="Login form page",
        description=(
            "Centred login card on a coloured/gradient background. Card has "
            "logo, title, email + password fields, primary button, social-login "
            "row, and a 'sign up' link below. Minimal chrome around it."
        ),
        sections=("background", "centred login card"),
    ),
    Archetype(
        slug="news",
        title="News homepage",
        description=(
            "Newspaper-style homepage with a thick masthead, a lead story with "
            "a large headline and image, a 2-column secondary stories area, "
            "and a 4-column grid of smaller story tiles below."
        ),
        sections=("masthead", "lead story", "secondary stories", "tile grid", "footer"),
    ),
    Archetype(
        slug="contact",
        title="Contact page",
        description=(
            "Two-column contact page: a contact form on the left with name/"
            "email/message fields, and an info column on the right with "
            "address block, phone, email and a small map placeholder."
        ),
        sections=("nav", "page header", "contact form", "info column", "footer"),
    ),
    Archetype(
        slug="app-marketing",
        title="Mobile app marketing page",
        description=(
            "Marketing page for a mobile app. Hero shows a phone mockup next "
            "to headline + app-store buttons. Then a 3-up benefits row, a "
            "feature spotlight with alternating image/text rows, and a final "
            "CTA band before the footer."
        ),
        sections=("nav", "hero with phone mockup", "benefits row", "feature spotlight", "CTA band", "footer"),
    ),
)


STYLES: tuple[Style, ...] = (
    Style(
        slug="minimalist",
        title="Minimalist editorial",
        description=(
            "Lots of whitespace, neutral palette (off-white background, near-"
            "black text, a single restrained accent), serif or grotesque sans, "
            "thin hairlines, generous typographic scale."
        ),
    ),
    Style(
        slug="brutalist",
        title="Web-brutalist",
        description=(
            "High-contrast, raw aesthetic. Visible borders, system or mono "
            "fonts, oversized type, hard edges, primary colours used boldly, "
            "intentionally unpolished spacing."
        ),
    ),
    Style(
        slug="glassmorphism",
        title="Glassmorphism / soft tech",
        description=(
            "Frosted-glass cards with translucency, soft drop shadows, gentle "
            "gradient backgrounds (lavender/teal/peach), rounded corners, "
            "modern geometric sans like Inter."
        ),
    ),
    Style(
        slug="retro",
        title="Retro 80s/90s",
        description=(
            "Nostalgic aesthetic: chunky bordered boxes, drop-shadow text, "
            "vibrant teal/magenta/yellow palette, monospace or display fonts, "
            "occasional grid patterns or scanline accents."
        ),
    ),
    Style(
        slug="dark-saas",
        title="Dark-mode SaaS",
        description=(
            "Near-black background (#0b0d10-ish), bright accent colour for "
            "CTAs, glowing button effects, modern sans, dimmed surface cards, "
            "subtle grid or dot background."
        ),
    ),
    Style(
        slug="editorial",
        title="Editorial / magazine",
        description=(
            "Magazine-influenced layout: serif display headlines, multi-column "
            "text where appropriate, generous leading, asymmetric image "
            "placements, warm off-white background and dark ink."
        ),
    ),
)


ARCHETYPE_BY_SLUG: dict[str, Archetype] = {a.slug: a for a in ARCHETYPES}
STYLE_BY_SLUG: dict[str, Style] = {s.slug: s for s in STYLES}

"""Shared look for the README graphics, built on GitHub's own Primer design tokens.

Cards are flat boxes with hairline borders and no fill, so they sit on the page like
GitHub's own UI in light, dark, and dark dimmed themes.
"""

import json
from pathlib import Path
from xml.sax.saxutils import escape

W = 1000
GAP = 24  # gutter between cards; ~matches the gap GitHub leaves between stacked images
PAD = 32  # inner padding of every card
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

_icons = json.loads((Path(__file__).parent / "icons.json").read_text())
BRANDS, LUCIDE = _icons["brands"], _icons["lucide"]

# Primer functional colours (github.com light / dark default).
THEMES = {
    "dark": {
        "fg": "#f0f6fc",
        "muted": "#9198a1",
        "faint": "#656c76",
        "border": "#3d444d",
        "card": "rgba(110,118,129,0.035)",
        "btn": "#212830",
        "primary": "#4493f8",
        "primary_soft": "rgba(56,139,253,0.15)",
        "green": "#3fb950",
        "heat": ["rgba(110,118,129,0.14)", "#033a16", "#196c2e", "#2ea043", "#56d364"],
    },
    "light": {
        "fg": "#1f2328",
        "muted": "#59636e",
        "faint": "#818b98",
        "border": "#d1d9e0",
        "card": "rgba(208,215,222,0.08)",
        "btn": "#f6f8fa",
        "primary": "#0969da",
        "primary_soft": "#ddf4ff",
        "green": "#1a7f37",
        "heat": ["#eff2f5", "#aceebb", "#4ac26b", "#2da44e", "#116329"],
    },
}

BASE_CSS = f"""
text {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
@keyframes pulse {{ 0% {{ opacity: .6; transform: scale(1); }} 100% {{ opacity: 0; transform: scale(2.4); }} }}
.rise {{ opacity: 0; animation: rise .6s cubic-bezier(.25,.46,.45,.94) forwards; }}
.fade {{ opacity: 0; animation: fade .5s ease-out forwards; }}
.pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse 2s ease-out infinite; }}
@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; }}
  .rise, .fade {{ opacity: 1; }}
}}
"""


def svg(t, width, height, body, css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none">\n'
        f"<style>{BASE_CSS}{css}</style>\n<defs>{defs}</defs>\n{body}\n</svg>\n"
    )


def icon(name, x, y, size, color, width=2):
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({size / 24})" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="none">{LUCIDE[name]}</g>'
    )


def brand(name, x, y, size, color, opacity=1):
    return (
        f'<path transform="translate({x:.1f} {y:.1f}) scale({size / 24})" d="{BRANDS[name]}" '
        f'fill="{color}" fill-opacity="{opacity}"/>'
    )


def delay(i, step=0.1, base=0.05):
    return f'style="animation-delay:{base + i * step:.2f}s"'


def cell(t, x, y, w, h, rx=12):
    """GitHub 'Box': hairline border, near-transparent fill."""
    return (
        f'<rect x="{x + .5:.1f}" y="{y + .5:.1f}" width="{w - 1:.1f}" height="{h - 1:.1f}" rx="{rx}" '
        f'fill="{t["card"]}" stroke="{t["border"]}"/>'
    )


def heading(t, x, y, text, icon_name=None):
    """Card title in GitHub's sentence-case style, with an optional muted icon."""
    out = ""
    if icon_name:
        out += icon(icon_name, x, y - 13, 16, t["muted"])
        x += 24
    return out + f'<text x="{x:.1f}" y="{y}" font-size="15" font-weight="600" fill="{t["fg"]}">{escape(text)}</text>'


def sublabel(t, x, y, text, anchor="start"):
    """Small muted caption for sub-sections and right-aligned hints."""
    return (
        f'<text x="{x:.1f}" y="{y}" font-size="12.5" font-weight="600" text-anchor="{anchor}" '
        f'fill="{t["muted"]}">{escape(text)}</text>'
    )


def graph_backdrop(t, w, h, rx=12, seed=7):
    """Faint contribution-graph squares at both edges, fading out towards the centre."""
    step, size = 15, 11
    cols, rows = int(w // step), int(h // step)
    x0, y0 = (w - cols * step + step - size) / 2, (h - rows * step + step - size) / 2
    edge = cols * 0.26
    rng = seed
    rects = []
    for c in range(cols):
        dist = min(c, cols - 1 - c)
        if dist > edge:
            continue
        for r in range(rows):
            rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
            roll = rng % 100
            level = 0 if roll < 45 else 1 if roll < 68 else 2 if roll < 84 else 3 if roll < 95 else 4
            op = max(0.0, 1 - dist / edge) ** 1.4 * (0.38 if level else 0.6)
            if op < 0.05:
                continue
            rects.append(
                f'<rect x="{x0 + c * step:.1f}" y="{y0 + r * step:.1f}" width="{size}" height="{size}" rx="2.5" '
                f'fill="{t["heat"][level]}" fill-opacity="{op:.2f}"/>'
            )
    return (
        f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>'
        f'<g clip-path="url(#frame)" class="fade" style="animation-duration:1.2s">{"".join(rects)}</g>'
        + cell(t, 0, 0, w, h, rx)
    )

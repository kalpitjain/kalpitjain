"""Shared look for the README graphics: kalpitjain.dev's navy + blue palette."""

import json
from pathlib import Path
from xml.sax.saxutils import escape

W = 1000
GAP = 16
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

_icons = json.loads((Path(__file__).parent / "icons.json").read_text())
BRANDS, LUCIDE = _icons["brands"], _icons["lucide"]

THEMES = {
    "dark": {
        "bg": "#080c16",
        "card": "#0e1522",
        "card_hi": "#131c2d",
        "fg": "#eef2f7",
        "muted": "#8a99ad",
        "faint": "#5d6b80",
        "border": "#223049",
        "primary": "#3b82f6",
        "primary_soft": "#12203a",
        "shine": "#93c5fd",
        "green": "#34d399",
        "glow": 0.22,
        "blob": 1.0,
        "heat": ["#1b2436", "#1c3366", "#1e40af", "#2f6fe8", "#7cb4fb"],
    },
    "light": {
        "bg": "#f4f6fa",
        "card": "#ffffff",
        "card_hi": "#f7f9fd",
        "fg": "#121826",
        "muted": "#58606f",
        "faint": "#8b95a5",
        "border": "#d9e0ea",
        "primary": "#3b82f6",
        "primary_soft": "#e8f0fe",
        "shine": "#1d4ed8",
        "green": "#10b981",
        "glow": 0.12,
        "blob": 0.5,
        "heat": ["#e9eef6", "#c7dbfd", "#93c5fd", "#3b82f6", "#1d4ed8"],
    },
}

BASE_CSS = f"""
text {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
@keyframes pulse {{ 0% {{ opacity: .7; transform: scale(1); }} 100% {{ opacity: 0; transform: scale(2.6); }} }}
@keyframes drift1 {{ 0%, 100% {{ transform: translate(0, 0); }} 50% {{ transform: translate(70px, 30px); }} }}
@keyframes drift2 {{ 0%, 100% {{ transform: translate(0, 0); }} 50% {{ transform: translate(-80px, -25px); }} }}
.rise {{ opacity: 0; animation: rise .7s cubic-bezier(.25,.46,.45,.94) forwards; }}
.fade {{ opacity: 0; animation: fade .5s ease-out forwards; }}
.pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse 2s ease-out infinite; }}
.d1 {{ animation: drift1 14s ease-in-out infinite; }}
.d2 {{ animation: drift2 17s ease-in-out infinite; }}
@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; }}
  .rise, .fade {{ opacity: 1; }}
}}
"""


def shared_defs(t):
    """Gradients every card uses: glass fill, gradient edge, corner glow."""
    return f"""
<linearGradient id="fill" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{t['card_hi']}"/><stop offset="1" stop-color="{t['card']}"/>
</linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{t['primary']}" stop-opacity=".5"/>
  <stop offset=".45" stop-color="{t['border']}"/>
  <stop offset="1" stop-color="{t['border']}"/>
</linearGradient>
<radialGradient id="glow" cx="0" cy="0" r="1">
  <stop offset="0" stop-color="{t['primary']}" stop-opacity="{t['glow']}"/>
  <stop offset="1" stop-color="{t['primary']}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="glow-br" cx="1" cy="1" r="1">
  <stop offset="0" stop-color="#60a5fa" stop-opacity="{t['glow'] * 0.8:.2f}"/>
  <stop offset="1" stop-color="#60a5fa" stop-opacity="0"/>
</radialGradient>
<linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="440" y2="0" spreadMethod="reflect">
  <stop offset="0" stop-color="{t['primary']}"/><stop offset=".5" stop-color="{t['shine']}"/><stop offset="1" stop-color="{t['primary']}"/>
  <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="880 0" dur="6s" repeatCount="indefinite"/>
</linearGradient>
"""


def svg(t, width, height, body, css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none">\n'
        f"<style>{BASE_CSS}{css}</style>\n<defs>{shared_defs(t)}{defs}</defs>\n{body}\n</svg>\n"
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


def delay(i, step=0.12, base=0.1):
    return f'style="animation-delay:{base + i * step:.2f}s"'


def cell(x, y, w, h, rx=20, glow="tl"):
    """Glass card: gradient fill, soft corner glow, gradient hairline edge."""
    glow_fill = {"tl": "url(#glow)", "br": "url(#glow-br)"}.get(glow)
    out = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="url(#fill)"/>'
    if glow_fill:
        out += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{glow_fill}"/>'
    out += (
        f'<rect x="{x + .5:.1f}" y="{y + .5:.1f}" width="{w - 1:.1f}" height="{h - 1:.1f}" rx="{rx - .5}" '
        f'stroke="url(#edge)"/>'
    )
    return out


def label(t, x, y, text, icon_name=None):
    """Small uppercase mono eyebrow used at the top of each card."""
    out = ""
    if icon_name:
        out += icon(icon_name, x, y - 11, 14, t["primary"])
        x += 22
    return out + (
        f'<text class="mono" x="{x:.1f}" y="{y}" font-size="11.5" font-weight="600" letter-spacing="1.8" '
        f'fill="{t["muted"]}">{escape(text)}</text>'
    )


def backdrop(t, h, rx, blobs):
    """Navy panel with drifting blurred glows and a faint dot grid (for hero-style panels)."""
    defs = f"""
<clipPath id="frame"><rect width="{W}" height="{h}" rx="{rx}"/></clipPath>
<filter id="blur" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="55"/></filter>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{t['fg']}" fill-opacity=".07"/></pattern>
"""
    circles = "".join(
        f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}" fill="{color}" fill-opacity="{op * t["blob"]:.2f}"/>'
        for cls, cx, cy, r, color, op in blobs
    )
    body = (
        f'<g clip-path="url(#frame)"><rect width="{W}" height="{h}" fill="{t["bg"]}"/>'
        f'<rect width="{W}" height="{h}" fill="url(#dots)"/>'
        f'<g filter="url(#blur)">{circles}</g></g>'
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{h - 1.5}" rx="{rx - 0.75}" stroke="url(#edge)" stroke-width="1.5"/>'
    )
    return defs, body

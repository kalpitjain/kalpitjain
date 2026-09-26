"""Compose the whole profile into one SVG per theme, so every gap between cards is identical.

Separate <img>s can't do this: GitHub puts a fixed CSS gap between images, while gaps
drawn inside an image scale with the page width, so the two never match.

In CI:   GITHUB_TOKEN=... python3 scripts/build.py --user kalpitjain --out dist
Locally: python3 scripts/build.py --calendar days.json --out preview
         (days.json is a list of {"date": "YYYY-MM-DD", "count": N})
"""

import argparse
import json
import os
import re
from pathlib import Path

import activity
from generate import banner, bento_about, bento_highlights, signoff, toolbox
from theme import BASE_CSS, GAP, THEMES, W


def parts(markup):
    """Split one of our generated SVGs into (height, extra css, defs, body)."""
    height = float(re.search(r'<svg[^>]* height="([\d.]+)"', markup).group(1))
    css = re.search(r"<style>(.*?)</style>", markup, re.S).group(1).replace(BASE_CSS, "")
    defs = re.search(r"<defs>(.*?)</defs>", markup, re.S).group(1)
    body = re.search(r"</defs>\n(.*)\n</svg>", markup, re.S).group(1)
    return height, css, defs, body


def compose(t, stats):
    sections = [
        banner(t),
        bento_about(t),
        bento_highlights(t),
        toolbox(t),
        activity.card(t, stats),
        signoff(t),
    ]
    y, css, defs, bodies = 0.0, [], [], []
    for markup in sections:
        h, extra_css, extra_defs, body = parts(markup)
        css.append(extra_css)
        defs.append(extra_defs)
        bodies.append(f'<g transform="translate(0 {y:.1f})">\n{body}\n</g>')
        y += h + GAP
    height = y - GAP
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height:.0f}" '
        f'viewBox="0 0 {W} {height:.0f}" fill="none">\n'
        f"<style>{BASE_CSS}{''.join(css)}</style>\n<defs>{''.join(defs)}</defs>\n"
        + "\n".join(bodies)
        + "\n</svg>\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="kalpitjain")
    ap.add_argument("--calendar", help="JSON file of {date, count} instead of calling the API")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()

    if args.calendar:
        days = json.loads(Path(args.calendar).read_text())
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("Set GITHUB_TOKEN or pass --calendar")
        days = activity.fetch_calendar(args.user, token)

    stats = activity.summarize(days)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme, tokens in THEMES.items():
        (out / f"profile-{theme}.svg").write_text(compose(tokens, stats))
    print(f"total={stats['total']} current={stats['current']} longest={stats['longest']} -> {out}")


if __name__ == "__main__":
    main()

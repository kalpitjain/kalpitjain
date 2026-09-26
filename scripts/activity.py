"""Render the contributions card (dark + light) from the contribution calendar.

In CI:   GITHUB_TOKEN=... python3 scripts/activity.py --user kalpitjain --out dist
Locally: python3 scripts/activity.py --calendar days.json --out assets
         (days.json is a list of {"date": "YYYY-MM-DD", "count": N})
"""

import argparse
import json
import os
import urllib.request
from datetime import date, timedelta
from pathlib import Path

from theme import GAP, THEMES, W, cell, delay, icon, label, svg

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def fetch_calendar(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.load(res)
    if "errors" in payload:
        raise SystemExit(f"GitHub API error: {payload['errors']}")
    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]


def summarize(days):
    days = sorted(days, key=lambda d: d["date"])
    counts = [d["count"] for d in days]

    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)

    # Today may still be in progress, so a zero today doesn't break the streak.
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    current = 0
    for c in reversed(tail):
        if not c:
            break
        current += 1

    return {
        "days": days,
        "total": sum(counts),
        "current": current,
        "longest": longest,
        "best": max(counts, default=0),
        "active": sum(1 for c in counts if c),
        "updated": date.fromisoformat(days[-1]["date"]),
    }


def levels(counts):
    """GitHub-style 0–4 intensity using quartiles of the non-zero days."""
    nonzero = sorted(c for c in counts if c)
    if not nonzero:
        return lambda c: 0
    q = [nonzero[int(len(nonzero) * f)] for f in (0.25, 0.5, 0.75)]
    return lambda c: 0 if c == 0 else 1 + sum(c > x for x in q)


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def card(t, s):
    pad = 32
    tiles = [
        ("git-commit", f"{s['total']:,}", "Contributions"),
        ("flame", plural(s["current"], "day"), "Current streak"),
        ("trophy", plural(s["longest"], "day"), "Longest streak"),
        ("zap", f"{s['active']}", "Active days"),
    ]
    tile_y, tile_h = 0, 96
    tile_w = (W - GAP * 3) / 4

    # Heatmap: weeks as columns, Sunday-first rows, like GitHub's graph.
    days = s["days"]
    first = date.fromisoformat(days[0]["date"])
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = ((date.fromisoformat(days[-1]["date"]) - start).days // 7) + 1
    step = (W - pad * 2 + 3) / weeks
    size = step - 3
    heat_top = tile_h + GAP + 96
    heat_h = 7 * step - 3
    h = heat_top + heat_h + 64
    lvl = levels([d["count"] for d in days])

    body = []
    for i, (ic, value, text) in enumerate(tiles):
        x = i * (tile_w + GAP)
        body += [
            f'<g class="rise" {delay(i, 0.08)}>',
            cell(x, tile_y, tile_w, tile_h, glow="tl" if i == 0 else None),
            f'<rect x="{x + 20:.1f}" y="{tile_y + 28}" width="40" height="40" rx="11" fill="{t["primary_soft"]}"/>',
            icon(ic, x + 30, tile_y + 38, 20, t["primary"]),
            f'<text x="{x + 74:.1f}" y="{tile_y + 48}" font-size="24" font-weight="800" letter-spacing="-.5" fill="{t["fg"]}">{value}</text>',
            f'<text x="{x + 74:.1f}" y="{tile_y + 69}" font-size="13" fill="{t["muted"]}">{text}</text>',
            "</g>",
        ]

    box_y = tile_h + GAP
    updated = s["updated"].strftime("%-d %b %Y")
    body += [
        cell(0, box_y, W, h - box_y, glow="br"),
        label(t, pad, box_y + 44, "CONTRIBUTIONS · PAST 12 MONTHS", "activity"),
        f'<text class="mono" x="{W - pad}" y="{box_y + 44}" font-size="11.5" letter-spacing="1" text-anchor="end" fill="{t["faint"]}">UPDATED {updated.upper()}</text>',
    ]

    seen = set()
    for d in days:
        day = date.fromisoformat(d["date"])
        offset = (day - start).days
        col, row = divmod(offset, 7)
        x = pad + col * step
        y = heat_top + row * step
        level = lvl(d["count"])
        body.append(
            f'<rect class="fade" style="animation-delay:{0.3 + col * 0.018 + row * 0.01:.3f}s" x="{x:.1f}" y="{y:.1f}" '
            f'width="{size:.1f}" height="{size:.1f}" rx="{size * 0.22:.1f}" fill="{t["heat"][level]}"/>'
        )
        # Month label above the first full week of each month.
        if day.day <= 7 and row == 0 and day.strftime("%Y-%m") not in seen and col < weeks - 2:
            seen.add(day.strftime("%Y-%m"))
            body.append(
                f'<text class="mono" x="{x:.1f}" y="{heat_top - 12}" font-size="11.5" fill="{t["muted"]}">{day.strftime("%b")}</text>'
            )

    legend_y = heat_top + heat_h + 34
    body.append(
        f'<text x="{pad}" y="{legend_y}" font-size="13" fill="{t["muted"]}">'
        f'<tspan fill="{t["fg"]}" font-weight="700">{s["total"]:,}</tspan> contributions · best day '
        f'<tspan fill="{t["fg"]}" font-weight="700">{s["best"]}</tspan></text>'
    )
    lx = W - pad - 5 * 17 - 40
    body.append(f'<text class="mono" x="{lx - 10}" y="{legend_y}" font-size="11.5" text-anchor="end" fill="{t["faint"]}">Less</text>')
    for i, color in enumerate(t["heat"]):
        body.append(f'<rect x="{lx + i * 17}" y="{legend_y - 11}" width="13" height="13" rx="3" fill="{color}"/>')
    body.append(f'<text class="mono" x="{lx + 5 * 17 + 6}" y="{legend_y}" font-size="11.5" fill="{t["faint"]}">More</text>')

    return svg(t, W, h, "\n".join(body))


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
        days = fetch_calendar(args.user, token)

    stats = summarize(days)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme, tokens in THEMES.items():
        (out / f"activity-{theme}.svg").write_text(card(tokens, stats))
    print(f"total={stats['total']} current={stats['current']} longest={stats['longest']} -> {out}")


if __name__ == "__main__":
    main()

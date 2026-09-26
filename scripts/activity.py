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

from theme import GAP, PAD, THEMES, W, cell, delay, icon, sublabel, svg

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
    pad = PAD
    tiles = [
        ("git-commit", f"{s['total']:,}", "Contributions"),
        ("flame", plural(s["current"], "day"), "Current streak"),
        ("trophy", plural(s["longest"], "day"), "Longest streak"),
        ("zap", f"{s['active']}", "Active days"),
    ]
    tile_h = 92
    tile_w = (W - GAP * 3) / 4

    # Heatmap: weeks as columns, Sunday-first rows, like GitHub's graph.
    days = s["days"]
    first = date.fromisoformat(days[0]["date"])
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = ((date.fromisoformat(days[-1]["date"]) - start).days // 7) + 1
    step = (W - pad * 2 + 3) / weeks
    size = step - 3
    box_y = tile_h + GAP
    heat_top = box_y + 96
    heat_h = 7 * step - 3
    h = heat_top + heat_h + 62
    lvl = levels([d["count"] for d in days])

    body = []
    for i, (ic, value, text) in enumerate(tiles):
        x = i * (tile_w + GAP)
        body += [
            f'<g class="rise" {delay(i, 0.08)}>',
            cell(t, x, 0, tile_w, tile_h),
            f'<text x="{x + 24:.1f}" y="44" font-size="22" font-weight="600" fill="{t["fg"]}">{value}</text>',
            f'<text x="{x + 24:.1f}" y="67" font-size="13" fill="{t["muted"]}">{text}</text>',
            icon(ic, x + tile_w - 24 - 18, 22, 18, t["muted"]),
            "</g>",
        ]

    updated = s["updated"].strftime("%-d %b %Y")
    body += [
        cell(t, 0, box_y, W, h - box_y),
        f'<text x="{pad}" y="{box_y + 46}" font-size="15" fill="{t["fg"]}"><tspan font-weight="600">{s["total"]:,}</tspan> contributions in the last year</text>',
        sublabel(t, W - pad, box_y + 46, f"Updated {updated}", "end"),
    ]

    seen = set()
    for d in days:
        day = date.fromisoformat(d["date"])
        col, row = divmod((day - start).days, 7)
        x = pad + col * step
        y = heat_top + row * step
        level = lvl(d["count"])
        body.append(
            f'<rect class="fade" style="animation-delay:{0.2 + col * 0.015 + row * 0.008:.3f}s" x="{x:.1f}" y="{y:.1f}" '
            f'width="{size:.1f}" height="{size:.1f}" rx="{size * 0.2:.1f}" fill="{t["heat"][level]}"/>'
        )
        # Month label above the first full week of each month.
        if day.day <= 7 and row == 0 and day.strftime("%Y-%m") not in seen and col < weeks - 2:
            seen.add(day.strftime("%Y-%m"))
            body.append(f'<text x="{x:.1f}" y="{heat_top - 11}" font-size="12" fill="{t["muted"]}">{day.strftime("%b")}</text>')

    legend_y = heat_top + heat_h + 34
    body.append(
        f'<text x="{pad}" y="{legend_y}" font-size="12.5" fill="{t["muted"]}">Best day: '
        f'<tspan fill="{t["fg"]}" font-weight="600">{s["best"]}</tspan> contributions</text>'
    )
    lx = W - pad - 5 * 16 - 36
    body.append(f'<text x="{lx - 8}" y="{legend_y}" font-size="12" text-anchor="end" fill="{t["muted"]}">Less</text>')
    for i, color in enumerate(t["heat"]):
        body.append(f'<rect x="{lx + i * 16}" y="{legend_y - 11}" width="12" height="12" rx="2.5" fill="{color}"/>')
    body.append(f'<text x="{lx + 5 * 16 + 4}" y="{legend_y}" font-size="12" fill="{t["muted"]}">More</text>')

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

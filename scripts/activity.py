"""Contribution data and the contributions card; composed into the profile by build.py."""

import json
import urllib.request
from datetime import date

from theme import GAP, W, cell, delay, icon, svg

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


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def card(t, s):
    """Four stat tiles. The contribution graph itself is left to GitHub, which shows it below the README."""
    tiles = [
        ("git-commit", f"{s['total']:,}", "Contributions, past year"),
        ("flame", plural(s["current"], "day"), "Current streak"),
        ("trophy", plural(s["longest"], "day"), "Longest streak"),
        ("calendar", f"{s['active']}", "Active days"),
    ]
    tile_h = 92
    tile_w = (W - GAP * 3) / 4

    body = []
    for i, (ic, value, text) in enumerate(tiles):
        x = i * (tile_w + GAP)
        body += [
            f'<g class="rise" {delay(i, 0.08)}>',
            cell(t, x, 0, tile_w, tile_h),
            f'<text x="{x + 24:.1f}" y="44" font-size="22" font-weight="600" fill="{t["fg"]}">{value}</text>',
            f'<text x="{x + 24:.1f}" y="67" font-size="13" fill="{t["muted"]}">{text}</text>',
            icon(ic, x + tile_w - 24 - 16, 24, 16, t["muted"]),
            "</g>",
        ]
    return svg(t, W, tile_h, "\n".join(body))

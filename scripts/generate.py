"""Generate the README's static graphics (dark + light) in ../assets.

Run: python3 scripts/generate.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

from theme import GAP, THEMES, W, backdrop, brand, cell, delay, icon, label, svg

OUT = Path(__file__).resolve().parent.parent / "assets"

# ── Banner ─────────────────────────────────────────────────────────────

# Same rotation as the kalpitjain.dev hero.
PHRASES = [
    "Software Engineer",
    "Turning ideas into products",
    "Solving problems end to end",
    "7× Hackathon Winner",
]


def typewriter(t, cx, y, size):
    """Centred type-and-delete loop over PHRASES, in SMIL so it runs inside <img>."""
    cw = size * 0.6
    type_s, hold_s, del_s, gap_s = 0.07, 1.9, 0.03, 0.3
    events, spans, now = [], [], 0.0  # events: (time, chars shown, phrase index)
    for i, p in enumerate(PHRASES):
        start = now
        for k in range(len(p) + 1):
            events.append((now, k, i))
            now += type_s if k < len(p) else hold_s
        for k in range(len(p) - 1, -1, -1):
            events.append((now, k, i))
            now += del_s
        now += gap_s
        spans.append((start, now))
    total = now
    kt = ";".join(f"{e[0] / total:.5f}" for e in events) + ";1"

    # Each phrase is centred, so its left edge depends on its own length.
    def left(i):
        return cx - len(PHRASES[i]) * cw / 2

    clip_x = ";".join(f"{left(i):.1f}" for _, _, i in events) + f";{left(0):.1f}"
    clip_w = ";".join(f"{k * cw:.1f}" for _, k, _ in events) + ";0"
    cursor_x = ";".join(f"{left(i) + k * cw + 3:.1f}" for _, k, i in events) + f";{left(0) + 3:.1f}"
    anim = f'dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}"'

    out = [
        f'<clipPath id="type"><rect y="{y - size}" height="{size * 1.4}" x="{left(0):.1f}" width="0">'
        f'<animate attributeName="x" {anim} values="{clip_x}"/>'
        f'<animate attributeName="width" {anim} values="{clip_w}"/></rect></clipPath>',
        '<g clip-path="url(#type)">',
    ]
    for p, (start, end) in zip(PHRASES, spans):
        out.append(
            f'<text class="mono" x="{cx}" y="{y}" font-size="{size}" text-anchor="middle" fill="{t["primary"]}" '
            f'textLength="{len(p) * cw:.1f}" lengthAdjust="spacingAndGlyphs" opacity="0">{escape(p)}'
            f'<animate attributeName="opacity" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{start / total:.5f};{end / total:.5f};1" values="0;1;0;0"/></text>'
        )
    out.append("</g>")
    out.append(
        f'<rect class="cursor" y="{y - size * 0.82:.1f}" width="2.5" height="{size * 1.02:.1f}" rx="1" fill="{t["primary"]}">'
        f'<animate attributeName="x" {anim} values="{cursor_x}"/></rect>'
    )
    return "\n".join(out)


def banner(t):
    h, cx = 270, W / 2
    defs, back = backdrop(
        t, h, 22,
        [
            ("d1", 150, 40, 150, t["primary"], 0.4),
            ("d2", 860, 250, 160, "#60a5fa", 0.3),
            ("d1", 520, 290, 110, "#1d4ed8", 0.22),
        ],
    )
    css = ".cursor { animation: blink 1s step-end infinite; }"
    body = [
        back,
        f'<text class="mono rise" {delay(0)} x="{cx}" y="62" font-size="14" letter-spacing="3" text-anchor="middle" fill="{t["muted"]}">HELLO, WORLD — I\'M</text>',
        f'<text class="rise" {delay(1)} x="{cx}" y="134" font-size="72" font-weight="800" letter-spacing="-2" text-anchor="middle" fill="url(#shimmer)">Kalpit Jain</text>',
        f'<g class="rise" {delay(2)}>{typewriter(t, cx, 186, 21)}</g>',
        f'<g class="rise" {delay(3)} font-size="14.5" fill="{t["muted"]}">',
        icon("map-pin", cx - 66, 218, 16, t["muted"]),
        f'<text x="{cx - 44}" y="231">Bengaluru, India</text>',
        "</g>",
    ]
    return svg(t, W, h, "\n".join(body), css, defs)


# ── Link buttons ───────────────────────────────────────────────────────

BUTTONS = {
    "portfolio": ("icon", "globe", "kalpitjain.dev"),
    "linkedin": ("brand", "linkedin", "LinkedIn"),
    "leetcode": ("brand", "leetcode", "LeetCode"),
    "email": ("icon", "mail", "Email"),
}


def button(t, kind, glyph, text):
    h = 44
    w = round(52 + len(text) * 8.1 + 20)
    mark = icon(glyph, 18, 13, 18, t["primary"]) if kind == "icon" else brand(glyph, 19, 14, 16, t["primary"])
    body = (
        cell(0, 0, w, h, rx=h / 2, glow="tl")
        + mark
        + f'<text x="46" y="27.5" font-size="14.5" font-weight="600" fill="{t["fg"]}">{escape(text)}</text>'
    )
    return svg(t, w, h, body)


# ── Bento row 1: About + Now ───────────────────────────────────────────

ABOUT = [
    "Every system starts as a question. I find where work is still",
    "manual, form a hypothesis, and experiment with AI until the",
    "answer holds up in production.",
]
METHOD = ["observe", "question", "experiment", "refine"]
FOCUS = "agents that reason · automation · search that finds the answer"

PREVIOUSLY = [("Microsoft", "SWE Intern"), ("MyShubhLife", "Backend Intern")]


def text_w(text, size, weight=400):
    """Rough proportional-font width, good enough for laying out pills."""
    narrow = sum(text.count(c) for c in "iljtfrI.,·(/ ")
    wide = sum(text.count(c) for c in "MWmw")
    avg = 0.6 if weight >= 600 else 0.56
    return ((len(text) - narrow - wide) * avg + narrow * 0.3 + wide * 0.85) * size


def bento_about(t):
    h = 340
    aw = 604
    nx, nw = aw + GAP, W - aw - GAP
    body = [
        f'<g class="rise" {delay(0)}>',
        cell(0, 0, aw, h, glow="tl"),
        label(t, 32, 44, "ABOUT", "sparkles"),
        f'<text x="32" y="90" font-size="26" font-weight="800" letter-spacing="-.5" fill="{t["fg"]}">I approach software the way</text>',
        f'<text x="32" y="122" font-size="26" font-weight="800" letter-spacing="-.5" fill="url(#shimmer)">a scientist approaches the world.</text>',
    ]
    for i, line in enumerate(ABOUT):
        body.append(f'<text x="32" y="{164 + i * 23}" font-size="15" fill="{t["muted"]}">{escape(line)}</text>')

    # observe → question → experiment → refine
    x, y = 32, 236
    for i, step in enumerate(METHOD):
        w = text_w(step, 13, 600) + 28
        body += [
            f'<g class="rise" {delay(i, 0.12, 0.5)}>',
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="32" rx="16" fill="{t["primary_soft"]}" stroke="{t["primary"]}" stroke-opacity=".3"/>',
            f'<text class="mono" x="{x + w / 2:.1f}" y="{y + 20.5}" font-size="13" font-weight="600" text-anchor="middle" fill="{t["primary"]}">{step}</text>',
            "</g>",
        ]
        x += w
        if i < len(METHOD) - 1:
            body.append(icon("chevron-right", x + 5, y + 8, 16, t["faint"]))
            x += 26

    body += [
        f'<line x1="32" y1="290" x2="{aw - 32}" y2="290" stroke="{t["border"]}"/>',
        icon("zap", 32, 303, 15, t["primary"]),
        f'<text x="56" y="315" font-size="13" fill="{t["muted"]}"><tspan fill="{t["fg"]}" font-weight="600">Focus</tspan>  {escape(FOCUS)}</text>',
        "</g>",
    ]

    body += [
        f'<g class="rise" {delay(1)}>',
        cell(nx, 0, nw, h, glow="br"),
        label(t, nx + 30, 44, "NOW", "briefcase"),
        f'<circle class="pulse" cx="{nx + nw - 36}" cy="40" r="5" fill="{t["green"]}"/>',
        f'<circle cx="{nx + nw - 36}" cy="40" r="5" fill="{t["green"]}"/>',
        f'<text x="{nx + 30}" y="90" font-size="23" font-weight="800" letter-spacing="-.4" fill="{t["fg"]}">Software Engineer II</text>',
        f'<text x="{nx + 30}" y="116" font-size="16" font-weight="600" fill="{t["primary"]}">Bik.AI <tspan fill="{t["muted"]}" font-weight="400">· YC S20 · Bengaluru</tspan></text>',
        f'<line x1="{nx + 30}" y1="142" x2="{nx + nw - 30}" y2="142" stroke="{t["border"]}"/>',
        label(t, nx + 30, 172, "PREVIOUSLY"),
    ]
    for i, (org, role) in enumerate(PREVIOUSLY):
        y = 200 + i * 26
        body += [
            f'<text x="{nx + 30}" y="{y}" font-size="15.5" font-weight="600" fill="{t["fg"]}">{org}</text>',
            f'<text x="{nx + nw - 30}" y="{y}" font-size="13.5" text-anchor="end" fill="{t["muted"]}">{role}</text>',
        ]
    body += [
        f'<line x1="{nx + 30}" y1="252" x2="{nx + nw - 30}" y2="252" stroke="{t["border"]}"/>',
        label(t, nx + 30, 282, "EDUCATION"),
        f'<text x="{nx + 30}" y="310" font-size="15.5" font-weight="600" fill="{t["fg"]}">B.Tech, Computer Science</text>',
        f'<text x="{nx + nw - 30}" y="310" font-size="13.5" text-anchor="end" fill="{t["muted"]}">JECRC · 2024</text>',
        "</g>",
    ]
    return svg(t, W, h, "\n".join(body))


# ── Bento row 2: Highlights + Off-screen ───────────────────────────────

STATS = [("trophy", "7×", "Hackathon wins", "across AI and Web3"), ("code", "3+", "Years building", "AI into real products")]
OFFSCREEN = [
    ("book-open", "Reading", "finance, economics, politics & history"),
    ("plane", "Travel", "seeing how other places work"),
    ("camera", "Photography", "slowing down to notice the details"),
]


def bento_highlights(t):
    h = 214
    sw = 232
    body = []
    for i, (ic, big, text, sub) in enumerate(STATS):
        x = i * (sw + GAP)
        body += [
            f'<g class="rise" {delay(i)}>',
            cell(x, 0, sw, h, glow="tl" if i == 0 else None),
            f'<rect x="{x + sw - 58}" y="22" width="36" height="36" rx="10" fill="{t["primary_soft"]}"/>',
            icon(ic, x + sw - 49, 31, 18, t["primary"]),
            f'<text x="{x + 28}" y="126" font-size="64" font-weight="800" letter-spacing="-2" fill="url(#shimmer)">{big}</text>',
            f'<text x="{x + 30}" y="160" font-size="15.5" font-weight="700" fill="{t["fg"]}">{escape(text)}</text>',
            f'<text x="{x + 30}" y="182" font-size="13" fill="{t["muted"]}">{escape(sub)}</text>',
            "</g>",
        ]

    ox = 2 * (sw + GAP)
    ow = W - ox
    body += [
        f'<g class="rise" {delay(2)}>',
        cell(ox, 0, ow, h, glow="br"),
        label(t, ox + 30, 44, "OFF-SCREEN"),
        f'<text class="mono" x="{ox + ow - 30}" y="44" font-size="11.5" letter-spacing="1.8" text-anchor="end" fill="{t["faint"]}">WHAT KEEPS ME GROUNDED</text>',
    ]
    for i, (ic, title, sub) in enumerate(OFFSCREEN):
        y = 70 + i * 46
        body += [
            f'<rect x="{ox + 30}" y="{y}" width="36" height="36" rx="10" fill="{t["primary_soft"]}"/>',
            icon(ic, ox + 39, y + 9, 18, t["primary"]),
            f'<text x="{ox + 80}" y="{y + 16}" font-size="15" font-weight="700" fill="{t["fg"]}">{title}</text>',
            f'<text x="{ox + 80}" y="{y + 33}" font-size="13" fill="{t["muted"]}">{escape(sub)}</text>',
        ]
    body.append("</g>")
    return svg(t, W, h, "\n".join(body))


# ── Toolbox: every resume skill, grouped like the resume ───────────────

# (kind, glyph, name): kind is "brand" (Simple Icons) or "icon" (Lucide, for concepts).
TOOLS = [
    ("LANGUAGES", [
        ("brand", "typescript", "TypeScript"), ("brand", "javascript", "JavaScript"), ("brand", "openjdk", "Java"),
        ("brand", "python", "Python"), ("icon", "database", "SQL"), ("brand", "c", "C"),
    ]),
    ("FRONTEND", [
        ("brand", "react", "React"), ("brand", "nextdotjs", "Next.js"), ("brand", "redux", "Redux"),
        ("brand", "tailwindcss", "Tailwind CSS"), ("brand", "storybook", "Storybook"),
    ]),
    ("BACKEND", [
        ("brand", "nodedotjs", "Node.js"), ("brand", "express", "Express.js"), ("brand", "postgresql", "PostgreSQL"),
        ("brand", "redis", "Redis"), ("brand", "firebase", "Firestore"),
    ]),
    ("AI & SEARCH", [
        ("icon", "search", "RAG"), ("brand", "langchain", "LangChain"), ("icon", "brain", "Semantic Kernel"),
        ("brand", "elasticsearch", "Elasticsearch"), ("brand", "qdrant", "Qdrant"),
        ("icon", "message-square-text", "Prompt Engineering"), ("brand", "openai", "OpenAI"), ("brand", "googlegemini", "Gemini"),
    ]),
    ("INFRA & CLOUD", [
        ("brand", "docker", "Docker"), ("brand", "googlecloud", "GCP"), ("brand", "githubactions", "GitHub Actions"),
        ("brand", "vercel", "Vercel"), ("brand", "supabase", "Supabase"),
    ]),
]

PILL_H, PILL_GAP, PILL_FS = 38, 10, 13.5


def pill(t, x, y, kind, glyph, name):
    w = 44 + text_w(name, PILL_FS, 600) + 16
    mark = brand(glyph, x + 15, y + 11, 16, t["fg"], 0.92) if kind == "brand" else icon(glyph, x + 14, y + 10, 18, t["fg"])
    return w, (
        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{PILL_H}" rx="{PILL_H / 2}" fill="{t["primary_soft"]}" '
        f'fill-opacity=".65" stroke="{t["border"]}"/>' + mark +
        f'<text x="{x + 40:.1f}" y="{y + 24}" font-size="{PILL_FS}" font-weight="600" fill="{t["fg"]}">{escape(name)}</text>'
    )


def toolbox(t):
    pad, label_w = 32, 170
    left, right = pad + label_w, W - pad
    body, y, n = [], 84, 0
    for g, (group, items) in enumerate(TOOLS):
        if g:
            body.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{t["border"]}" stroke-opacity=".7"/>')
        body.append(label(t, pad, y + 24, group))
        x = left
        for kind, glyph, name in items:
            w = 44 + text_w(name, PILL_FS, 600) + 16
            if x + w > right:
                x, y = left, y + PILL_H + PILL_GAP
            _, markup = pill(t, x, y, kind, glyph, name)
            body.append(f'<g class="rise" {delay(n, 0.025, 0.2)}>{markup}</g>')
            x += w + PILL_GAP
            n += 1
        y += PILL_H + 28
    h = y - 4
    header = [
        cell(0, 0, W, h, glow="tl"),
        label(t, pad, 44, "TOOLBOX", "code"),
        f'<text class="mono" x="{W - pad}" y="44" font-size="11.5" letter-spacing="1.8" text-anchor="end" fill="{t["faint"]}">WHAT I BUILD WITH</text>',
    ]
    return svg(t, W, h, "\n".join(header + body))


# ── Sign-off ───────────────────────────────────────────────────────────


def signoff(t):
    h = 150
    body = [
        cell(0, 0, W, h, glow="tl"),
        f'<rect width="{W}" height="{h}" rx="20" fill="url(#glow-br)"/>',
        icon("quote", W / 2 - 14, 26, 28, t["primary"]),
        f'<text class="rise" {delay(0)} x="{W / 2}" y="92" font-size="21" font-style="italic" text-anchor="middle" fill="{t["fg"]}">'
        "The best solutions come from understanding the world beyond the screen.</text>",
        f'<text class="mono rise" {delay(1)} x="{W / 2}" y="124" font-size="12" letter-spacing="2" text-anchor="middle" fill="{t["muted"]}">— KALPIT JAIN</text>',
    ]
    return svg(t, W, h, "\n".join(body))


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    pages = {
        "banner": banner,
        "about": bento_about,
        "highlights": bento_highlights,
        "toolbox": toolbox,
        "signoff": signoff,
        **{f"btn-{k}": (lambda t, v=v: button(t, *v)) for k, v in BUTTONS.items()},
    }
    for name, render in pages.items():
        for theme, tokens in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(render(tokens))
    print(f"Wrote {len(pages) * len(THEMES)} files to {OUT}")


if __name__ == "__main__":
    main()

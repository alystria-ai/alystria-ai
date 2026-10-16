"""Generates the animated SVG artwork for the Alystria GitHub profile README.

    python tools/make_assets.py      (writes into ../assets)

Everything is plain SVG + SMIL so it animates inside GitHub's <img> sandbox:
no scripts, no external fonts. Randomness is seeded, so output is stable.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

CYAN, BLUE, VIOLET, PINK, PEACH = "#6fe7ff", "#6aa8ff", "#a77bff", "#ff7ad9", "#f3b9a6"
INK, MUTED = "#eef1ff", "#a7b2d9"
SERIF = "Georgia, 'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', serif"
SANS = "'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Consolas, 'SFMono-Regular', Menlo, monospace"


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def smooth_path(pts):
    """Catmull-Rom through pts, as cubic beziers (same command count for any pts of equal length)."""
    d = [f"M{f(pts[0][0])} {f(pts[0][1])}"]
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    return "".join(d)


def iris_gradient(gid, width, dur, direction=1):
    return (
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="{width}" y2="0" gradientUnits="userSpaceOnUse" spreadMethod="repeat">'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{direction * width} 0" dur="{dur}s" repeatCount="indefinite"/>'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".25" stop-color="{BLUE}"/>'
        f'<stop offset=".5" stop-color="{VIOLET}"/><stop offset=".75" stop-color="{PINK}"/>'
        f'<stop offset="1" stop-color="{CYAN}"/></linearGradient>'
    )


def stars(rng, n, w, h, max_y=None):
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, max_y or h)
        r = rng.choice([0.7, 0.9, 1.1, 1.4])
        dur = rng.uniform(2.5, 7)
        begin = rng.uniform(-7, 0)
        out.append(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="#fff">'
            f'<animate attributeName="opacity" values=".15;.9;.15" dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite"/></circle>'
        )
    return "".join(out)


def mane(rng, n, w, h, base, rise, spread, grad, mask=None, amp=(14, 40)):
    """Flowing strands that morph between two phases."""
    out = [f'<g fill="none" stroke="url(#{grad})" stroke-linecap="round"' + (f' mask="url(#{mask})"' if mask else "") + ">"]
    for i in range(n):
        t = i / (n - 1)
        a = rng.uniform(*amp)
        fr = rng.uniform(0.0035, 0.0065)
        ph = rng.uniform(0, math.tau)
        width = rng.uniform(0.7, 2.4)
        op = rng.uniform(0.25, 0.75)
        dur = rng.uniform(9, 16)

        def curve(shift):
            pts = []
            for x in range(-60, int(w) + 61, 70):
                nx = x / w
                y = h * (base - nx * rise) + (t - 0.5) * spread * (0.45 + nx * 0.9)
                y += math.sin(x * fr + ph + shift) * a + math.sin(x * fr * 2.2 - ph * 2 + shift * 1.6) * a * 0.3
                pts.append((x, y))
            return smooth_path(pts)

        d0, d1, d2 = curve(0), curve(math.pi * 0.66), curve(math.pi * 1.33)
        out.append(
            f'<path d="{d0}" stroke-width="{f(width)}" opacity="{op:.2f}">'
            f'<animate attributeName="d" values="{d0};{d1};{d2};{d0}" dur="{f(dur)}s" repeatCount="indefinite" '
            f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></path>'
        )
        if i % 3 == 0:  # soft glow under every third strand
            out.append(
                f'<path d="{d0}" stroke-width="{f(width * 9)}" opacity=".05">'
                f'<animate attributeName="d" values="{d0};{d1};{d2};{d0}" dur="{f(dur)}s" repeatCount="indefinite" '
                f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></path>'
            )
    out.append("</g>")
    return "".join(out)


def lys(uid, scale=1.0):
    """Lys, the Alystria mascot: blinks and bobs. Centred on (0,0)."""
    blink = 'values="5.4;5.4;.5;5.4;5.4" keyTimes="0;.9;.93;.96;1" dur="4.6s" repeatCount="indefinite"'
    glint = 'values="1;1;0;1;1" keyTimes="0;.9;.93;.96;1" dur="4.6s" repeatCount="indefinite"'
    return f"""<g transform="scale({scale})">
  <defs>
    <radialGradient id="{uid}b" cx=".4" cy=".34" r=".72" fx=".3" fy=".24">
      <stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="#d4f8ff"/><stop offset=".6" stop-color="#8ec5ff"/>
      <stop offset=".84" stop-color="#ad8cff"/><stop offset="1" stop-color="#ff8ad8"/>
    </radialGradient>
    <linearGradient id="{uid}h" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#f6f0ff"/><stop offset="1" stop-color="#9fe9ff"/></linearGradient>
    <linearGradient id="{uid}m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
    <filter id="{uid}g" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="9"/></filter>
  </defs>
  <animateTransform attributeName="transform" type="translate" additive="sum" values="0 0;0 -6;0 0" dur="3.6s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
  <circle r="30" fill="{CYAN}" opacity=".45" filter="url(#{uid}g)"/>
  <path d="M2 -24 L9 -46 L13 -22 Z" fill="url(#{uid}h)"/>
  <path d="M4.5 -32 l6 -1.5 M6 -38 l4.6 -1.2" stroke="#9fd7ff" stroke-width="1.2" stroke-linecap="round"/>
  <circle r="26" fill="url(#{uid}b)"/>
  <path d="M-14 -22 q8 -10 20 -4 q-10 -2 -14 6 q-2 -4 -6 -2z M-22 -12 q2 -12 14 -14 q-8 6 -8 14z" fill="url(#{uid}m)"/>
  <ellipse cx="-9" cy="2" rx="4.2" ry="5.4" fill="#1c1442"><animate attributeName="ry" {blink}/></ellipse>
  <ellipse cx="9" cy="2" rx="4.2" ry="5.4" fill="#1c1442"><animate attributeName="ry" {blink}/></ellipse>
  <circle cx="-7.4" cy="-.6" r="1.5" fill="#fff"><animate attributeName="opacity" {glint}/></circle>
  <circle cx="10.6" cy="-.6" r="1.5" fill="#fff"><animate attributeName="opacity" {glint}/></circle>
  <ellipse cx="-16" cy="11" rx="4" ry="2.2" fill="{PINK}" opacity=".45"/>
  <ellipse cx="16" cy="11" rx="4" ry="2.2" fill="{PINK}" opacity=".45"/>
  <path d="M-3 11 q3 3 6 0" stroke="#1c1442" stroke-width="1.6" fill="none" stroke-linecap="round"/>
</g>"""


def cycle_opacity(i, n, dur, fade=0.03):
    """Opacity animation that shows item i of n during its slot of a repeating cycle."""
    a, b = i / n, (i + 1) / n
    keys = sorted({0, max(a - 0.0001, 0), a, min(a + fade, b), max(b - fade, a), b, 1})
    vals = []
    for k in keys:
        vals.append("1" if (a + fade - 1e-9 <= k <= b - fade + 1e-9) else "0")
    return f'<animate attributeName="opacity" values="{";".join(vals)}" keyTimes="{";".join(f"{k:.4f}" for k in keys)}" dur="{dur}s" repeatCount="indefinite"/>'


def bubble(lines, x, y, dur, size=17, pad=16, tail_x=None, char_w=0.5):
    """A speech bubble that resizes around each line as the text cycles. (x, y) is its top-left at the widest line."""
    h = size + pad * 1.3
    widths = [len(s) * size * char_w + pad * 2 for s in lines]
    right = x + max(widths)  # bubbles grow leftwards from a fixed right edge
    tx = tail_x if tail_x is not None else right - 30
    n = len(lines)
    kt = ";".join(f"{i / n:.4f}" for i in range(n))
    xs = ";".join(f(right - w) for w in widths)
    ws = ";".join(f(w) for w in widths)
    mids = ";".join(f(right - w / 2) for w in widths)
    out = [
        f'<g font-family="{SANS}" font-size="{size}" font-weight="500" fill="#1c1442" text-anchor="middle">',
        f'<rect x="{f(right - widths[0])}" y="{f(y)}" width="{f(widths[0])}" height="{f(h)}" rx="{f(h / 2)}" fill="#fbf9ff">'
        f'<animate attributeName="x" values="{xs}" keyTimes="{kt}" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>'
        f'<animate attributeName="width" values="{ws}" keyTimes="{kt}" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/></rect>',
        f'<path d="M{f(tx - 7)} {f(y + h - 1)} l7 9 l7 -9z" fill="#fbf9ff"/>',
    ]
    for i, s in enumerate(lines):
        out.append(f'<text x="{f(right - widths[i] / 2)}" y="{f(y + h / 2 + size * 0.36)}" opacity="0">{s}{cycle_opacity(i, n, dur)}</text>')
    out.append("</g>")
    return "".join(out)


# ── banner ────────────────────────────────────────────────────────────────

def banner():
    rng = random.Random(7)
    W, H = 1280, 400
    clouds = []
    for cx, cy, rx, ry, dur, op in [(200, 90, 260, 60, 70, -0.4), (900, 260, 320, 70, 90, -0.6), (500, 360, 260, 50, 80, -0.2)]:
        clouds.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#cloud)" filter="url(#blur)">'
            f'<animateTransform attributeName="transform" type="translate" values="-160 0;160 0;-160 0" dur="{dur}s" begin="{op * dur}s" repeatCount="indefinite"/></ellipse>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Alystria: AI characters with presence">
<defs>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="26"/></clipPath>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1230"/><stop offset=".55" stop-color="#152150"/><stop offset="1" stop-color="#2b3a78"/></linearGradient>
  <radialGradient id="warm" cx=".78" cy="1.05" r=".7"><stop offset="0" stop-color="{PEACH}" stop-opacity=".35"/><stop offset="1" stop-color="{PEACH}" stop-opacity="0"/></radialGradient>
  <radialGradient id="cool" cx=".05" cy="1" r=".6"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".25"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <radialGradient id="cloud"><stop offset="0" stop-color="#8d9ad8" stop-opacity=".35"/><stop offset="1" stop-color="#8d9ad8" stop-opacity="0"/></radialGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
  {iris_gradient("mane", 1100, 18)}
  {iris_gradient("word", 760, 12, -1)}
  <linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".38" stop-color="#555"/><stop offset=".62" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>
  <mask id="maneMask"><rect width="{W}" height="{H}" fill="url(#fadeL)"/></mask>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  <rect width="{W}" height="{H}" fill="url(#warm)"/>
  <rect width="{W}" height="{H}" fill="url(#cool)"/>
  {stars(rng, 90, W, H, 330)}
  {"".join(clouds)}
  {mane(rng, 26, W, H, 0.86, 0.62, 150, "mane", "maneMask")}
  <text x="76" y="92" font-family="{MONO}" font-size="15" letter-spacing="3.5" fill="{MUTED}">AN INDEPENDENT STUDIO OF ONE</text>
  <text x="70" y="222" font-family="{SERIF}" font-size="132" letter-spacing="-3" fill="url(#word)">Alystria</text>
  <text x="76" y="282" font-family="{SERIF}" font-size="36" fill="{INK}">AI characters with <tspan font-style="italic" fill="{PEACH}">presence.</tspan></text>
  <text x="77" y="334" font-family="{MONO}" font-size="15" fill="{MUTED}">game companions <tspan fill="{VIOLET}">✦</tspan> chess coaches <tspan fill="{VIOLET}">✦</tspan> desktop pets <tspan fill="{VIOLET}">✦</tspan> free &amp; open</text>
  <g transform="translate(1110 236)">{lys("ly", 1.55)}</g>
  {bubble(["hi! I'm Lys.", "I live here.", "everything here is free.", "the code is open, too.", "throw me on the website!"], 930, 104, 15, size=19, tail_x=1112)}
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="25.5" fill="none" stroke="#bccdff" stroke-opacity=".16" stroke-width="1.5"/>
</svg>"""
    (OUT / "banner.svg").write_text(svg, encoding="utf-8")


# ── divider ───────────────────────────────────────────────────────────────

def divider():
    rng = random.Random(21)
    W, H = 1280, 90
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="flowing iridescent divider">
<defs>
  {iris_gradient("dv", 900, 14)}
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
  <mask id="dm"><rect width="{W}" height="{H}" fill="url(#edge)"/></mask>
</defs>
{mane(rng, 12, W, H, 0.5, 0, 34, "dv", "dm", amp=(6, 16))}
</svg>"""
    (OUT / "divider.svg").write_text(svg, encoding="utf-8")


# ── scene cards ───────────────────────────────────────────────────────────

CW, CH = 480, 300


def card(name, label, body, defs=""):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CW} {CH}" width="{CW}" height="{CH}" role="img" aria-label="{label}">
<defs><clipPath id="c"><rect width="{CW}" height="{CH}" rx="22"/></clipPath>{defs}</defs>
<g clip-path="url(#c)">{body}</g>
<rect x=".75" y=".75" width="{CW - 1.5}" height="{CH - 1.5}" rx="21.5" fill="none" stroke="#bccdff" stroke-opacity=".18" stroke-width="1.5"/>
</svg>"""
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def card_games():
    lines = [
        ("YOU", "Think they'll follow us?"),
        ("MIRA", "Let them. I want a rematch."),
        ("MIRA", "You went left. I said right."),
        ("YOU", "…I was flanking."),
        ("MIRA", "Sure you were."),
    ]
    dur = 15
    subs = []
    for i, (who, text) in enumerate(lines):
        subs.append(
            f'<text x="240" y="275" text-anchor="middle" opacity="0"><tspan fill="{PEACH}" font-weight="700">{who}</tspan> {text}{cycle_opacity(i, len(lines), dur)}</text>'
        )
    defs = f"""<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c2b5c"/><stop offset=".6" stop-color="#6a4f8f"/><stop offset="1" stop-color="#e3a08f"/></linearGradient>
<radialGradient id="fire"><stop offset="0" stop-color="#ffd59a" stop-opacity=".9"/><stop offset="1" stop-color="#ff7a59" stop-opacity="0"/></radialGradient>"""
    rng = random.Random(3)
    body = f"""<rect width="{CW}" height="{CH}" fill="url(#dusk)"/>
{stars(rng, 26, CW, 120)}
<circle cx="360" cy="128" r="24" fill="#ffe2c4" opacity=".55"/>
<path d="M0 170 L60 128 L110 156 L180 104 L246 158 L314 118 L384 158 L446 124 L480 144 V300 H0Z" fill="#33295a"/>
<path d="M0 200 L84 166 L156 192 L228 160 L300 194 L384 170 L480 196 V300 H0Z" fill="#1d1a3f"/>
<path d="M0 228 Q120 212 240 224 T480 218 V300 H0Z" fill="#0f1029"/>
<path d="M48 228 l12 -40 l12 40z M70 230 l9 -30 l9 30z M396 224 l13 -44 l13 44z M420 226 l9 -31 l9 31z" fill="#0f1029"/>
<circle cx="240" cy="226" r="56" fill="url(#fire)"><animate attributeName="r" values="56;48;58;52;56" dur="1.9s" repeatCount="indefinite"/></circle>
<path d="M240 234 q-11 -12 0 -29 q11 17 0 29z" fill="#ffc46b"><animate attributeName="d" values="M240 234 q-11 -12 0 -29 q11 17 0 29z;M240 234 q-12 -15 1 -34 q10 20 -1 34z;M240 234 q-11 -12 0 -29 q11 17 0 29z" dur=".9s" repeatCount="indefinite"/></path>
<g fill="#0b0b20"><path d="M192 234 q0 -28 11 -33 a8 8 0 1 1 7 0 q11 5 11 33z"/><path d="M266 234 q0 -26 10 -31 a8 8 0 1 1 7 0 q10 5 10 31z"/></g>
<path d="M293 207 l12 -20" stroke="#0b0b20" stroke-width="3"/>
<rect x="12" y="248" width="456" height="40" rx="10" fill="#050616" opacity=".66"/>
<g font-family="{SANS}" font-size="19" fill="{INK}">{"".join(subs)}</g>"""
    card("scene-games", "A game companion talking by the campfire", body, defs)


def card_chess():
    # board 8x8 at (24,30), 240px; knight hops g1 → f3 → g5 → f7 while the coach comments
    s, bx, by = 30, 24, 30
    sq = []
    for r in range(8):
        for c in range(8):
            fill = "#5463ab" if (r + c) % 2 else "#aeb8e8"
            sq.append(f'<rect x="{bx + c * s}" y="{by + r * s}" width="{s}" height="{s}" fill="{fill}"/>')
    glyph = {"k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"}
    rows = ["r.bqkb.r", "pppp.ppp", "..n..n..", "....p...", "..B.P...", "........", "PPPP.PPP", "RNBQK..R"]
    pieces = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            white = ch.isupper()
            fill = "#fff" if white else "#1c1442"
            stroke = ' stroke="#1c1442" stroke-width="1.1" paint-order="stroke"' if white else ""
            pieces.append(
                f'<text x="{bx + c * s + s / 2}" y="{by + r * s + s * 0.78}" text-anchor="middle" fill="{fill}"{stroke}>{glyph[ch.lower()]}︎</text>'
            )
    # the moving knight: squares as (col,row) from white's view
    path = [(6, 7), (5, 5), (6, 3), (5, 1)]
    pts = [(bx + c * s, by + r * s) for c, r in path]
    dur = 12
    # hold, hop, hold... keyTimes for 4 positions over the cycle, then snap back
    kt = "0;.2;.25;.45;.5;.7;.75;.97;1"
    vals = f"{pts[0][0]} {pts[0][1]};{pts[0][0]} {pts[0][1]};{pts[1][0]} {pts[1][1]};{pts[1][0]} {pts[1][1]};{pts[2][0]} {pts[2][1]};{pts[2][0]} {pts[2][1]};{pts[3][0]} {pts[3][1]};{pts[3][0]} {pts[3][1]};{pts[0][0]} {pts[0][1]}"
    knight = (
        f'<g><animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/>'
        f'<rect width="{s}" height="{s}" fill="{PINK}" opacity=".35"/>'
        f'<text x="{s / 2}" y="{s * 0.78}" text-anchor="middle" fill="#fff" stroke="#1c1442" stroke-width="1.1" paint-order="stroke">♞︎</text></g>'
    )
    comments = [
        ["Knight out.", "Eyeing e5."],
        ["Ooh. Going", "after f7?"],
        ["Brave.", "Slightly reckless."],
        ["Fried Liver!", "I'm so proud."],
    ]
    says = []
    for i, (a, b) in enumerate(comments):
        says.append(
            f'<g opacity="0">{cycle_opacity(i, 4, dur)}<text x="306" y="170">{a}</text><text x="306" y="196">{b}</text></g>'
        )
    body = f"""<rect width="{CW}" height="{CH}" fill="#0f1840"/>
<rect width="{CW}" height="{CH}" fill="url(#glowC)"/>
<rect x="{bx - 4}" y="{by - 4}" width="{s * 8 + 8}" height="{s * 8 + 8}" rx="8" fill="#0a0f2c"/>
{"".join(sq)}
<g font-family="'Segoe UI Symbol', 'DejaVu Sans', 'Noto Sans Symbols 2', serif" font-size="24">{"".join(pieces)}{knight}</g>
<g transform="translate(330 104)"><circle r="22" fill="url(#face)"/>
<rect x="-9" y="-5" width="4.5" height="7" rx="2" fill="#2a1838"><animate attributeName="height" values="7;7;1;7" keyTimes="0;.94;.97;1" dur="4.6s" repeatCount="indefinite"/></rect>
<rect x="4.5" y="-5" width="4.5" height="7" rx="2" fill="#2a1838"><animate attributeName="height" values="7;7;1;7" keyTimes="0;.94;.97;1" dur="4.6s" repeatCount="indefinite"/></rect></g>
<rect x="290" y="140" width="176" height="74" rx="12" fill="#fff" fill-opacity=".08" stroke="#bccdff" stroke-opacity=".2"/>
<g font-family="{SANS}" font-size="17" fill="{INK}">{"".join(says)}</g>"""
    defs = f"""<radialGradient id="glowC" cx=".3" cy=".5" r=".7"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".22"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<radialGradient id="face" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff"/><stop offset=".45" stop-color="#ffd2a8"/><stop offset="1" stop-color="#f39a7a"/></radialGradient>"""
    card("scene-chess", "A chess coach commenting on a knight's moves", body, defs)


def card_pets():
    # walk: taskbar → up the right edge of a window → across its top → sit → hop down → back
    route = "M40 262 L392 262 L392 112 L262 112 L262 112 L230 262 L40 262"
    dur = 14
    critter = f"""<g>
<animateMotion dur="{dur}s" repeatCount="indefinite" path="{route}" keyPoints="0;.361;.515;.648;.648;.805;1" keyTimes="0;.28;.4;.52;.74;.82;1" calcMode="linear"/>
<g transform="translate(-17 -30)"><g><animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur=".45s" repeatCount="indefinite"/>
<path d="M8 10 L11 1 L16 8 M24 8 L29 1 L32 10" fill="#ffb3e6" stroke="#ffb3e6" stroke-linejoin="round" stroke-width="2"/>
<ellipse cx="20" cy="21" rx="15" ry="12.5" fill="#ffd6f2"/>
<circle cx="15" cy="20" r="2.2" fill="#24163f"/><circle cx="25" cy="20" r="2.2" fill="#24163f"/>
<ellipse cx="11" cy="25" rx="2.6" ry="1.5" fill="#ff8fcf" opacity=".7"/><ellipse cx="29" cy="25" rx="2.6" ry="1.5" fill="#ff8fcf" opacity=".7"/>
<path d="M18 25 q2 2 4 0" stroke="#24163f" stroke-width="1.4" fill="none" stroke-linecap="round"/></g></g>
<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.53;.56;.72;.75;1" dur="{dur}s" repeatCount="indefinite"/>
<rect x="-58" y="-66" width="116" height="28" rx="11" fill="#fff"/><path d="M-6 -39 l6 7 l6 -7z" fill="#fff"/>
<text x="0" y="-46" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="700" fill="#24163f">water break?</text></g>
</g>"""
    def win(x, y, w, h):
        return (
            f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#f0f2ff" fill-opacity=".93"/>'
            f'<path d="M{x} {y + 7} a7 7 0 0 1 7 -7 h{w - 14} a7 7 0 0 1 7 7 v9 h-{w}z" fill="#d6dbf5"/>'
            f'<rect x="{x + 12}" y="{y + 28}" width="{w * 0.7}" height="7" rx="3.5" fill="#c7cdea"/>'
            f'<rect x="{x + 12}" y="{y + 44}" width="{w * 0.5}" height="7" rx="3.5" fill="#c7cdea"/>'
            f'<rect x="{x + 12}" y="{y + 60}" width="{w * 0.6}" height="7" rx="3.5" fill="#c7cdea"/></g>'
        )
    body = f"""<rect width="{CW}" height="{CH}" fill="url(#wall)"/>
<rect width="{CW}" height="{CH}" fill="url(#wallP)"/>
<rect width="{CW}" height="{CH}" fill="url(#wallC)"/>
{win(40, 40, 220, 150)}
{win(250, 112, 142, 110)}
<rect y="262" width="{CW}" height="38" fill="#0a0e28" fill-opacity=".78"/>
<rect x="16" y="273" width="16" height="16" rx="4" fill="url(#irisP)"/>
<rect x="40" y="273" width="16" height="16" rx="4" fill="#fff" fill-opacity=".35"/>
<rect x="64" y="273" width="16" height="16" rx="4" fill="#fff" fill-opacity=".35"/>
<text x="458" y="286" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">16:00</text>
{critter}"""
    defs = f"""<linearGradient id="wall" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a3a86"/><stop offset="1" stop-color="#563c8c"/></linearGradient>
<radialGradient id="wallP" cx=".85" cy=".15" r=".7"><stop offset="0" stop-color="{PINK}" stop-opacity=".4"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
<radialGradient id="wallC" cx=".1" cy=".95" r=".7"><stop offset="0" stop-color="{CYAN}" stop-opacity=".3"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="irisP"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>"""
    card("scene-pets", "A desktop pet climbing a window and asking about a water break", body, defs)


# ── badges ────────────────────────────────────────────────────────────────

ICONS = {
    # simple glyphs drawn in a 24x24 box
    "website": '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18" fill="none" stroke="currentColor" stroke-width="1.6"/>',
    "youtube": '<rect x="2" y="5" width="20" height="14" rx="4.5" fill="currentColor"/><path d="M10 9l5 3-5 3z" fill="#141c48"/>',
    "patreon": '<circle cx="14.5" cy="9.5" r="6.5" fill="currentColor"/><rect x="3" y="3" width="3.6" height="18" rx="1" fill="currentColor"/>',
    "linkedin": '<rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="currentColor"/><path d="M7 10v7M7 7v.01M11 17v-7m0 3.2c0-2 1.3-3.2 2.9-3.2 1.6 0 2.6 1 2.6 3.2V17" stroke="#141c48" stroke-width="2.2" stroke-linecap="round" fill="none"/>',
}


def badge(name, label, color, width):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 56" width="{width}" height="56" role="img" aria-label="{label}">
<defs>{iris_gradient("bd", width * 2, 8)}</defs>
<rect x="1.5" y="1.5" width="{width - 3}" height="53" rx="26.5" fill="#141c48"/>
<rect x="1.5" y="1.5" width="{width - 3}" height="53" rx="26.5" fill="none" stroke="url(#bd)" stroke-width="2" stroke-opacity=".85"/>
<g transform="translate(20 16)" color="{color}" style="color:{color}">{ICONS[name]}</g>
<text x="54" y="35.5" font-family="{SANS}" font-size="20" font-weight="600" fill="{INK}">{label}</text>
</svg>"""
    (OUT / f"badge-{name}.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    banner()
    divider()
    card_games()
    card_chess()
    card_pets()
    badge("website", "Website", CYAN, 150)
    badge("youtube", "YouTube", "#ff6b8b", 150)
    badge("patreon", "Patreon", PEACH, 146)
    badge("linkedin", "LinkedIn", BLUE, 150)
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.name:24} {p.stat().st_size:>7,} bytes")

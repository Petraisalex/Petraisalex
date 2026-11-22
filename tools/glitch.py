#!/usr/bin/env python3
"""
glitch.py: wrap portrait.svg in a subtle, intermittent terminal-glitch animation.

    python3 tools/glitch.py                  # writes art/portrait-glitch.svg
    python3 tools/glitch.py --peak out.svg   # frozen at peak glitch (for checking)

portrait.svg stays the source of truth and is embedded once. Effects (pure CSS
@keyframes, so they run inside a GitHub <img>):

  slices   a few thin bands of rows jump sideways for a fraction of a second
  echo     cyan + pale-pink offset copies (<use>, no duplication) flash with the slices
  tears    ▓▒░ fragments appear at the ends of the displaced bands during a burst
  noise    sparse ASCII glyphs blink just outside the silhouette (never near the face)
  rain     three thin columns of falling characters in the empty margins
  scan     a faint scanline bar sweeps top to bottom, plus a rare whole-image flicker

Every animation is at rest at t=0 and for most of each cycle; periods are
prime-ish so the combined pattern does not visibly repeat. Randomness is seeded.
"""
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "portrait.svg"
DST = ROOT / "art" / "portrait-glitch.svg"

CW, RH = 3.02, 5.9          # grid: column width, row height (viewBox units)
SEED = 1337

# Slice sets: (period s, burst start %, [(first row, n rows, offsets...)]).
# Offsets are viewBox units (the README shows the art at ~0.54x).
SLICE_SETS = [
    ("a", 13.1, 37.0, [(36, 3, 9, -5), (52, 2, -7, 4), (74, 4, 6, -10), (118, 3, -11, 6)]),
    ("b", 19.7, 71.0, [(44, 4, -6, 8), (97, 2, 10, -4), (133, 3, -8, 5)]),
]
FACE_ROWS = 31               # rows above this (head and neck) get no noise
NOISE_GLYPHS = "01░▒▓/\\|:;+*<>_-"
NOISE_COLORS = ["#e04060", "#d13d5c", "#f08aa0", "#b33853", "#5fd4dc"]
RAIN_GLYPHS = "01:.|/\\░"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse(svg):
    m = re.search(r"<style>(.*?)</style>", svg, re.S)
    base_css = m.group(1)
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
    rows = re.findall(r'<text y="([\d.]+)">(.*?)</text>', svg, re.S)
    return base_css, vb, [(float(y), body) for y, body in rows]


def occupancy(rows):
    xs = [float(v) for _, b in rows for xx in re.findall(r'x="([^"]+)"', b) for v in xx.split()]
    x0 = min(xs)
    occ = set()
    for r, (_, b) in enumerate(rows):
        for xx in re.findall(r'x="([^"]+)"', b):
            for v in xx.split():
                occ.add((r, round((float(v) - x0) / CW)))
    return x0, occ


def slice_keyframes(name, start, offsets):
    """Calm, then a short stutter between the given offsets, then calm again."""
    a, b = offsets
    p = start
    steps = [(0, 0), (p, a), (p + 0.7, b), (p + 1.3, 0), (p + 2.0, round(a / 2)), (p + 2.4, 0), (100, 0)]
    frames = " ".join(f"{t:.2f}%{{transform:translateX({x}px)}}" for t, x in steps)
    return f"@keyframes {name}{{{frames}}}"


def build(peak=False):
    rnd = random.Random(SEED)
    base_css, vb, rows = parse(SRC.read_text(encoding="utf-8"))
    W, H = (float(v) for v in vb.split()[2:])
    x0, occ = occupancy(rows)
    y0 = rows[0][0]
    cx = lambda c: f"{x0 + c * CW:.2f}"
    ry = lambda r: f"{y0 + r * RH:.2f}"

    css = [base_css, "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace}"]
    peak_css = []

    # ---- slices: wrap their rows in animated groups --------------------------
    row_group, starts = {}, {}
    tears = []
    for set_name, period, start, bands in SLICE_SETS:
        for i, (r0, n, a, b) in enumerate(bands):
            cls = f"s{set_name}{i}"
            for r in range(r0, r0 + n):
                row_group[r] = cls
            st = start + rnd.uniform(-0.3, 0.3)
            starts[cls] = st
            css.append(slice_keyframes(cls, st, (a, b)))
            css.append(f".{cls}{{animation:{cls} {period}s steps(1,end) infinite}}")
            peak_css.append(f".{cls}{{transform:translateX({a}px)}}")
            # tear fragments at both row ends, shown only during this burst
            for r in range(r0, r0 + n):
                cols = [c for (rr, c) in occ if rr == r]
                if not cols:
                    continue
                for end, d in ((min(cols), -1), (max(cols), 1)):
                    k = rnd.randint(1, 3)
                    for j in range(k):
                        tears.append((cls, period, st, r, end + d * (j + 1) + (a // 3 if d > 0 else 0),
                                      "▓▒░"[min(j, 2)]))
    body, open_cls = [], None
    for r, (y, inner) in enumerate(rows):
        cls = row_group.get(r)
        if cls != open_cls:
            if open_cls:
                body.append("</g>")
            if cls:
                body.append(f'<g class="{cls}">')
            open_cls = cls
        body.append(f'<text y="{y}">{inner}</text>')
    if open_cls:
        body.append("</g>")

    # ---- echo: two tinted offset copies that flash with slice set "a" --------
    pa, sa = SLICE_SETS[0][1], SLICE_SETS[0][2]
    pb, sb = SLICE_SETS[1][1], SLICE_SETS[1][2]
    css.append(
        "@keyframes echoA{0%{visibility:hidden;transform:translate(0,0)}"
        f"{sa:.2f}%{{visibility:visible;transform:translate(3px,0)}}"
        f"{sa+0.9:.2f}%{{visibility:visible;transform:translate(-2px,1px)}}"
        f"{sa+1.6:.2f}%{{visibility:hidden}}"
        f"{sa+2.0:.2f}%{{visibility:visible;transform:translate(2px,0)}}"
        f"{sa+2.4:.2f}%{{visibility:hidden}}100%{{visibility:hidden}}}}")
    css.append(
        "@keyframes echoB{0%{visibility:hidden;transform:translate(0,0)}"
        f"{sb:.2f}%{{visibility:visible;transform:translate(-3px,0)}}"
        f"{sb+1.1:.2f}%{{visibility:visible;transform:translate(2px,0)}}"
        f"{sb+1.8:.2f}%{{visibility:hidden}}100%{{visibility:hidden}}}}")
    css.append(f".echo{{visibility:hidden;opacity:.4}}"
               f".e1{{animation:echoA {pa}s steps(1,end) infinite}}"
               f".e2{{animation:echoB {pb}s steps(1,end) infinite;opacity:.35}}")
    peak_css.append(".e1{visibility:visible;transform:translate(3px,0)}"
                    ".e2{visibility:visible;transform:translate(-3px,0)}")

    # ---- tears --------------------------------------------------------------
    tear_svg = []
    for cls, period, st, r, c, g in tears:
        tear_svg.append(f'<text class="t{cls}" x="{cx(c)}" y="{ry(r)}">{g}</text>')
    for set_name, period, start, bands in SLICE_SETS:
        for i in range(len(bands)):
            cls = f"s{set_name}{i}"
            st = starts[cls]
            css.append(f".t{cls}{{fill:#f08aa0;opacity:0;animation:{cls} {period}s steps(1,end) infinite,"
                       f"tv{cls} {period}s steps(1,end) infinite}}")
            css.append(f"@keyframes tv{cls}{{0%{{opacity:0}}{st:.2f}%{{opacity:.9}}"
                       f"{st+1.3:.2f}%{{opacity:0}}{st+2.0:.2f}%{{opacity:.6}}{st+2.4:.2f}%{{opacity:0}}100%{{opacity:0}}}}")
            peak_css.append(f".t{cls}{{opacity:.9;transform:translateX({bands[i][2]}px)}}")

    # ---- noise: sparse blinking glyphs near the silhouette edge -------------
    cand = []
    for r in range(FACE_ROWS, len(rows)):
        for c in range(-8, 170):
            if (r, c) in occ:
                continue
            near = any((r + dr, c + dc) in occ for dr in (-1, 0, 1) for dc in range(-3, 4))
            if near and x0 + c * CW > 4 and x0 + c * CW < W - 4:
                cand.append((r, c))
    picks = rnd.sample(cand, 54)
    periods = [5.3, 6.7, 8.9, 10.3, 12.7, 15.1]
    for k, p in enumerate(periods):
        css.append(f"@keyframes nz{k}{{0%{{opacity:0}}{88 - k:.0f}%{{opacity:0}}{88.5 - k:.1f}%{{opacity:.85}}"
                   f"{89.5 - k:.1f}%{{opacity:0}}{90.5 - k:.1f}%{{opacity:.6}}{92 - k:.0f}%{{opacity:0}}100%{{opacity:0}}}}")
    noise_svg = []
    for i, (r, c) in enumerate(picks):
        k = i % len(periods)
        delay = -round(rnd.uniform(0, periods[k]), 2)
        col = rnd.choice(NOISE_COLORS)
        g = esc(rnd.choice(NOISE_GLYPHS))
        noise_svg.append(f'<text x="{cx(c)}" y="{ry(r)}" fill="{col}" '
                         f'style="animation:nz{k} {periods[k]}s steps(1,end) {delay}s infinite">{g}</text>')
    css.append(".nz text{opacity:0}")
    peak_css.append(".nz text{opacity:.85!important}")

    # ---- rain: three thin columns in the empty margins ----------------------
    def free_span(c, r_lo, r_hi):
        return all((r, cc) not in occ for r in range(r_lo, r_hi) for cc in (c - 2, c - 1, c, c + 1, c + 2))
    rain_cols = [(146, 0, len(rows), 11.3), (157, 0, len(rows), 16.9), (6, 62, len(rows), 13.7)]
    rain_svg, defs_clip = [], []
    for i, (c, r_lo, r_hi, dur) in enumerate(rain_cols):
        assert free_span(c, r_lo, r_hi), f"rain column {c} overlaps the art"
        x = x0 + c * CW
        top, bot = y0 + (r_lo - 1) * RH, y0 + r_hi * RH
        n = 24
        glyphs = []
        for j in range(n):
            if j < n - 1 and rnd.random() < 0.3:
                continue  # gaps make it read as data, not a bar
            t = j / (n - 1)
            fill = "#f6c6cf" if j == n - 1 else ("#f08aa0" if t > 0.7 else "#d13d5c")
            op = 1.0 if j == n - 1 else round(0.15 + 0.7 * t, 2)
            glyphs.append(f'<text x="{x:.2f}" y="{j * RH:.2f}" fill="{fill}" opacity="{op}">'
                          f'{esc(rnd.choice(RAIN_GLYPHS))}</text>')
        strip_h = n * RH
        defs_clip.append(f'<clipPath id="rc{i}"><rect x="{x - 4:.2f}" y="{top:.2f}" width="8" '
                         f'height="{bot - top:.2f}"/></clipPath>')
        css.append(f"@keyframes rn{i}{{0%{{transform:translateY({top - strip_h:.1f}px)}}"
                   f"100%{{transform:translateY({bot + RH:.1f}px)}}}}")
        delay = -round(rnd.uniform(0, dur), 2)
        css.append(f".rn{i}{{transform:translateY({top - strip_h:.1f}px);"
                   f"animation:rn{i} {dur}s linear {delay}s infinite}}")
        peak_css.append(f".rn{i}{{transform:translateY({(top + bot) / 2 - strip_h / 2:.1f}px)}}")
        rain_svg.append(f'<g clip-path="url(#rc{i})" opacity=".55"><g class="rn{i}">{"".join(glyphs)}</g></g>')

    # ---- scanline + flicker -------------------------------------------------
    css.append(f"@keyframes scan{{0%{{transform:translateY(-30px)}}100%{{transform:translateY({H + 10:.0f}px)}}}}"
               ".scan{animation:scan 9.7s linear infinite;transform:translateY(-30px)}")
    peak_css.append(f".scan{{transform:translateY({H * 0.42:.0f}px)}}")
    css.append("@keyframes flk{0%{opacity:1}61%{opacity:1}61.4%{opacity:.78}61.9%{opacity:1}"
               "62.5%{opacity:.88}63%{opacity:1}100%{opacity:1}}"
               ".flk{animation:flk 7.3s steps(1,end) infinite}")
    css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    if peak:
        css.append("*{animation:none!important}")
        css += peak_css

    defs = (
        "<defs>"
        '<filter id="fcy" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">'
        '<feFlood flood-color="#5fd4dc"/><feComposite in2="SourceAlpha" operator="in"/></filter>'
        '<filter id="fpk" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">'
        '<feFlood flood-color="#f6c6cf"/><feComposite in2="SourceAlpha" operator="in"/></filter>'
        '<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#f6c6cf" stop-opacity="0"/>'
        '<stop offset=".8" stop-color="#f6c6cf" stop-opacity=".025"/>'
        '<stop offset=".93" stop-color="#f6c6cf" stop-opacity=".07"/>'
        '<stop offset="1" stop-color="#f6c6cf" stop-opacity="0"/></linearGradient>'
        + "".join(defs_clip) + "</defs>"
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="{vb}" width="{W}" height="{H}" role="img" '
        f'aria-label="Character-art portrait with a subtle terminal-glitch animation">'
        f"<style>{''.join(css)}</style>{defs}"
        f'<g class="rain">{"".join(rain_svg)}</g>'
        f'<g class="flk">'
        f'<use class="echo e1" href="#art" xlink:href="#art" filter="url(#fcy)"/>'
        f'<use class="echo e2" href="#art" xlink:href="#art" filter="url(#fpk)"/>'
        f'<g id="art">{"".join(body)}</g>'
        f'<g class="tears">{"".join(tear_svg)}</g>'
        f"</g>"
        f'<g class="nz">{"".join(noise_svg)}</g>'
        f'<rect class="scan" x="0" y="0" width="{W}" height="16" fill="url(#sg)"/>'
        f"</svg>"
    )
    return svg


if __name__ == "__main__":
    peak = "--peak" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--peak"]
    out = Path(args[0]) if args else DST
    out.parent.mkdir(parents=True, exist_ok=True)
    data = build(peak)
    out.write_text(data, encoding="utf-8")
    print(f"wrote {out}: {len(data.encode()) / 1024:.0f} KB")

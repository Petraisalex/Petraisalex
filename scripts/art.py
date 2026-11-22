#!/usr/bin/env python3
"""
art.py — draw the profile's static graphics in the banner's navy & pink.

Outputs (all in art/):
    whoami.svg, profile.svg About Me as box-drawn 'files' (work, and person)
    typing.svg              rotating "typed" tagline under the banner
    stack-mastered.svg      tech-stack tiles: mastered
    learn-<group>.svg       "learning now" headings (data, web)
    learn-<lang>.svg        clickable language card (README <summary>)
    learn-<lang>-libs.svg   what I'm learning in that language (README <details> body)
    connect-<name>.svg      link buttons
    wave.svg                footer wave

Brand marks in art/icons/ are from Simple Icons (CC0). Power BI and Excel are
drawn here as simple geometric marks. No API calls; edit the constants below
and re-run to change anything.
"""
import re
from pathlib import Path

ART = Path(__file__).resolve().parent.parent / "art"

SANS = "Montserrat, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# light first, dark under the media query (the README sanitiser keeps <style> inside SVGs)
STYLE = """<style>
.fg{fill:#1f2328}.mu{fill:#59636e}.ac{fill:#dd2d51}.acs{stroke:#dd2d51}
.cd{fill:#f6f8fa;stroke:#d1d9e0}.bgs{stroke:#f6f8fa}
@media(prefers-color-scheme:dark){
.fg{fill:#f0f6fc}.mu{fill:#9198a1}.ac{fill:#e04060}.acs{stroke:#e04060}
.cd{fill:#151b23;stroke:#30363d}.bgs{stroke:#151b23}}
</style>"""

TAGLINES = [
    "Professional Hobby-collector",
    "Finance × AI",
    "Dashboards that get read",
    "Hyrox, boxing & live-coded music",
]

MASTERED = ["python", "n8n", "powerbi", "excel", "r", "git"]
# Learning now, grouped by language. Each entry:
#   (slug, language label, card icons, [what I'm learning in it], noun, caption)
# The README shows one clickable <details> per language; the panel lists its items.
LEARNING_GROUPS = {
    "data": ("LEARNING NOW · DATA & ML", [
        ("python", "Python", ["python"],
         ["catboost", "shap", "fastapi", "mlflow", "umap", "bertopic"],
         "libraries", "modelling · explainability · serving · tracking · topics"),
        ("sql", "SQL", ["sql"], ["googlebigquery", "looker"],
         "tools", "warehouse queries and BI modelling"),
        ("docker", "Docker", ["docker"], ["dockerfile"],
         "tool", "containers for serving models"),
    ]),
    "web": ("LEARNING NOW · WEB", [
        ("javascript", "JavaScript", ["javascript"], ["react"], "library", "UI components"),
        ("typescript", "TypeScript", ["typescript"], ["nextdotjs"], "framework",
         "full-stack React framework"),
        ("htmlcss", "HTML & CSS", ["html5", "css3"], ["html5", "css3"], "standards",
         "layout and semantics, no extra libraries"),
    ]),
}
LABELS = {"python": "Python", "n8n": "n8n", "powerbi": "Power BI", "excel": "Excel", "r": "R",
          "git": "Git", "catboost": "CatBoost", "shap": "SHAP", "fastapi": "FastAPI",
          "docker": "Docker", "dockerfile": "Dockerfile", "mlflow": "MLflow",
          "googlebigquery": "BigQuery", "looker": "Looker", "umap": "UMAP", "bertopic": "BERTopic",
          "html5": "HTML5", "css3": "CSS3", "javascript": "JavaScript", "sql": "SQL",
          "typescript": "TypeScript", "react": "React", "nextdotjs": "Next.js"}
ICON_ALIAS = {"dockerfile": "docker"}

CONNECT = [("linkedin", "LinkedIn"), ("instagram", "Instagram"), ("email", "Email")]


def xesc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def svg(w, h, inner, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{xesc(label)}">{STYLE}{inner}</svg>')


def icon_path(name):
    """24×24 path data for a mark."""
    f = ART / "icons" / f"{name}.svg"
    if f.exists():
        return re.search(r' d="([^"]+)"', f.read_text()).group(1)
    return None


def mark(name, x, y, size):
    """A 24-unit icon placed at (x, y) and scaled to `size` px, in the accent colour."""
    s = size / 24
    name = ICON_ALIAS.get(name, name)
    head = f'<g transform="translate({x} {y}) scale({s:.4f})">'
    if name == "sql":       # database cylinder
        body = ('<ellipse class="acs" cx="12" cy="5" rx="8" ry="3" fill="none" stroke-width="2"/>'
                '<path class="acs" d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" '
                'fill="none" stroke-width="2"/>')
    elif name == "powerbi":   # three rising bars
        body = ('<rect class="ac" x="2.5" y="12" width="5" height="10" rx="1.4"/>'
                '<rect class="ac" x="9.5" y="7" width="5" height="15" rx="1.4"/>'
                '<rect class="ac" x="16.5" y="2" width="5" height="20" rx="1.4"/>')
    elif name == "excel":   # sheet with a cross
        body = ('<rect class="ac" x="2" y="2" width="20" height="20" rx="4"/>'
                '<path class="bgs" d="M8 7l8 10M16 7L8 17" stroke-width="2.6" '
                'stroke-linecap="round" fill="none"/>')
    elif name == "catboost":  # boosted trees: three stumps, growing
        body = ''.join(f'<path class="acs" d="M{x} {y0}v4M{x} {y0 + 4}l-2.6 4M{x} {y0 + 4}l2.6 4" '
                       f'fill="none" stroke-width="1.8" stroke-linecap="round"/>'
                       f'<circle class="ac" cx="{x}" cy="{y0}" r="1.9"/>'
                       for x, y0 in ((4.5, 11), (12, 7), (19.5, 3)))
        body += '<path class="acs" d="M2 22h20" stroke-width="1.8" stroke-linecap="round"/>'
    elif name == "shap":     # waterfall of +/- contributions
        body = ''.join(f'<rect class="ac" x="{x}" y="{y}" width="{w}" height="3.2" rx="1"/>'
                       for x, y, w in ((3, 3, 9), (12, 7.5, 6), (9, 12, 3), (9, 16.5, 11)))
        body += '<path class="acs" d="M3 21.5h18" stroke-width="1.4" stroke-linecap="round"/>'
    elif name == "umap":     # points falling into clusters
        pts = ((5, 6), (7.5, 4.5), (4, 9), (7, 8), (17, 5), (19.5, 7.5), (16, 8.5),
               (10, 17), (13, 19), (11.5, 15), (14.5, 16.5), (21, 19))
        body = ''.join(f'<circle class="ac" cx="{x}" cy="{y}" r="1.7"/>' for x, y in pts)
    elif name == "bertopic":  # a cluster with a topic tag
        body = (''.join(f'<circle class="ac" cx="{x}" cy="{y}" r="1.8"/>'
                        for x, y in ((5, 14), (8, 11), (7, 17.5), (10.5, 15), (4, 19)))
                + '<path class="ac" d="M13 3h7.5a1.5 1.5 0 0 1 1.5 1.5v4a1.5 1.5 0 0 1-1.5 1.5H13l-3-3.5z"/>'
                + '<path class="acs" d="M11 12.5l3-3" stroke-width="1.6" stroke-linecap="round"/>')
    elif name == "email":   # envelope
        body = ('<rect class="acs" x="2.5" y="5" width="19" height="14" rx="2.5" '
                'fill="none" stroke-width="2"/>'
                '<path class="acs" d="M3.5 7l8.5 6 8.5-6" fill="none" stroke-width="2" '
                'stroke-linejoin="round" stroke-linecap="round"/>')
    else:
        body = f'<path class="ac" d="{icon_path(name)}"/>'
    return head + body + "</g>"


# ---------------------------------------------------------------------------
def build_typing():
    W, H, FS = 760, 56, 26
    CW = FS * 0.6                  # monospace advance
    TYPE, HOLD, ERASE, GAP = 0.07, 1.6, 0.03, 0.35   # seconds
    spans = []                     # (line, start, per-char type times...)
    t = 0.0
    for line in TAGLINES:
        n = len(line)
        dur = n * TYPE + HOLD + n * ERASE + GAP
        spans.append((line, t, dur))
        t += dur
    T = t

    clips, texts, caret_pts = [], [], []
    for i, (line, start, dur) in enumerate(spans):
        n = len(line)
        x0 = W / 2 - n * CW / 2
        pts = [(0.0, 0.0)]
        for k in range(1, n + 1):                       # typing
            pts.append((start + k * TYPE, k * CW))
        hold_end = start + n * TYPE + HOLD
        for k in range(n - 1, -1, -1):                  # erasing
            pts.append((hold_end + (n - k) * ERASE, k * CW))
        pts.append((T, 0.0))
        # de-duplicate equal times, keep order
        clean = []
        for tm, v in pts:
            tm = round(tm / T, 5)
            if clean and tm <= clean[-1][0]:
                clean[-1] = (clean[-1][0], v)
            else:
                clean.append((tm, v))
        clean[-1] = (1.0, clean[-1][1])
        kt = ";".join(f"{a:g}" for a, _ in clean)
        vals = ";".join(f"{b:.1f}" for _, b in clean)
        base = n * CW if i == 0 else 0                  # still shows line 1 if animation is off
        clips.append(
            f'<clipPath id="c{i}"><rect x="{x0:.1f}" y="0" height="{H}" width="{base:.1f}">'
            f'<animate attributeName="width" calcMode="discrete" dur="{T:.2f}s" '
            f'repeatCount="indefinite" keyTimes="{kt}" values="{vals}"/></rect></clipPath>')
        texts.append(f'<text class="fg" x="{x0:.1f}" y="37" clip-path="url(#c{i})">'
                     f'{xesc(line)}</text>')
        caret_pts += [(tm, x0 + v) for tm, v in clean if 0 < tm < 1]

    caret_pts.sort()
    first_x = W / 2 + len(TAGLINES[0]) * CW / 2
    kt = "0;" + ";".join(f"{a:g}" for a, _ in caret_pts) + ";1"
    vals = f"{first_x:.1f};" + ";".join(f"{b:.1f}" for _, b in caret_pts) + f";{first_x:.1f}"
    caret = (f'<rect class="ac" x="{first_x + 3:.1f}" y="13" width="3" height="31" rx="1">'
             f'<animate attributeName="x" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite" '
             f'keyTimes="{kt}" values="{vals}"/>'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" '
             f'repeatCount="indefinite"/></rect>')
    inner = (f'<defs>{"".join(clips)}</defs>'
             f'<g font-family="{MONO}" font-size="{FS}">{"".join(texts)}</g>{caret}')
    return svg(W, H, inner, " · ".join(TAGLINES))


# --- About Me cards: box-drawn "files", same frame and width -----------------
WHOAMI = [  # (key, wrapped lines)
    ("study", ["BSc International Business, Finance major",
               "MSc Organizational Management, 3 business schools",
               "potential switch to Digital Financial Technology"]),
    ("work",  ["Agentic workflows (n8n) & business",
               "intelligence for SMEs and startups"]),
    ("build", ["XGBoost decision engine scoring tabular",
               "transactions in <50 ms for digital banks"]),
    ("competed", ["RAISE Hackathon Paris: top 3% of 922 teams,",
                  "cross-border payment fraud model (€7k prize)"]),
]
BASED_IN = "Maastricht, NL"
LANGUAGES = [("English", 10, "native"), ("Russian", 10, "native"),
             ("Dutch", 7, "professional"), ("Japanese", 2, "learning"),
             ("German", 2, "learning")]
# certificate each "learning" language is aiming for: language -> (certificate, by when)
CERT_TARGETS = {"Japanese": ("JLPT N5", "Dec 2027"),
                "German": ("Goethe B1", "Dec 2028")}
OFF_SCREEN = ["live-coding music", "Hyrox & boxing", "wine tasting"]

CARD_FS, CARD_CW, CARD_LH = 13, 13 * 0.6, 22
CARD_INNER = 63                          # characters inside the frame (fits the cert reveal)
OFF_SCREEN_WRAP = 52                     # characters per off_screen line

# cert reveal: types in after "learning", holds, erases; one shared loop, rows staggered
REVEAL_COL = 37                          # one space after the level word (col 28 + 8 + 1)
REVEAL_TYPE, REVEAL_HOLD, REVEAL_ERASE = 0.06, 3.0, 0.025   # seconds
REVEAL_LOOP = 14.0                       # seconds for the whole cycle
REVEAL_STARTS = [1.5, 8.0]               # when each target row starts typing, in order


def reveal(i, x0, y, pieces, start):
    """Typed reveal of inline pieces [(text, class)] at (x0, y): a clip rect grows a
    character at a time, holds, then shrinks (the build_typing technique), with a
    blinking caret that is shown only while the reveal is on screen."""
    CW, T = CARD_CW, REVEAL_LOOP
    n = sum(len(t) for t, _ in pieces)
    pts = [(0.0, 0)]
    pts += [(start + k * REVEAL_TYPE, k) for k in range(1, n + 1)]
    hold_end = start + n * REVEAL_TYPE + REVEAL_HOLD
    pts += [(hold_end + (n - k) * REVEAL_ERASE, k) for k in range(n - 1, -1, -1)]
    end = pts[-1][0]
    clean = []
    for tm, v in pts:
        tm = round(tm / T, 5)
        if clean and tm <= clean[-1][0]:
            clean[-1] = (clean[-1][0], v)
        else:
            clean.append((tm, v))
    clean.append((1.0, 0))
    kt = ";".join(f"{a:g}" for a, _ in clean)
    # real monospace advances run a little over 0.6em, so give the clip some slack
    px = lambda v: v * CW * 1.03 + (2 if v else 0)
    widths = ";".join(f"{px(v):.1f}" for _, v in clean)
    xs = ";".join(f"{x0 + 1 + px(v):.1f}" for _, v in clean)
    on, off = round(start / T, 5), round(end / T, 5)
    anim = f'dur="{T:g}s" repeatCount="indefinite"'
    body = "".join(f'<tspan class="{c}">{xesc(t)}</tspan>' for t, c in pieces)
    # base width = full text, so a viewer without SMIL still shows the target
    return (f'<clipPath id="r{i}"><rect x="{x0:.1f}" y="{y - 14}" height="18" width="{px(n):.1f}">'
            f'<animate attributeName="width" calcMode="discrete" {anim} keyTimes="{kt}" '
            f'values="{widths}"/></rect></clipPath>'
            f'<text x="{x0:.1f}" y="{y}" clip-path="url(#r{i})" xml:space="preserve">{body}</text>'
            f'<rect class="ac" x="{x0 + 1:.1f}" y="{y - 11}" width="1.6" height="14" visibility="hidden">'
            f'<animate attributeName="x" calcMode="discrete" {anim} keyTimes="{kt}" values="{xs}"/>'
            f'<animate attributeName="visibility" calcMode="discrete" {anim} '
            f'keyTimes="0;{on:g};{off:g}" values="hidden;visible;hidden"/>'
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" '
            f'repeatCount="indefinite"/></rect>')


def frame(title, rows, label, extra=""):
    """rows: list of rows; each row is a list of (column, text, class, bold).
    An empty list is a blank line. Border runs are stretched with textLength so
    the corners meet in any monospace font."""
    CW, LH, inner = CARD_CW, CARD_LH, CARD_INNER
    W = (inner + 2) * CW
    top = 22
    H = top + (len(rows) + 1) * LH + 8
    bottom = H - 14
    title = f" {title} "

    def run(y, s, x1, x2):
        return (f'<text class="ac" x="{x1:.1f}" y="{y}" textLength="{x2 - x1:.1f}" '
                f'lengthAdjust="spacingAndGlyphs">{s}</text>')

    p = [
        f'<text class="ac" x="0" y="{top}">┌─</text>',
        f'<text class="fg" x="{2 * CW:.1f}" y="{top}" font-weight="700">{xesc(title)}</text>',
        run(top, "─" * (inner - len(title) - 1), (2 + len(title)) * CW, W - CW),
        f'<text class="ac" x="{W - CW:.1f}" y="{top}">┐</text>',
        f'<text class="ac" x="0" y="{bottom}">└</text>',
        run(bottom, "─" * inner, CW, W - CW),
        f'<text class="ac" x="{W - CW:.1f}" y="{bottom}">┘</text>',
    ]
    for i, row in enumerate(rows):
        y = top + (i + 1) * LH
        for col, text, cls, bold in row:
            weight = ' font-weight="700"' if bold else ""
            if isinstance(text, list):      # inline pieces that flow together: [(text, class, bold)]
                bw = ' font-weight="700"'
                body = "".join(f'<tspan class="{c}"{bw if b else ""}>{xesc(t)}</tspan>'
                               for t, c, b in text)
                p.append(f'<text x="{(3 + col) * CW:.1f}" y="{y}" xml:space="preserve">{body}</text>')
                continue
            p.append(f'<text class="{cls}" x="{(3 + col) * CW:.1f}" y="{y}"{weight} '
                     f'xml:space="preserve">{xesc(text)}</text>')
    for yy in range(top + LH // 2, bottom - LH // 2 + 1, LH // 2):   # side rails
        p.append(f'<text class="ac" x="0" y="{yy + 4}">│</text>')
        p.append(f'<text class="ac" x="{W - CW:.1f}" y="{yy + 4}">│</text>')
    return svg(round(W, 1), H, f'<g font-family="{MONO}" font-size="{CARD_FS}">{"".join(p)}{extra}</g>', label)


def build_whoami():
    KEY, rows = max(len(k) for k, _ in WHOAMI) + 3, []   # label column fits the longest key
    for i, (key, lines) in enumerate(WHOAMI):
        for j, line in enumerate(lines):
            row = [(KEY, line, "fg", False)]
            if j == 0:
                row = [(0, key, "ac", True), (KEY - 2, "→", "mu", False)] + row
            rows.append(row)
        if i < len(WHOAMI) - 1:
            rows.append([])
    label = "Who am I. " + " ".join(f"{k}: {' '.join(ls)}." for k, ls in WHOAMI)
    return frame("whoami.txt", rows, label)


def wrap_items(items, width):
    """Quote and comma-join items, breaking onto new lines so none exceeds width."""
    lines, cur = [], ""
    for i, it in enumerate(items):
        piece = f'"{it}"' + ("," if i < len(items) - 1 else "")
        if cur and len(cur) + 1 + len(piece) > width:
            lines.append(cur)
            cur = piece
        else:
            cur = f"{cur} {piece}" if cur else piece
    return lines + [cur]


def build_profile():
    def kv(indent, key, rest):
        """One flowing line: "key": followed by value pieces [(text, class)]."""
        return [(indent, [(f'"{key}"', "ac", True), (": ", "mu", False)]
                 + [(t, c, False) for t, c in rest], None, False)]

    rows = [[(0, "{", "mu", False)],
            kv(2, "based_currently_in", [(f'"{BASED_IN}"', "fg"), (",", "mu")]),
            kv(2, "languages", [("{", "mu")])]
    reveals = []                         # (row index, language)
    for name, level, word in LANGUAGES:
        bar = [(17, "█" * level, "ac", False)] if level else []
        if level < 10:
            bar.append((17 + level, "░" * (10 - level), "mu", False))
        if name in CERT_TARGETS:
            reveals.append((len(rows), name))
        rows.append([(4, f'"{name}"', "fg", False)] + bar + [(28, word, "mu", False)])
    rows += [[(2, "},", "mu", False)],
             kv(2, "off_screen", [("[", "mu")]),
             *[[(4, line, "fg", False)] for line in wrap_items(OFF_SCREEN, OFF_SCREEN_WRAP)],
             [(2, "]", "mu", False)],
             [(0, "}", "mu", False)]]
    label = (f"Profile. Based currently in {BASED_IN}. Languages: "
             + ", ".join(f"{n} ({w})" for n, _, w in LANGUAGES)
             + ". Certificate targets: "
             + ", ".join(f"{n} {c} by {d}" for n, (c, d) in CERT_TARGETS.items())
             + ". Off-screen: " + ", ".join(OFF_SCREEN) + ".")
    extra = ""
    for k, (r, name) in enumerate(reveals):
        cert, by = CERT_TARGETS[name]
        x0 = (3 + REVEAL_COL) * CARD_CW
        y = 22 + (r + 1) * CARD_LH            # frame(): top + (row + 1) * line height
        extra += reveal(k, x0, y, [("→ ", "mu"), (cert, "ac"), (f" · {by}", "fg")],
                        REVEAL_STARTS[k % len(REVEAL_STARTS)])
    return frame("profile.json", rows, label, extra)


# --- Tech stack ---------------------------------------------------------------
# stack-mastered.svg is one row of tiles. The learning part is split so the README
# can wrap each language in <details>: a heading per group, a clickable card per
# language (learn-<slug>.svg, the <summary>) and a panel of what's inside
# (learn-<slug>-libs.svg, the opened body).
STACK_W = 712
TW, TH, TGAP = 72, 84, 8


def section_title(x, y, title):
    return (f'<text class="mu" x="{x}" y="{y}" text-anchor="middle" font-family="{SANS}" '
            f'font-size="11" font-weight="700" letter-spacing="2.5">{xesc(title)}</text>')


def tiles(names, y, dashed=False):
    span = len(names) * TW + (len(names) - 1) * TGAP
    x0 = (STACK_W - span) / 2
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    out = []
    for i, name in enumerate(names):
        x = x0 + i * (TW + TGAP)
        out.append(f'<rect class="cd" x="{x + .5}" y="{y + .5}" width="{TW - 1}" height="{TH - 1}" rx="12"{dash}/>')
        out.append(mark(name, x + TW / 2 - 16, y + 14, 32))
        out.append(f'<text class="fg" x="{x + TW / 2}" y="{y + 68}" text-anchor="middle" '
                   f'font-family="{SANS}" font-size="11.5" font-weight="600">{xesc(LABELS[name])}</text>')
    return out


def build_stack_mastered():
    LBL = 22
    inner = [section_title(STACK_W / 2, 12, "MASTERED")] + tiles(MASTERED, LBL)
    label = "Mastered: " + ", ".join(LABELS[n] for n in MASTERED) + "."
    return svg(STACK_W, LBL + TH, "".join(inner), label)


def build_learn_heading(title):
    W, H = STACK_W, 40
    inner = (section_title(W / 2, 14, title)
             + f'<text class="ac" x="{W / 2}" y="33" text-anchor="middle" font-family="{MONO}" '
               f'font-size="11">{xesc("click a language to see what I am learning in it ▾")}</text>')
    return svg(W, H, inner, f"{title.title()}. Click a language to see what I am learning in it.")


def hint(items, noun):
    return f"{len(items)} {noun} ▸"


def build_learn_card(lang, icons, items, noun):
    """The clickable row: icon(s), language, and how many things sit inside."""
    W, H, IS = STACK_W, 60, 28
    p = [f'<rect class="cd" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" stroke-dasharray="5 4"/>']
    x = 20
    for name in icons:
        p.append(mark(name, x, (H - IS) / 2, IS))
        x += IS + 6
    p.append(f'<text class="fg" x="{x + 8}" y="{H / 2 + 5.5}" font-family="{SANS}" font-size="16" '
             f'font-weight="700">{xesc(lang)}</text>')
    p.append(f'<text class="ac" x="{W - 22}" y="{H / 2 + 4.5}" text-anchor="end" font-family="{MONO}" '
             f'font-size="13">{xesc(hint(items, noun))}</text>')
    label = f"{lang}: {len(items)} {noun}. Click to show them."
    return svg(W, H, "".join(p), label)


def build_learn_panel(lang, items, noun, caption):
    """What's inside a language: tiles in the Learning (dashed) style."""
    CAP = 26
    inner = ([f'<text class="mu" x="{STACK_W / 2}" y="14" text-anchor="middle" font-family="{MONO}" '
              f'font-size="11.5">{xesc(f"{lang.lower()} → {caption}")}</text>']
             + tiles(items, CAP, dashed=True))
    label = f"Learning in {lang}: " + ", ".join(LABELS[n] for n in items) + f" ({caption})."
    return svg(STACK_W, CAP + TH + 2, "".join(inner), label)


def stack_outputs():
    out = {"stack-mastered.svg": build_stack_mastered()}
    for key, (title, langs) in LEARNING_GROUPS.items():
        out[f"learn-{key}.svg"] = build_learn_heading(title)
        for slug, lang, icons, items, noun, caption in langs:
            out[f"learn-{slug}.svg"] = build_learn_card(lang, icons, items, noun)
            out[f"learn-{slug}-libs.svg"] = build_learn_panel(lang, items, noun, caption)
    return out


def build_connect(name, label):
    W, H = 168, 44
    inner = (f'<rect class="cd" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22"/>'
             + mark(name, 20, 12, 20)
             + f'<text class="fg" x="52" y="27.5" font-family="{SANS}" font-size="14" '
               f'font-weight="600">{label}</text>')
    return svg(W, H, inner, label)


def build_wave():
    W, H = 1600, 140
    inner = (
        '<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0">'
        '<stop offset="0" stop-color="#852f45"/><stop offset=".5" stop-color="#e04060"/>'
        '<stop offset="1" stop-color="#f6c6cf"/></linearGradient></defs>'
        f'<path fill="url(#g)" opacity=".35" d="M0 70 C 260 20 520 120 800 70 S 1340 20 {W} 60 V {H} H 0 Z"/>'
        f'<path fill="url(#g)" d="M0 95 C 300 55 560 135 820 95 S 1360 60 {W} 92 V {H} H 0 Z"/>'
    )
    return svg(W, H, inner, "")


def main():
    outputs = {"whoami.svg": build_whoami(), "profile.svg": build_profile(), "typing.svg": build_typing(), "wave.svg": build_wave(),
               **stack_outputs()}
    for name, label in CONNECT:
        outputs[f"connect-{name}.svg"] = build_connect(name, label)
    for name, content in outputs.items():
        (ART / name).write_text(content)
        print(f"wrote art/{name} ({len(content)} bytes)")


if __name__ == "__main__":
    main()

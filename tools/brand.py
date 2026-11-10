#!/usr/bin/env python3
"""Generate the site's icon set and social card.

    python3 tools/brand.py          (needs Pillow: pip install pillow)

Writes assets/icon.svg, assets/icon-{48,96,192,512}.png, assets/apple-touch-icon.png,
favicon.ico and assets/og-card.jpg. The page itself is set in Geist (Google Fonts);
the card uses the macOS system fonts Helvetica Neue and Menlo, so re-run it on a Mac.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Colour tokens, same as assets/style.css (light scheme)
BG, TEXT, MUTED, FAINT, LINE = "#fafaf8", "#1b1b1a", "#5f5e59", "#73726c", "#e4e2dc"
ACCENT, ACCENT_SOFT = "#2e6150", "#e3eee9"
AWARD, AWARD_SOFT, AWARD_LINE = "#1f5fae", "#e8f1fc", "#c6dbf5"
INK, PAPER, DOT = "#1b1b1a", "#fafaf8", "#84c2ab"

HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"  # 0 Regular, 1 Bold, 10 Medium
MENLO = "/System/Library/Fonts/Menlo.ttc"


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


# ---------------------------------------------------------------- icon mark
# One stroke "M" and the site's status dot on an ink square (100-unit grid).
M_POINTS = [(20, 72), (20, 28), (45, 55), (70, 28), (70, 72)]
M_STROKE = 11
DOT_XY, DOT_R = (86, 67), 6.5
CORNER = 22

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="22" fill="#1b1b1a"/>
  <path d="M20 72V28l25 27 25-27v44" fill="none" stroke="#fafaf8" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="86" cy="67" r="6.5" fill="#84c2ab"/>
</svg>
"""


def mark(size, rounded=True, scale=8):
    """Render the mark at `size` px, drawn 8x larger and downsampled for clean edges."""
    big = size * scale
    u = big / 100
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle([0, 0, big - 1, big - 1], radius=CORNER * u, fill=INK)
    else:
        d.rectangle([0, 0, big, big], fill=INK)
    pts = [(x * u, y * u) for x, y in M_POINTS]
    w = M_STROKE * u
    d.line(pts, fill=PAPER, width=round(w), joint="curve")
    for x, y in (pts[0], pts[-1]):  # round caps
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=PAPER)
    cx, cy, r = DOT_XY[0] * u, DOT_XY[1] * u, DOT_R * u
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DOT)
    return img.resize((size, size), Image.LANCZOS)


def icons():
    (ASSETS / "icon.svg").write_text(ICON_SVG)
    for s in (48, 96, 192, 512):
        mark(s).save(ASSETS / f"icon-{s}.png", optimize=True)
    mark(180, rounded=False).convert("RGB").save(ASSETS / "apple-touch-icon.png", optimize=True)
    mark(256).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


# -------------------------------------------------------------- social card
def tracked_width(d, s, f, tracking):
    return sum(d.textlength(ch, font=f) for ch in s) + tracking * (len(s) - 1)


def draw_tracked(d, xy, s, f, fill, tracking=0.0):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking
    return x


def wrap(d, s, f, max_w):
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def medal(d, x, y, color, s=1.0):
    """Tiny award icon matching the page's: a circle on two ribbon legs."""
    r = 5 * s
    d.ellipse([x - r, y - r, x + r, y + r], outline=color, width=max(1, round(1.8 * s)))
    d.line([(x - 3 * s, y + 4 * s), (x - 4.5 * s, y + 11 * s), (x, y + 8.5 * s), (x + 4.5 * s, y + 11 * s), (x + 3 * s, y + 4 * s)],
           fill=color, width=max(1, round(1.8 * s)), joint="curve")


def card():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0, right_limit = 84, 790

    # Eyebrow with the status dot
    mono = font(MENLO, 19)
    d.ellipse([x0 - 1, 97, x0 + 15, 113], fill=ACCENT_SOFT)
    d.ellipse([x0 + 3, 101, x0 + 11, 109], fill=ACCENT)
    draw_tracked(d, (x0 + 28, 94), "ROBOTICS R&D · RESEARCH & INDUSTRY", mono, MUTED, tracking=2.2)

    # Name, fitted to the column
    size = 92
    while True:
        bold = font(HELVETICA, size, 1)
        tr = -size * 0.035
        if max(tracked_width(d, s, bold, tr) for s in ("Athanasios", "Mastrogeorgiou")) <= right_limit - x0 - 20 or size <= 56:
            break
        size -= 2
    y = 146
    draw_tracked(d, (x0 - 4, y), "Athanasios", bold, TEXT, tracking=tr)
    draw_tracked(d, (x0 - 4, y + size * 0.98), "Mastrogeorgiou", bold, TEXT, tracking=tr)

    # One line of substance
    reg = font(HELVETICA, 27, 0)
    med = font(HELVETICA, 27, 10)
    y2 = y + size * 1.96 + 30
    lead = "Perception, motion planning and control"
    rest = " for legged and field robots, from simulation to deployment."
    lines = wrap(d, lead + rest, reg, right_limit - x0)
    yy = y2
    for i, ln in enumerate(lines):
        if i == 0 and ln.startswith(lead):
            d.text((x0, yy), lead, font=med, fill=TEXT)
            d.text((x0 + d.textlength(lead, font=med), yy), ln[len(lead):], font=reg, fill=MUTED)
        else:
            d.text((x0, yy), ln, font=reg, fill=MUTED)
        yy += 38

    # Award chips, blue as on the page
    chipf = font(HELVETICA, 18, 10)
    x, yc, h = x0, yy + 30, 40
    for label in ("Best Agri-Robotics Paper Finalist · IROS 2024", "Best Paper Finalist · AIM 2023", "Second Prize · CLAWAR 2020"):
        w = d.textlength(label, font=chipf) + 52
        if x + w > right_limit:
            x, yc = x0, yc + h + 10
        d.rounded_rectangle([x, yc, x + w, yc + h], radius=8, fill=AWARD_SOFT, outline=AWARD_LINE, width=2)
        medal(d, x + 20, yc + 15, AWARD, 1.0)
        d.text((x + 36, yc + 9), label, font=chipf, fill=AWARD)
        x += w + 10

    # Portrait as a plate, address beneath it
    cx, cy, r = 985, 300, 160
    d.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], outline=LINE, width=2)
    portrait = Image.open(ASSETS / "img" / "portrait-960.jpg").convert("RGB")
    portrait = Image.blend(portrait, ImageOps.grayscale(portrait).convert("RGB"), 0.15)
    big = 4 * 2 * r
    p = portrait.resize((big, big), Image.LANCZOS)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, big - 1, big - 1], fill=255)
    img.paste(p.resize((2 * r, 2 * r), Image.LANCZOS), (cx - r, cy - r), mask.resize((2 * r, 2 * r), Image.LANCZOS))
    url = font(MENLO, 21)
    uw = tracked_width(d, "mastrogeorgiou.gr", url, 1.2)
    draw_tracked(d, (cx - uw / 2, cy + r + 40), "mastrogeorgiou.gr", url, FAINT, tracking=1.2)

    img.save(ASSETS / "og-card.jpg", quality=90, optimize=True, progressive=True, subsampling=0)
    return size, lines


if __name__ == "__main__":
    icons()
    size, lines = card()
    print(f"icons written; card written (name at {size}px, {len(lines)} lede line(s))")

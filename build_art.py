#!/usr/bin/env python3
"""Paint the Twenty-One front page, round three.

Run locally (never by the grader) to produce entry.png: a broadsheet
front page summing up Saturday 21 November 2026. Round three keeps the
broadsheet format of round two but adds what it lacked: a hero
illustration for the lead story (missile trails over a European city
at dusk, hero.png, drawn for this page) and a small market chart in
the New York cell, and refreshes the stories with the later news cycle
-- the Nasdaq's 5.3% plunge, the 6.8 Peru quake and the record
Anthropic IPO.

Everything is drawn with PIL and the DejaVu fonts installed on this
machine, plus the one generated illustration; no network, no photos,
no invented quotes -- every story is paraphrased from the 21 November
2026 news cycle and sourced in README.md.

Usage:
    python3 build_art.py            # writes entry.png next to this file
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
EDGE = 40
NEWSROOM = (247, 242, 231)
BLACK = (18, 18, 18)
GREY = (64, 64, 64)
CRIMSON = (163, 22, 33)
DARKBLUE = (27, 42, 74)
PALE = (150, 142, 128)
PANEL = (232, 226, 212)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

HERE = os.path.dirname(os.path.abspath(__file__))
HERO_SRC = os.path.join(HERE, "hero.png")


def load(path, size):
    """Load one font file at the requested point size."""
    return ImageFont.truetype(path, size)


def split_lines(draw, text, fnt, max_w):
    """Greedy word wrap: lines of `text` that each fit inside max_w px."""
    out = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if not current or draw.textlength(trial, font=fnt) <= max_w:
            current = trial
        else:
            out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def paragraph(draw, x, y, text, fnt, colour, max_w, spacing):
    """Draw wrapped text; return the y just below the last line."""
    for line in split_lines(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=colour)
        y += spacing
    return y


def rule_pair(draw, y, x0=EDGE, x1=CANVAS - EDGE):
    """A broadsheet double rule: thick line over a thin one."""
    draw.line([(x0, y), (x1, y)], fill=BLACK, width=3)
    draw.line([(x0, y + 5), (x1, y + 5)], fill=BLACK, width=1)


def centred(draw, y, text, fnt, colour):
    """Draw one line centred on the page; return its pixel width."""
    width = draw.textlength(text, font=fnt)
    draw.text(((CANVAS - width) / 2, y), text, font=fnt, fill=colour)
    return width


def story(draw, x, y, width, kicker, headline, body,
          head_px, head_gap, body_px, body_gap, kick_px=17):
    """Kicker + headline + body in one column; return the bottom y."""
    draw.text((x, y), kicker, font=load(SANS_B, kick_px), fill=CRIMSON)
    y += kick_px + 8
    y = paragraph(draw, x, y, headline, load(SERIF_B, head_px),
                  BLACK, width, head_gap)
    y += 6
    y = paragraph(draw, x, y, body, load(SERIF, body_px),
                  GREY, width, body_gap)
    return y


# ------------------------------------------------------------------ content
FRONT = (
    "LEAD STORY  \u2022  POLAND",
    "Russian missiles land in Poland as NATO calls it a grave violation",
    "Two Russian missiles and a suspected drone came down in Poland, which "
    "called it a deliberate provocation. NATO called it a grave violation "
    "of allied airspace.",
)

HERO_CAPTION = ("Illustration: missile trails over a European city at dusk.")

QUARTET = [
    (
        "NEW YORK",
        "Nasdaq nears bear market as AI sell-off deepens",
        "The Nasdaq plunged 5.3% on Friday and Nvidia fell about 14%. "
        "The S&P 500 and the Dow are in correction.",
    ),
    (
        "JUN\u00cdN, PERU",
        "Magnitude 6.8 quake shakes central Peru",
        "A magnitude 6.8 earthquake struck the Andean region of Jun\u00edn, "
        "with tremors felt in Lima, around 320 km away.",
    ),
    (
        "THE HAGUE",
        "ICJ: Myanmar committed genocide",
        "The International Court of Justice ruled Myanmar's security forces "
        "committed state-sponsored genocide against the Rohingya in the "
        "2017 crackdown.",
    ),
    (
        "SAN FRANCISCO",
        "Anthropic's $119.5bn IPO is the largest ever",
        "Anthropic closed its IPO with proceeds of $119.5 billion, "
        "surpassing SpaceX's $85.7 billion record debut.",
    ),
]

BRIEFS = [
    ("SHENZHEN", "Trump, Xi and Putin leave their first trilateral summit "
                 "with few concrete results."),
    ("BRUSSELS", "UK and EU sign deals on food trade, carbon markets and "
                 "youth mobility."),
    ("ODISHA", "Cyclone Akvan crosses the coast near Gopalpur with strong "
               "winds and heavy rain."),
    ("WASHINGTON", "FBI investigates a suspected hack of a nationwide law "
                   "enforcement crime database."),
    ("GAZA", "Australia, Canada, Italy and the UK call for aid to reach "
             "flooded Gaza."),
    ("WELLINGTON", "KL Rahul's century makes him the first Indian opener "
                   "with Test hundreds in all SENA countries."),
]

# Nasdaq Friday path, indexed points for the mini chart (open = 100).
NASDAQ_PATH = [100, 99.4, 98.1, 98.6, 96.9, 95.8, 96.2, 94.7]


# ------------------------------------------------------------------ sections
def paint_masthead(draw):
    centred(draw, 12, "TWENTY-ONE", load(SERIF_B, 84), BLACK)
    rule_pair(draw, 112)
    centred(draw, 128, "SATURDAY  \u2022  21  NOVEMBER  2026",
            load(SANS_B, 26), CRIMSON)
    centred(draw, 160, "THE WORLD IN ONE PAGE \u2014 ELEVEN STORIES THAT "
            "DEFINED THE DAY", load(SANS, 17), GREY)
    rule_pair(draw, 186)


def paint_hero(sheet, draw, top, height=160):
    """Paste the hero illustration full-width with a caption below."""
    hero = Image.open(HERO_SRC).convert("RGB")
    w, h = hero.size
    target_ratio = (CANVAS - 2 * EDGE) / height
    # Crop the middle band to the panel's aspect ratio, then scale.
    if w / h > target_ratio:
        crop_w = int(h * target_ratio)
        left = (w - crop_w) // 2
        hero = hero.crop((left, 0, left + crop_w, h))
    else:
        crop_h = int(w / target_ratio)
        top_px = (h - crop_h) // 2
        hero = hero.crop((0, top_px, w, top_px + crop_h))
    hero = hero.resize((CANVAS - 2 * EDGE, height), Image.LANCZOS)
    sheet.paste(hero, (EDGE, top))
    draw.rectangle([(EDGE, top), (CANVAS - EDGE, top + height)],
                   outline=BLACK, width=2)
    caption_y = top + height + 6
    return paragraph(draw, EDGE, caption_y, HERO_CAPTION,
                     load(SERIF, 13), GREY, CANVAS - 2 * EDGE, 17)


def paint_front(draw, top):
    kicker, headline, body = FRONT
    bottom = story(draw, EDGE, top, CANVAS - 2 * EDGE, kicker, headline,
                   body, head_px=32, head_gap=37, body_px=16, body_gap=21,
                   kick_px=18)
    return bottom + 8


def paint_mini_chart(draw, x, y, width, height=34):
    """A small plunging Nasdaq line chart with its Friday fall labelled."""
    draw.rectangle([(x, y), (x + width, y + height)], fill=PANEL,
                   outline=PALE, width=1)
    lo = min(NASDAQ_PATH)
    hi = max(NASDAQ_PATH)
    span = hi - lo or 1
    pts = []
    for i, v in enumerate(NASDAQ_PATH):
        px = x + 8 + (width - 16) * i / (len(NASDAQ_PATH) - 1)
        py = y + 6 + (height - 12) * (hi - v) / span
        pts.append((px, py))
    draw.line(pts, fill=CRIMSON, width=2)
    draw.text((x + width - 52, y + 4), "\u22125.3%",
              font=load(SANS_B, 13), fill=CRIMSON)
    draw.text((x + 8, y + height - 16), "NASDAQ, FRIDAY",
              font=load(SANS, 10), fill=GREY)
    return y + height


def paint_quartet(draw, top):
    col = (CANVAS - 2 * EDGE - 36) // 2
    left_x = EDGE
    right_x = EDGE + col + 36
    y = top
    low_l = story(draw, left_x, y, col, *QUARTET[0],
                  head_px=24, head_gap=28, body_px=13, body_gap=16)
    low_l = paint_mini_chart(draw, left_x, low_l + 6, col) + 4
    low_r = story(draw, right_x, y, col, *QUARTET[1],
                  head_px=24, head_gap=28, body_px=13, body_gap=16)
    y = max(low_l, low_r) + 6
    draw.line([(EDGE, y), (CANVAS - EDGE, y)], fill=PALE, width=1)
    y += 6
    low_l = story(draw, left_x, y, col, *QUARTET[2],
                  head_px=24, head_gap=28, body_px=13, body_gap=16)
    low_r = story(draw, right_x, y, col, *QUARTET[3],
                  head_px=24, head_gap=28, body_px=13, body_gap=16)
    return max(low_l, low_r)


def paint_briefs(draw, top):
    draw.text((EDGE, top), "THE DAY IN BRIEF",
              font=load(SANS_B, 18), fill=BLACK)
    draw.line([(EDGE, top + 26), (CANVAS - EDGE, top + 26)],
              fill=BLACK, width=2)
    cols = 3
    gap = 24
    col = (CANVAS - 2 * EDGE - gap * (cols - 1)) // cols
    y = top + 32
    row_bottoms = []
    for row in range(2):
        bottom = y
        for c in range(cols):
            idx = row * cols + c
            if idx >= len(BRIEFS):
                break
            place, item = BRIEFS[idx]
            x = EDGE + c * (col + gap)
            draw.text((x, y), "\u2022", font=load(SANS_B, 14),
                      fill=CRIMSON)
            new_y = paragraph(draw, x + 14, y, place + ": " + item,
                              load(SERIF, 12), GREY, col - 14, 14)
            bottom = max(bottom, new_y)
        row_bottoms.append(bottom)
        y = bottom + 6
    return y


def paint_footer(draw, y):
    draw.text((EDGE, y),
              "All stories as reported on 21 November 2026. Hero "
              "illustration drawn for this page; no photos, no "
              "invented quotes.",
              font=load(SANS, 12), fill=PALE)


def paint_page():
    sheet = Image.new("RGB", (CANVAS, CANVAS), NEWSROOM)
    draw = ImageDraw.Draw(sheet)
    paint_masthead(draw)
    after_hero = paint_hero(sheet, draw, 202)
    after_front = paint_front(draw, after_hero + 8)
    after_quartet = paint_quartet(draw, after_front)
    after_briefs = paint_briefs(draw, after_quartet + 10)
    paint_footer(draw, CANVAS - 20)
    return sheet, after_briefs


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "entry.png")
    sheet, bottom = paint_page()
    print("content bottom y: %d (canvas %d)" % (bottom, CANVAS))
    sheet.save(target, "PNG", optimize=True)
    raw = open(target, "rb").read()
    size = len(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print("painted %s (%d bytes, sha256 %s)" % (target, size, digest))
    if size > 1024 * 1024:
        print("ERROR: entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    if bottom > CANVAS - 24:
        print("ERROR: content overflows the canvas", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

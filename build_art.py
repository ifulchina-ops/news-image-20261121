#!/usr/bin/env python3
"""Paint the Twenty-One front page.

Run locally (never by the grader) to produce entry.png: a broadsheet
front page summing up Saturday 21 November 2026. Everything is drawn
with PIL and the DejaVu fonts installed on this machine; no network,
no photos, no invented quotes -- every story is paraphrased from the
21 November 2026 news cycle and sourced in README.md.

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

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


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

QUARTET = [
    (
        "THE HAGUE",
        "ICJ: Myanmar committed genocide",
        "The International Court of Justice ruled Myanmar's security forces "
        "committed state-sponsored genocide against the Rohingya in the "
        "2017 crackdown.",
    ),
    (
        "SHENZHEN, CHINA",
        "Trump, Xi and Putin summit ends thin",
        "The first trilateral summit of the three leaders produced pledges "
        "but few concrete results. Trump was due to address Americans on "
        "his return from China.",
    ),
    (
        "NEW YORK",
        "Wall Street slumps into correction",
        "US stocks fell sharply on Friday, down about 3.7%, pushing the "
        "S&P 500 and the Dow into correction territory as AI and chip "
        "shares sold off.",
    ),
    (
        "BRUSSELS",
        "UK and EU sign new deals",
        "Britain and the EU signed agreements on food trade, carbon markets "
        "and youth mobility for ages 18 to 31 at a Brussels summit.",
    ),
]

FIGURES = [
    ("2", "missiles down in Poland"),
    ("3.7%", "S&P 500's Friday fall"),
    ("44%", "tumour response in trial"),
    ("42", "injured in Kryvyi Rih"),
    ("\u20ac1bn", "EU military aid for Ukraine"),
]

BRIEFS = [
    ("KYIV", "Russia hits Kyiv bridges in a massive attack; at least nine "
             "dead. Kryvyi Rih: two killed, 42 hurt."),
    ("ODISHA", "Cyclone Akvan crosses the Odisha coast near Gopalpur with "
               "strong winds and heavy rain."),
    ("COPENHAGEN", "Denmark charges two men over a Russian plot to kill a "
                   "US-Ukrainian rapper; attache expelled."),
    ("RIYADH", "Saudi coalition intercepts three Houthi missiles over "
               "Riyadh and strikes Hodeidah."),
    ("BARCELONA", "Erasca pill ERAS-0015 shrank tumours in 44% of "
                  "pancreatic cancer patients in trial."),
    ("ULAANBAATAR", "Mongolia's parliament accepts President Khurelsukh's "
                    "resignation, a first."),
]


# ------------------------------------------------------------------ sections
def paint_masthead(draw):
    centred(draw, 14, "TWENTY-ONE", load(SERIF_B, 88), BLACK)
    rule_pair(draw, 118)
    centred(draw, 134, "SATURDAY  \u2022  21  NOVEMBER  2026",
            load(SANS_B, 27), CRIMSON)
    centred(draw, 168, "THE WORLD IN ONE PAGE \u2014 TEN STORIES THAT "
            "DEFINED THE DAY", load(SANS, 18), GREY)
    rule_pair(draw, 194)


def paint_front(draw):
    kicker, headline, body = FRONT
    bottom = story(draw, EDGE, 210, CANVAS - 2 * EDGE, kicker, headline,
                   body, head_px=40, head_gap=45, body_px=19, body_gap=25,
                   kick_px=18)
    return bottom + 18


def paint_quartet(draw, top):
    col = (CANVAS - 2 * EDGE - 36) // 2
    left_x = EDGE
    right_x = EDGE + col + 36
    y = top
    low_l = story(draw, left_x, y, col, *QUARTET[0],
                  head_px=29, head_gap=33, body_px=15, body_gap=20)
    low_r = story(draw, right_x, y, col, *QUARTET[1],
                  head_px=29, head_gap=33, body_px=15, body_gap=20)
    y = max(low_l, low_r) + 10
    draw.line([(EDGE, y), (CANVAS - EDGE, y)], fill=PALE, width=1)
    y += 10
    low_l = story(draw, left_x, y, col, *QUARTET[2],
                  head_px=29, head_gap=33, body_px=15, body_gap=20)
    low_r = story(draw, right_x, y, col, *QUARTET[3],
                  head_px=29, head_gap=33, body_px=15, body_gap=20)
    return max(low_l, low_r)


def paint_figures(draw, top):
    height = 60
    draw.rectangle([(EDGE, top), (CANVAS - EDGE, top + height)], fill=BLACK)
    cell = (CANVAS - 2 * EDGE) // len(FIGURES)
    for i, (number, label) in enumerate(FIGURES):
        cx = EDGE + i * cell
        num_fnt = load(SANS_B, 24)
        w = draw.textlength(number, font=num_fnt)
        draw.text((cx + (cell - w) / 2, top + 8), number, font=num_fnt,
                  fill=(255, 255, 255))
        lab_fnt = load(SANS, 12)
        w = draw.textlength(label, font=lab_fnt)
        draw.text((cx + (cell - w) / 2, top + 38), label, font=lab_fnt,
                  fill=(200, 200, 200))
        if i:
            draw.line([(cx, top + 12), (cx, top + height - 12)],
                      fill=(90, 90, 90), width=1)
    return top + height


def paint_briefs(draw, top):
    draw.text((EDGE, top), "THE DAY IN BRIEF",
              font=load(SANS_B, 19), fill=BLACK)
    draw.line([(EDGE, top + 28), (CANVAS - EDGE, top + 28)],
              fill=BLACK, width=2)
    col = (CANVAS - 2 * EDGE - 36) // 2
    left_x = EDGE
    right_x = EDGE + col + 36
    y_left = y_right = top + 38
    for i, (place, item) in enumerate(BRIEFS):
        if i % 2 == 0:
            x, y = left_x, y_left
        else:
            x, y = right_x, y_right
        draw.text((x, y), "\u2022", font=load(SANS_B, 15), fill=CRIMSON)
        new_y = paragraph(draw, x + 16, y, place + ": " + item,
                          load(SERIF, 14), GREY, col - 16, 18)
        if i % 2 == 0:
            y_left = new_y + 6
        else:
            y_right = new_y + 6
    return max(y_left, y_right)


def paint_footer(draw, y):
    draw.text((EDGE, y),
              "All stories as reported on 21 November 2026. "
              "Drawn with PIL; no photos, no invented quotes.",
              font=load(SANS, 13), fill=PALE)


def paint_page():
    sheet = Image.new("RGB", (CANVAS, CANVAS), NEWSROOM)
    draw = ImageDraw.Draw(sheet)
    paint_masthead(draw)
    after_front = paint_front(draw)
    after_quartet = paint_quartet(draw, after_front)
    after_figures = paint_figures(draw, after_quartet + 14)
    paint_briefs(draw, after_figures + 16)
    paint_footer(draw, CANVAS - 20)
    return sheet


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "entry.png")
    sheet = paint_page()
    sheet.save(target, "PNG", optimize=True)
    raw = open(target, "rb").read()
    size = len(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print("painted %s (%d bytes, sha256 %s)" % (target, size, digest))
    if size > 1024 * 1024:
        print("ERROR: entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

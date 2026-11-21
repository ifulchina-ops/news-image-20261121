#!/usr/bin/env python3
"""Twenty-One: Saturday 21 November 2026 in a single front page.

Draws entry.png (1024x1024) with PIL: a broadsheet-style front page that
sums up the day's world news. No photos, no network access, no invented
quotes -- every story below was reported in the 21 November 2026 news
cycle and is sourced in README.md.

Usage:
    python3 main.py            # writes entry.png next to this file
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
PAGE = 1024
MARGIN = 40
PAPER = (247, 242, 231)   # warm newsprint
INK = (18, 18, 18)
SOFT_INK = (64, 64, 64)
RED = (163, 22, 33)       # single accent colour
NAVY = (27, 42, 74)
RULE = (18, 18, 18)
FAINT = (150, 142, 128)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ------------------------------------------------------------- the stories
# (headline, kicker, body) -- bodies are short paraphrases of the reporting.
LEAD = {
    "kicker": "LEAD STORY  \u2022  POLAND",
    "headline": "Russian missiles land in Poland as NATO calls it a grave violation",
    "body": (
        "Two Russian missiles and a suspected drone came down in Poland, which "
        "called it a deliberate provocation. NATO called it a grave violation "
        "of allied airspace."
    ),
}

GRID = [
    {
        "kicker": "THE HAGUE",
        "headline": "ICJ: Myanmar committed genocide",
        "body": (
            "The International Court of Justice ruled Myanmar's security forces "
            "committed state-sponsored genocide against the Rohingya in the "
            "2017 crackdown."
        ),
    },
    {
        "kicker": "SHENZHEN, CHINA",
        "headline": "Trump, Xi and Putin summit ends thin",
        "body": (
            "The first trilateral summit of the three leaders produced pledges "
            "but few concrete results. Trump was due to address Americans on "
            "his return from China."
        ),
    },
    {
        "kicker": "NEW YORK",
        "headline": "Wall Street slumps into correction",
        "body": (
            "US stocks fell sharply on Friday, down about 3.7%, pushing the "
            "S&P 500 and the Dow into correction territory as AI and chip "
            "shares sold off."
        ),
    },
    {
        "kicker": "BRUSSELS",
        "headline": "UK and EU sign new deals",
        "body": (
            "Britain and the EU signed agreements on food trade, carbon markets "
            "and youth mobility for ages 18 to 31 at a Brussels summit."
        ),
    },
]

BRIEF = [
    ("KYIV", "Russia hits Kyiv bridges in a massive attack; at least nine dead. Kryvyi Rih: two killed, 42 hurt."),
    ("ODISHA", "Cyclone Akvan crosses the Odisha coast near Gopalpur with strong winds and heavy rain."),
    ("COPENHAGEN", "Denmark charges two men over a Russian plot to kill a US-Ukrainian rapper; attache expelled."),
    ("RIYADH", "Saudi coalition intercepts three Houthi missiles over Riyadh and strikes Hodeidah."),
    ("BARCELONA", "Erasca pill ERAS-0015 shrank tumours in 44% of pancreatic cancer patients in trial."),
    ("ULAANBAATAR", "Mongolia's parliament accepts President Khurelsukh's resignation, a first."),
]

NUMBERS = [
    ("2", "missiles down in Poland"),
    ("3.7%", "S&P 500's Friday fall"),
    ("44%", "tumour response in trial"),
    ("42", "injured in Kryvyi Rih"),
    ("\u20ac1bn", "EU military aid for Ukraine"),
]


# ------------------------------------------------------------- text helpers
def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit `width` pixels."""
    lines, current = [], ""
    for word in text.split(" "):
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(draw, x, y, text, fnt, fill, width, leading):
    """Draw wrapped text; return the y coordinate just below the block."""
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def double_rule(draw, y, x0=MARGIN, x1=PAGE - MARGIN):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=3)
    draw.line([(x0, y + 5), (x1, y + 5)], fill=RULE, width=1)


def story_card(draw, x, y, width, story, head_size, head_lead, body_size,
               body_lead, kicker_size=17):
    """One kicker + headline + body story inside a column; returns bottom y."""
    draw.text((x, y), story["kicker"], font=font(SANS_BOLD, kicker_size),
              fill=RED)
    y += kicker_size + 8
    y = text_block(draw, x, y, story["headline"], font(SERIF_BOLD, head_size),
                   INK, width, head_lead)
    y += 6
    y = text_block(draw, x, y, story["body"], font(SERIF, body_size),
                   SOFT_INK, width, body_lead)
    return y


# ------------------------------------------------------------- page sections
def draw_masthead(draw):
    title = "TWENTY-ONE"
    fnt = font(SERIF_BOLD, 88)
    w = draw.textlength(title, font=fnt)
    draw.text(((PAGE - w) / 2, 14), title, font=fnt, fill=INK)
    double_rule(draw, 118)
    date = "SATURDAY  \u2022  21  NOVEMBER  2026"
    fnt = font(SANS_BOLD, 27)
    w = draw.textlength(date, font=fnt)
    draw.text(((PAGE - w) / 2, 134), date, font=fnt, fill=RED)
    sub = "THE WORLD IN ONE PAGE \u2014 TEN STORIES THAT DEFINED THE DAY"
    fnt = font(SANS, 18)
    w = draw.textlength(sub, font=fnt)
    draw.text(((PAGE - w) / 2, 168), sub, font=fnt, fill=SOFT_INK)
    double_rule(draw, 194)


def draw_lead(draw):
    y = story_card(draw, MARGIN, 210, PAGE - 2 * MARGIN, LEAD,
                   head_size=40, head_lead=45, body_size=19, body_lead=25,
                   kicker_size=18)
    return y + 18


def draw_grid(draw, top):
    col_w = (PAGE - 2 * MARGIN - 36) // 2
    left = MARGIN
    right = MARGIN + col_w + 36
    y = top
    # row one
    bottom_l = story_card(draw, left, y, col_w, GRID[0],
                          head_size=29, head_lead=33, body_size=15, body_lead=20)
    bottom_r = story_card(draw, right, y, col_w, GRID[1],
                          head_size=29, head_lead=33, body_size=15, body_lead=20)
    y = max(bottom_l, bottom_r) + 10
    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=FAINT, width=1)
    y += 10
    # row two
    bottom_l = story_card(draw, left, y, col_w, GRID[2],
                          head_size=29, head_lead=33, body_size=15, body_lead=20)
    bottom_r = story_card(draw, right, y, col_w, GRID[3],
                          head_size=29, head_lead=33, body_size=15, body_lead=20)
    return max(bottom_l, bottom_r)


def draw_numbers(draw, top):
    band_h = 60
    draw.rectangle([(MARGIN, top), (PAGE - MARGIN, top + band_h)], fill=INK)
    cell_w = (PAGE - 2 * MARGIN) // len(NUMBERS)
    for i, (num, label) in enumerate(NUMBERS):
        cx = MARGIN + i * cell_w
        fnt = font(SANS_BOLD, 24)
        w = draw.textlength(num, font=fnt)
        draw.text((cx + (cell_w - w) / 2, top + 8), num, font=fnt,
                  fill=(255, 255, 255))
        fnt = font(SANS, 12)
        w = draw.textlength(label, font=fnt)
        draw.text((cx + (cell_w - w) / 2, top + 38), label, font=fnt,
                  fill=(200, 200, 200))
        if i:
            draw.line([(cx, top + 12), (cx, top + band_h - 12)],
                      fill=(90, 90, 90), width=1)
    return top + band_h


def draw_brief(draw, top):
    draw.text((MARGIN, top), "THE DAY IN BRIEF",
              font=font(SANS_BOLD, 19), fill=INK)
    draw.line([(MARGIN, top + 28), (PAGE - MARGIN, top + 28)], fill=RULE,
              width=2)
    col_w = (PAGE - 2 * MARGIN - 36) // 2
    left = MARGIN
    right = MARGIN + col_w + 36
    y_l, y_r = top + 38, top + 38
    for i, (place, item) in enumerate(BRIEF):
        x = left if i % 2 == 0 else right
        y = y_l if i % 2 == 0 else y_r
        draw.text((x, y), "\u2022", font=font(SANS_BOLD, 15), fill=RED)
        line = place + ": " + item
        new_y = text_block(draw, x + 16, y, line, font(SERIF, 14),
                           SOFT_INK, col_w - 16, 18)
        if i % 2 == 0:
            y_l = new_y + 6
        else:
            y_r = new_y + 6
    return max(y_l, y_r)


def draw_footer(draw, y):
    note = ("All stories as reported on 21 November 2026. "
            "Drawn with PIL; no photos, no invented quotes.")
    draw.text((MARGIN, y), note, font=font(SANS, 13), fill=FAINT)


# -------------------------------------------------------------------- main
def build_page():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    after_lead = draw_lead(draw)
    after_grid = draw_grid(draw, after_lead)
    after_numbers = draw_numbers(draw, after_grid + 14)
    after_brief = draw_brief(draw, after_numbers + 16)
    draw_footer(draw, PAGE - 20)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", os.path.dirname(
        os.path.abspath(__file__)))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img = build_page()
    img.save(path, "PNG", optimize=True)
    size = os.path.getsize(path)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (path, size, digest))
    if size > 1024 * 1024:
        print("ERROR: entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

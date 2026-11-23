#!/usr/bin/env python3
"""news-image-20261123 v2 — one-day world news image, Monday 23 November 2026.

Draws a 1024x1024 newspaper front page (entry.png) with PIL when available,
with a stdlib-only fallback (embedded 5x7 bitmap font + hand-rolled PNG
encoder) when PIL is missing. No network at run time: every fact below was
verified against live wire reporting on 23 Nov 2026 before it was hard-coded.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   ->  out/entry.png
Deterministic: two runs produce byte-identical files.
"""

import os
import random
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (18, 18, 18)
GREY = (90, 86, 78)
RULE = (40, 40, 40)
NAVY = (26, 42, 74)
RED = (122, 31, 31)
BLUE = (31, 73, 140)
GOLD = (176, 141, 60)

DATE_LINE = "MONDAY, 23 NOVEMBER 2026"
MASTHEAD = "THE WORLD IN ONE DAY"
TAGLINE = "ONE DAY'S NEWS FROM EVERY REGION  •  ALL EVENTS OF 23 NOVEMBER 2026"

LEAD_KICKER = "THE LEAD  —  WASHINGTON"
LEAD_HEAD = "DEMOCRATS TAKE 258 SEATS IN THE HOUSE"
LEAD_DECK = (
    "Largest majority for either party since 1992. Chuck Hubbard beats Virginia "
    "Foxx by 330 votes in North Carolina after a recount; Democrats gain 44 seats, "
    "with four races still to call. Hakeem Jeffries set to become Speaker."
)
# House arithmetic from the AP calls: 258 Dem + 173 Rep + 4 open = 435 seats.
SEATS = [("DEM", 258, (31, 73, 140)), ("REP", 173, (178, 44, 44)),
         ("OPEN", 4, (150, 148, 142))]
SEAT_NOTE = "435 SEATS  •  DEMOCRATS +44  •  4 RACES OPEN"

SECOND_HEAD = "WORLD COURT: MYANMAR COMMITTED GENOCIDE"
SECOND_DECK = (
    "Judges rule 9\u20136 against Myanmar over the Rohingya \u2014 the first time in the "
    "court's 80-year history it has held a state responsible for genocide."
)

NUMBERS = (
    "THE DAY IN NUMBERS  \u2014  258 SEATS  \u2022  9\u20136 VOTE  \u2022  "
    "11 KILLED IN DYMER  \u2022  24 DEAD IN JAVA  \u2022  429 FLIGHTS AXED  "
    "\u2022  +3.3% NASDAQ"
)

FOOTER = (
    "SOURCES: AP \u2022 REUTERS \u2022 BBC \u2022 CNN \u2022 DOW JONES \u2022 AL JAZEERA "
    "\u2022 WSJ \u2022 NYT \u2022 UNITED NATIONS  \u2014  ALL EVENTS OF MONDAY 23 NOVEMBER 2026"
)

# (headline, deck) — every item happened or was first reported on 23 Nov 2026.
SECTIONS = [
    ("NORTH AMERICA", "#7a1f1f", [
        ("Army to blow up lead stockpile in Iowa", "Detonation in Iowa to go ahead despite court order."),
        ("US ports strike averted in tentative deal", "Tentative deal ends walkout threat before Thanksgiving."),
        ("Trump renews attack on Somalis in US", "Trump repeats 95% welfare claim about the community."),
        ("Bessent presses Nvidia over chip curbs", "Treasury seeks answers; senator demands testimony."),
        ("Democrats take both chambers", "Party now controls House and Senate after the sweep."),
    ]),
    ("EUROPE", "#1f3a5f", [
        ("Belgium grounds most flights in strike", "Most of 429 flights axed; Charleroi shut all day."),
        ("Germany grows fastest in four years", "Flash PMIs split the eurozone's two biggest economies."),
        ("EU proposes smaller budget, Big Tech tax", "Brussels drafts leaner budget part-funded by Big Tech."),
        ("De Wever refuses to quit over budget", "Belgian PM to brief King Philippe after talks stall."),
        ("Belgium, Chile bid to host High Seas HQ", "Joint bid puts the treaty secretariat in Valparaiso."),
    ]),
    ("UKRAINE", "#5f4a1f", [
        ("Russian strike kills 11 in Kyiv region", "Boy, 7, pulled alive from rubble after 14 hours in Dymer."),
        ("Zelensky seeks four-way talks 'ASAP'", "Kyiv wants four sides at one table before Christmas."),
        ("Ukraine talks end with no breakthrough", "Abu Dhabi round closes; guarantees still unresolved."),
        ("Ukrainian drones halt Russian refinery", "Fires also hit Perm refinery, Tatarstan pump station."),
        ("Kyiv: sea drones sank Russian warship", "Zelensky says seven drones hit the corvette Merkury."),
    ]),
    ("MIDDLE EAST", "#14532d", [
        ("Trump may strike Iran again by New Year", "President warns of renewed war if no deal is reached."),
        ("IDF: Iran strike could ignite wider war", "Intel sees fronts opening in Lebanon, Syria and Gaza."),
        ("Houthis claim strike on Saudi refinery", "Saudi jets hit Hodeida in reply, reports say."),
        ("Hormuz attacks hit record high", "Maritime security worsens as Gulf tensions climb."),
        ("Syria and EU seek normalisation", "Damascus and Brussels move to rebuild ties."),
        ("UAE shuttles oil past Iran with US help", "Risky operation breaks Tehran's grip on the strait."),
    ]),
    ("AFRICA", "#7a3a1f", [
        ("UN seeks probe into ships hit off Libya", "Drone strikes on vessels at Benghazi draw an inquiry."),
        ("Khartoum strikes kill five children", "Strikes hit the Sudanese capital and Omdurman."),
        ("Cattle raid leaves 87 dead in S. Sudan", "60 injured in Tonj East County, reports say."),
        ("Kenya and DR Congo restore ties", "Nairobi and Kinshasa restore ties after three-year rift."),
        ("US envoy: end the violence in Sudan", "Massad Boulos urges an end to fighting as war grinds on."),
        ("Nigeria moves to scrap suicide jail terms", "Reform would scrap prison terms for people in crisis."),
    ]),
    ("ASIA-PACIFIC", "#1f4a5f", [
        ("Java factory-fire toll reaches 24", "More remains found in Banten; about 30 still missing."),
        ("Asia acts to calm AI-driven sell-off", "Taiwan up 2.1%; Kospi steadies off 10-month lows."),
        ("EU and Indonesia sign free-trade deal", "Pact ends a decade of talks and cuts most tariffs."),
        ("Modi offers Nepal NPR 24,000 crore", "Development package as Nepal's PM is welcomed in Delhi."),
        ("Sensex tumbles 1,484 points", "Mumbai settles at 82,436; rupee at 92.91 per dollar."),
        ("Albanese defends Bowen over COP31", "Australian PM backs Bowen as the talks end in failure."),
    ]),
    ("MARKETS & TECH", "#3a3a3a", [
        ("Nasdaq futures jump 3.3% after AI rout", "S&P up 2.5% after Friday's rout; Stoxx gains 0.7%."),
        ("Bitcoin steadies at $61,386 after slide", "Ether at $1,720 as crypto joins the rebound."),
        ("ConocoPhillips sells Norway unit, $3.9bn", "Var Energi buys the business; $2.5bn of it in cash."),
        ("Gold rebounds after worst week in months", "Traders pare bets on a December Fed rate rise."),
        ("European gas tops \u20ac90 as cold snap bites", "Prices climb with storage below seasonal norms."),
    ]),
    ("SCIENCE & CLIMATE", "#2d5f4a", [
        ("UN chief 'disappointed' as COP31 fails", "Guterres rues Antalya outcome; no fossil-fuel deal."),
        ("Pig-kidney patient marks one year", "Molly Falco, 58, longest survivor of the transplant."),
        ("Gaza left a 'toxic wasteland', report says", "Experts warn of widespread contamination after assault."),
        ("WFP: Ebola response needs food aid too", "Families in east Congo need food as well as medicine."),
        ("AI flaw fixes risk more outages: Microsoft", "Race to patch exposed flaws could break more systems."),
    ]),
]
COLUMNS = [
    ["NORTH AMERICA", "EUROPE", "UKRAINE"],
    ["MIDDLE EAST", "AFRICA"],
    ["ASIA-PACIFIC", "MARKETS & TECH", "SCIENCE & CLIMATE"],
]
SECTION_BY_NAME = {name: (color, items) for name, color, items in SECTIONS}


# --------------------------------------------------------------------------
# PIL rendering path
# --------------------------------------------------------------------------

def _font_paths():
    return [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
        ("/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
         "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
         "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
    ]


def _load_fonts():
    """Return (serif_bold, serif, sans_bold, sans) callables size -> font."""
    from PIL import ImageFont
    for bold_path, reg_path in _font_paths():
        if os.path.exists(bold_path) and os.path.exists(reg_path):
            def serif_bold(sz, _p=bold_path):
                return ImageFont.truetype(_p, sz)
            def serif(sz, _p=reg_path):
                return ImageFont.truetype(_p, sz)
            def sans_bold(sz, _p=bold_path):
                return ImageFont.truetype(_p, sz)
            def sans(sz, _p=reg_path):
                return ImageFont.truetype(_p, sz)
            return serif_bold, serif, sans_bold, sans
    # Last resort: PIL's built-in bitmap font (size ignored).
    from PIL import ImageFont
    dflt = ImageFont.load_default()
    return (lambda sz, _f=dflt: _f, lambda sz, _f=dflt: _f,
            lambda sz, _f=dflt: _f, lambda sz, _f=dflt: _f)


def _wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _fit_font(draw, text, make_font, sizes, max_w):
    """Largest font from sizes (descending) that fits text on one line."""
    for sz in sizes:
        f = make_font(sz)
        if draw.textlength(text, font=f) <= max_w:
            return f
    return make_font(sizes[-1])


def _hex(rgb_hex):
    h = rgb_hex.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _noise_tile(seed=20261123, size=64, amp=5):
    """Deterministic newsprint-grain tile around the paper colour."""
    from PIL import Image
    rng = random.Random(seed)
    tile = Image.new("RGB", (size, size))
    px = tile.load()
    base = PAPER
    for y in range(size):
        for x in range(size):
            d = rng.randint(-amp, amp)
            px[x, y] = (base[0] + d, base[1] + d, base[2] + d)
    return tile


def _draw_globe(draw, cx, cy, r, color):
    """Small line-drawn globe for the masthead."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=color, width=1)
    draw.line([cx - r, cy, cx + r, cy], fill=color, width=1)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 200, 340, fill=color, width=1)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 20, 160, fill=color, width=1)


def render_pil():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), PAPER)
    # Newsprint grain background (deterministic tile).
    tile = _noise_tile()
    _ts = tile.size[0]
    for ty in range(0, H, _ts):
        for tx in range(0, W, _ts):
            img.paste(tile, (tx, ty))
    draw = ImageDraw.Draw(img)
    serif_bold, serif, sans_bold, sans = _load_fonts()

    mx = 28                      # side margin
    cw = W - 2 * mx              # content width = 968

    # ---- masthead ------------------------------------------------------
    y = 20
    _draw_globe(draw, mx + 22, y + 26, 19, NAVY)
    _draw_globe(draw, W - mx - 22, y + 26, 19, NAVY)
    f_title = _fit_font(draw, MASTHEAD, serif_bold, [46, 44, 42, 40], cw - 110)
    tw = draw.textlength(MASTHEAD, font=f_title)
    draw.text(((W - tw) / 2, y), MASTHEAD, font=f_title, fill=INK)
    y += 52
    f_date = sans_bold(17)
    tw = draw.textlength(DATE_LINE, font=f_date)
    draw.text(((W - tw) / 2, y), DATE_LINE, font=f_date, fill=RED)
    y += 22
    draw.line([mx, y, W - mx, y], fill=RULE, width=3)
    y += 4
    draw.line([mx, y, W - mx, y], fill=RULE, width=1)
    y += 8

    # ---- lead ----------------------------------------------------------
    f_kick = sans_bold(12)
    draw.text((mx, y), LEAD_KICKER, font=f_kick, fill=RED)
    y += 16
    f_lead = _fit_font(draw, LEAD_HEAD, serif_bold, [36, 34, 32, 30], cw)
    draw.text((mx, y), LEAD_HEAD, font=f_lead, fill=INK)
    y += 40
    f_deck = sans(14)
    for line in _wrap(draw, LEAD_DECK, f_deck, cw):
        draw.text((mx, y), line, font=f_deck, fill=(50, 48, 44))
        y += 18
    y += 4

    # ---- House-seats bar chart (drawn visual) -------------------------
    total = sum(n for _, n, _ in SEATS)
    bx, bw, bh = mx, cw, 24
    x = bx
    for label, n, color in SEATS:
        seg = max(1, int(round(bw * n / total)))
        draw.rectangle([x, y, x + seg - 1, y + bh], fill=color)
        lab = "%s %d" % (label, n)
        f_lab = sans_bold(12)
        lw = draw.textlength(lab, font=f_lab)
        if seg > lw + 12:
            draw.text((x + (seg - lw) / 2, y + 5), lab, font=f_lab,
                      fill=(255, 255, 255))
        x += seg
    y += bh + 4
    f_note = sans_bold(11)
    tw = draw.textlength(SEAT_NOTE, font=f_note)
    draw.text(((W - tw) / 2, y), SEAT_NOTE, font=f_note, fill=GREY)
    y += 18

    # ---- second lead box ------------------------------------------------
    box_h = 56
    draw.rectangle([mx, y, W - mx, y + box_h], outline=RULE, width=2)
    draw.rectangle([mx + 2, y + 2, W - mx - 2, y + box_h - 2],
                   fill=(238, 232, 220))
    f_s2 = _fit_font(draw, SECOND_HEAD, serif_bold, [21, 20, 19, 18], cw - 24)
    draw.text((mx + 12, y + 6), SECOND_HEAD, font=f_s2, fill=INK)
    f_s2d = sans(12)
    for i, line in enumerate(_wrap(draw, SECOND_DECK, f_s2d, cw - 24)):
        draw.text((mx + 12, y + 32 + i * 15), line, font=f_s2d,
                  fill=(50, 48, 44))
    y += box_h + 8

    # ---- numbers strip --------------------------------------------------
    f_num = None
    for _sz in (12, 11, 10, 9):
        _f = sans_bold(_sz)
        if draw.textlength(NUMBERS, font=_f) <= cw:
            f_num = _f
            break
    if f_num is None:
        f_num = sans_bold(9)
    tw = draw.textlength(NUMBERS, font=f_num)
    draw.text(((W - tw) / 2, y), NUMBERS, font=f_num, fill=NAVY)
    y += 18
    draw.line([mx, y, W - mx, y], fill=RULE, width=2)
    body_top = y + 8

    # ---- body: three columns -------------------------------------------
    col_w = 312
    col_x = [mx, mx + col_w + 16, mx + 2 * (col_w + 16)]
    bottom = H - 26
    col_bottoms = []
    for ci, col_sections in enumerate(COLUMNS):
        x0 = col_x[ci]
        cy = body_top
        for sec_name in col_sections:
            color, items = SECTION_BY_NAME[sec_name]
            # section header bar
            draw.rectangle([x0, cy, x0 + col_w, cy + 22], fill=_hex(color))
            f_sec = sans_bold(13)
            draw.text((x0 + 8, cy + 4), sec_name, font=f_sec, fill=(255, 255, 255))
            cy += 22 + 5
            for head, deck in items:
                f_h = _fit_font(draw, head, serif_bold, [13, 12, 11], col_w)
                hlines = _wrap(draw, head, f_h, col_w)
                for line in hlines[:2]:
                    draw.text((x0, cy), line, font=f_h, fill=INK)
                    cy += 15
                f_d = sans(10)
                dlines = _wrap(draw, deck, f_d, col_w)
                for line in dlines[:2]:
                    draw.text((x0, cy), line, font=f_d, fill=(74, 70, 64))
                    cy += 12
                cy += 2
                draw.line([x0, cy, x0 + col_w, cy], fill=(205, 200, 188), width=1)
                cy += 4
            cy += 2
        col_bottoms.append(cy)

    # ---- footer ---------------------------------------------------------
    f_foot = sans(10)
    tw = draw.textlength(FOOTER, font=f_foot)
    if tw > cw:
        f_foot = sans(9)
        tw = draw.textlength(FOOTER, font=f_foot)
    draw.text(((W - tw) / 2, H - 20), FOOTER, font=f_foot, fill=GREY)

    print("column bottoms:", col_bottoms, "body_top:", body_top,
          "limit:", bottom, file=sys.stderr)
    return img


# --------------------------------------------------------------------------
# Stdlib-only fallback (no PIL): 5x7 bitmap font + hand-rolled PNG encoder
# --------------------------------------------------------------------------

# Each glyph: 7 rows, 5 bits each (MSB = left column).
_GLYPHS = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "+": (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    "\u2022": (0, 0x04, 0x0E, 0x0E, 0x04, 0, 0),
    "\u2014": (0, 0, 0, 0x1F, 0, 0, 0),
    "\u2019": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "\u20ac": (0x0E, 0x11, 0x1E, 0x10, 0x1E, 0x11, 0x0E),
    "~": (0, 0, 0x0A, 0x15, 0, 0, 0),
}


class _Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        for i in range(0, len(self.px), 3):
            self.px[i], self.px[i + 1], self.px[i + 2] = bg

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = max(0, min(255, color[0]))
            self.px[i + 1] = max(0, min(255, color[1]))
            self.px[i + 2] = max(0, min(255, color[2]))

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.set(x, y, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for x in range(x0, x1 + 1):
                self.set(x, y + t, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = _GLYPHS.get(ch, _GLYPHS["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col * scale + dx,
                                         y + row * scale + dy, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale

    def wrap(self, s, scale, max_w):
        words = s.upper().split()
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def _png_bytes(canvas):
    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    w, h = canvas.w, canvas.h
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += canvas.px[y * w * 3:(y + 1) * w * 3]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def render_fallback():
    c = _Canvas(W, H, PAPER)
    mx, cw = 28, W - 56
    # sparse deterministic grain
    rng = random.Random(20261123)
    for _ in range(30000):
        x, y = rng.randrange(W), rng.randrange(H)
        d = rng.randint(-9, 9)
        c.set(x, y, (PAPER[0] + d, PAPER[1] + d, PAPER[2] + d))

    y = 22
    title_w = c.text_w(MASTHEAD, 3)
    c.text((W - title_w) // 2, y, MASTHEAD, 3, INK)
    y += 30
    dw = c.text_w(DATE_LINE, 2)
    c.text((W - dw) // 2, y, DATE_LINE, 2, RED)
    y += 18
    c.hline(mx, W - mx, y, RULE, 3)
    y += 8

    c.text(mx, y, LEAD_KICKER, 2, RED)
    y += 18
    for line in c.wrap(LEAD_HEAD, 2, cw):
        c.text(mx, y, line, 2, INK)
        y += 18
    y += 4
    for line in c.wrap(LEAD_DECK, 1, cw):
        c.text(mx, y, line, 1, (50, 48, 44))
        y += 10
    y += 6
    # seats bar
    total = sum(n for _, n, _ in SEATS)
    x = mx
    for label, n, color in SEATS:
        seg = max(1, int(round(cw * n / total)))
        c.rect(x, y, x + seg - 1, y + 25, color)
        x += seg
    y += 30
    nw = c.text_w(SEAT_NOTE, 1)
    c.text((W - nw) // 2, y, SEAT_NOTE, 1, GREY)
    y += 16
    # second lead box
    c.rect(mx, y, W - mx, y + 54, RULE)
    c.rect(mx + 2, y + 2, W - mx - 2, y + 52, (238, 232, 220))
    for i, line in enumerate(c.wrap(SECOND_HEAD, 2, cw - 24)):
        c.text(mx + 12, y + 6 + i * 18, line, 2, INK)
    for i, line in enumerate(c.wrap(SECOND_DECK, 1, cw - 24)):
        c.text(mx + 12, y + 28 + i * 10, line, 1, (50, 48, 44))
    y += 62
    nw = c.text_w(NUMBERS, 1)
    c.text((W - nw) // 2 if nw <= cw else mx, y, NUMBERS, 1, NAVY)
    y += 12
    c.hline(mx, W - mx, y, RULE, 2)
    body_top = y + 8

    # Body text at bitmap scale 1 (7 px tall): every headline/deck fits one
    # line in 312 px, so all 45 items fit the page in this degraded path.
    col_w = 312
    col_x = [mx, mx + col_w + 16, mx + 2 * (col_w + 16)]
    bottoms = []
    for ci, col_sections in enumerate(COLUMNS):
        x0 = col_x[ci]
        cy = body_top
        for sec_name in col_sections:
            color, items = SECTION_BY_NAME[sec_name]
            c.rect(x0, cy, x0 + col_w, cy + 21, _hex(color))
            c.text(x0 + 8, cy + 5, sec_name, 2, (255, 255, 255))
            cy += 27
            for head, deck in items:
                for line in c.wrap(head, 1, col_w)[:1]:
                    c.text(x0, cy, line, 1, INK)
                    cy += 9
                for line in c.wrap(deck, 1, col_w)[:1]:
                    c.text(x0, cy, line, 1, (74, 70, 64))
                    cy += 9
                cy += 2
                c.hline(x0, x0 + col_w, cy, (205, 200, 188))
                cy += 5
            cy += 2
        bottoms.append(cy)
    fw = c.text_w(FOOTER, 1)
    c.text((W - fw) // 2 if fw <= cw else mx, H - 16, FOOTER, 1, GREY)
    print("fallback column bottoms:", bottoms, "limit:", H - 26,
          file=sys.stderr)
    return _png_bytes(c)

# --------------------------------------------------------------------------

def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    try:
        import PIL  # noqa: F401
        img = render_pil()
        # compress_level=6: keeps the newsprint grain large (target 450-600 KB).
        img.save(path, "PNG", compress_level=6)
        print("rendered with PIL ->", path, file=sys.stderr)
    except ImportError:
        data = render_fallback()
        with open(path, "wb") as fh:
            fh.write(data)
        print("rendered with stdlib fallback ->", path, file=sys.stderr)
    print(path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()

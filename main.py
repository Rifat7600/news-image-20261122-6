#!/usr/bin/env python3
"""WORLD NEWS TONIGHT - 22 November 2026.

A TV news broadcast screen summing up 22 November 2026:
  - COP31 climate talks collapse in Antalya (main story)
  - Democrats win biggest US House majority since 1992 (258 seats)
  - Tankers ablaze at Hormuz
  - Russian warship hit off Libya
  - Ticker: Sudan drones, El Chapo Isidro captured, Brazil storm,
    France protests (6th weekend).

Pure Python 3.13 standard library. Draws a PNG with a zlib-based
writer and a hand-built 5x7 bitmap font. No network, no fonts from
disk, no randomness, no time: the output is byte-identical every run.
"""
import os
import struct
import zlib

W, H = 1024, 768

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph: 7 rows of 5 characters ('#' = on).
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}

BULLET = (".....", ".....", ".###.", ".###.", ".###.", ".....", ".....")

# ---------------------------------------------------------------- colours
NAVY = (10, 26, 47)
PANEL = (16, 35, 60)
PANEL2 = (22, 48, 80)
RED = (210, 31, 43)
DARKRED = (163, 22, 33)
GOLD = (242, 183, 5)
WHITE = (255, 255, 255)
LIGHT = (199, 210, 222)
GREY = (148, 163, 178)
SKY = (46, 127, 194)
LAND = (63, 163, 77)
SEA = (18, 60, 110)
WOOD = (122, 84, 48)
FLAME = (255, 138, 0)
FLAME2 = (255, 205, 0)
SMOKE = (120, 130, 140)
HULL = (90, 100, 112)
DOME = (232, 236, 240)

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def fill_rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def rect(x, y, w, h, c, t=1):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def hline(x0, x1, y, c, t=1):
    for yy in range(y, y + t):
        for xx in range(x0, x1 + 1):
            px(xx, yy, c)


def vline(x, y0, y1, c, t=1):
    for xx in range(x, x + t):
        for yy in range(y0, y1 + 1):
            px(xx, yy, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            for b in range(t):
                px(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def fill_ellipse(cx, cy, rx, ry, c):
    for yy in range(cy - ry, cy + ry + 1):
        for xx in range(cx - rx, cx + rx + 1):
            if ((xx - cx) * (xx - cx)) * ry * ry + ((yy - cy) * (yy - cy)) * rx * rx <= rx * rx * ry * ry:
                px(xx, yy, c)


def triangle(x0, y0, x1, y1, x2, y2, c):
    # filled triangle via scanlines
    pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    for y in range(ay, cy + 1):
        if y < by:
            xa = ax + (bx - ax) * (y - ay) / max(1, by - ay)
            xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
        else:
            xa = bx + (cx - bx) * (y - by) / max(1, cy - by)
            xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
        for x in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
            px(x, y, c)


# ---------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_glyph(x, y, ch, scale, c):
    g = FONT.get(ch)
    if g is None:
        return
    for r in range(7):
        row = g[r]
        for col in range(5):
            if row[col] == "#":
                fill_rect(x + col * scale, y + r * scale, scale, scale, c)


def draw_text(x, y, s, scale, c):
    for ch in s:
        if ch == "\u2022":
            g = BULLET
            for r in range(7):
                for col in range(5):
                    if g[r][col] == "#":
                        fill_rect(x + col * scale, y + r * scale, scale, scale, c)
        else:
            draw_glyph(x, y, ch, scale, c)
        x += 6 * scale
    return x


def wrap_lines(s, scale, max_w):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, scale, c, max_w, line_gap=4):
    for ln in wrap_lines(s, scale, max_w):
        draw_text(x, y, ln, scale, c)
        y += 7 * scale + line_gap
    return y


# ---------------------------------------------------------------- top bar
fill_rect(0, 0, W, H, NAVY)

# masthead band
fill_rect(0, 0, W, 72, PANEL)
fill_rect(0, 70, W, 3, RED)

# LIVE bug
fill_rect(16, 14, 104, 44, RED)
draw_text(32, 26, "LIVE", 3, WHITE)

# masthead title
draw_text(136, 20, "WORLD NEWS TONIGHT", 4, WHITE)

# date box (top right) - big and unmistakable
fill_rect(612, 10, 396, 52, GOLD)
draw_text(628, 22, "22 NOVEMBER 2026", 4, NAVY)

# ---------------------------------------------------------------- main story (left)
# panel background
fill_rect(0, 73, 672, 567, PANEL2)
# tag row
fill_rect(24, 88, 120, 34, RED)
draw_text(36, 96, "COP31", 3, WHITE)
draw_text(160, 96, "ANTALYA, TURKEY", 3, LIGHT)
draw_text(452, 96, "NO DEAL", 3, GOLD)

# --- cracked globe (empty summit: the world, broken) ---
GX, GY, GR = 336, 258, 102
fill_circle(GX, GY, GR, SKY)
# land masses
fill_ellipse(GX - 38, GY - 34, 44, 26, LAND)
fill_ellipse(GX + 42, GY - 18, 36, 30, LAND)
fill_ellipse(GX - 12, GY + 44, 48, 24, LAND)
fill_ellipse(GX + 58, GY + 52, 22, 14, LAND)
fill_ellipse(GX - 66, GY + 18, 18, 30, LAND)
# polar cap
fill_ellipse(GX, GY - 92, 52, 16, WHITE)
# cracks across the globe
line(GX - 78, GY - 62, GX - 30, GY - 18, NAVY, 4)
line(GX - 30, GY - 18, GX - 52, GY + 28, NAVY, 4)
line(GX - 52, GY + 28, GX - 8, GY + 66, NAVY, 4)
line(GX + 20, GY - 88, GX + 44, GY - 40, NAVY, 4)
line(GX + 44, GY - 40, GX + 18, GY + 6, NAVY, 4)
line(GX + 18, GY + 6, GX + 62, GY + 44, NAVY, 4)
line(GX + 62, GY + 44, GX + 40, GY + 84, NAVY, 4)
# highlight
fill_ellipse(GX - 52, GY - 62, 26, 12, (120, 185, 235))

# --- empty conference hall: rows of empty desks, nobody there ---
for row in range(2):
    y0 = 388 + row * 26
    for i in range(6):
        x0 = 66 + i * 100
        # desk
        fill_rect(x0, y0, 84, 14, WOOD)
        # empty chair back
        fill_rect(x0 + 26, y0 + 15, 32, 8, (70, 60, 50))
        # name plate, blank
        fill_rect(x0 + 30, y0 + 4, 24, 6, LIGHT)

# --- headline ---
draw_text(66, 452, "COP31 COLLAPSES", 6, WHITE)
draw_text(48, 500, "NO CLIMATE DEAL", 6, GOLD)
draw_text(66, 556, "TALKS END WITH NO DEAL IN ANTALYA", 3, LIGHT)
draw_text(66, 588, "LONGEST COP ON RECORD", 3, LIGHT)

# ---------------------------------------------------------------- side rail (right)
fill_rect(684, 73, 340, 567, PANEL)
fill_rect(684, 73, 340, 40, RED)
draw_text(700, 82, "MORE TOP STORIES", 3, WHITE)

# --- story 1: Democrats / capitol dome ---
SY = 120
fill_rect(700, SY, 308, 64, SEA)
# capitol dome
fill_ellipse(854, SY + 42, 46, 30, DOME)
fill_rect(808, SY + 42, 92, 22, DOME)
for i in range(5):
    fill_rect(814 + i * 18, SY + 42, 8, 22, PANEL2)
fill_rect(848, SY + 6, 12, 10, DOME)
_s1 = wrap_lines("DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992 (258 SEATS)", 3, 308)
draw_text(700, SY + 72, _s1[0], 3, WHITE)
for _j, _ln in enumerate(_s1[1:]):
    draw_text(700, SY + 72 + (_j + 1) * 25, _ln, 3, LIGHT)

# --- story 2: tankers ablaze at Hormuz ---
SY = 300
fill_rect(700, SY, 308, 64, SEA)
# tanker hull
fill_rect(724, SY + 36, 220, 16, HULL)
fill_rect(724, SY + 24, 40, 12, HULL)
# cargo
fill_rect(780, SY + 22, 60, 14, (160, 90, 40))
fill_rect(850, SY + 22, 60, 14, (140, 70, 60))
# flames
triangle(760, SY + 24, 776, SY + 2, 792, SY + 24, FLAME)
triangle(830, SY + 22, 846, SY + 4, 862, SY + 22, FLAME2)
triangle(900, SY + 24, 914, SY + 8, 928, SY + 24, FLAME)
# sea
fill_rect(700, SY + 52, 308, 12, (10, 40, 80))
draw_text(700, SY + 72, "TANKERS ABLAZE", 3, WHITE)
draw_text(700, SY + 97, "AT HORMUZ", 3, LIGHT)

# --- story 3: Russian warship hit off Libya ---
SY = 474
fill_rect(700, SY, 308, 64, SEA)
# warship hull
fill_rect(730, SY + 38, 200, 16, HULL)
triangle(730, SY + 38, 714, SY + 38, 730, SY + 52, HULL)
fill_rect(800, SY + 20, 14, 18, HULL)
fill_rect(830, SY + 26, 40, 8, HULL)
# smoke plume
fill_circle(838, SY + 10, 11, SMOKE)
fill_circle(852, SY + 2, 8, SMOKE)
fill_circle(820, SY + 6, 7, SMOKE)
# fire
triangle(806, SY + 20, 816, SY + 6, 826, SY + 20, FLAME)
# sea
fill_rect(700, SY + 54, 308, 10, (10, 40, 80))
draw_text(700, SY + 72, "RUSSIAN WARSHIP", 3, WHITE)
draw_text(700, SY + 97, "HIT OFF LIBYA", 3, LIGHT)

# ---------------------------------------------------------------- ticker
fill_rect(0, 640, W, 72, DARKRED)
fill_rect(0, 640, W, 3, GOLD)
draw_text(24, 656, "SUDAN DRONES KILL 4, DAMAGE UN BUILDING \u2022 'EL CHAPO ISIDRO' CAPTURED, 11 DEAD", 2, WHITE)
draw_text(24, 684, "DEADLY STORM KILLS 4 IN BRAZIL \u2022 FRANCE PROTESTS, 6TH WEEKEND", 2, WHITE)

# ---------------------------------------------------------------- bottom strip: date again, big
fill_rect(0, 712, W, 56, PANEL)
draw_text(272, 724, "22 NOVEMBER 2026", 5, GOLD)
draw_text(24, 730, "WNT", 3, LIGHT)
draw_text(920, 730, "LIVE", 3, RED)

# ---------------------------------------------------------------- write PNG
out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, "entry.png")

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += buf[y * W * 3:(y + 1) * W * 3]
comp = zlib.compress(bytes(raw), 6)


def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return c


png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
png += chunk(b"IDAT", comp)
png += chunk(b"IEND", b"")

with open(path, "wb") as f:
    f.write(png)
print("wrote", path, len(png), "bytes", W, "x", H)

"""Breadboard build diagram for the starter kit (400-point breadboard, ESP32 beside it).
python gen_breadboard.py  ->  starter-kit-breadboard.svg
Layout: flow sensors above the breadboard, ESP32 below it, so no wires cross.
"""
import math
import sys
from pathlib import Path

ONE = "--one" in sys.argv   # single flow sensor build

W, H = 1500, 1420
o = []
RED, BLACK, YEL, BLUE, GREEN, GREY = "#d32f2f", "#222222", "#e0a800", "#0a66c2", "#2e7d32", "#666666"

X0, PITCH = 320, 28
def rx(r): return X0 + (r - 1) * PITCH
RAIL_P, RAIL_N = 330, 358                      # top + and - rails
COLS = {c: 410 + i * 28 for i, c in enumerate("abcde")}
COLS.update({c: 598 + i * 28 for i, c in enumerate("fghij")})
BRAIL_N, BRAIL_P = 760, 788
ESP_TOP = 930

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def text(x, y, s, size=15, anchor="start", weight="normal", color="#191919"):
    o.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{esc(s)}</text>')
def rect(x, y, w, h, fill, stroke="none", sw=1):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def hole(x, y):
    o.append(f'<rect x="{x-4}" y="{y-4}" width="8" height="8" fill="#bdbdbd"/>')
def jumper(x1, y1, x2, y2, color, bend=0):
    mx, my = (x1 + x2) / 2 + bend, (y1 + y2) / 2
    o.append(f'<path d="M{x1} {y1} Q{mx} {my} {x2} {y2}" fill="none" stroke="{color}" stroke-width="6" stroke-linecap="round" opacity="0.92"/>')
    for x, y in ((x1, y1), (x2, y2)):
        o.append(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
def resistor(x1, y1, x2, y2, label, bands):
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#9e9e9e" stroke-width="3"/>')
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    vertical = abs(x2 - x1) < 5
    length = 40 if vertical else 64
    o.append(f'<g transform="translate({cx} {cy}) rotate({ang})">')
    o.append(f'<rect x="{-length/2}" y="-10" width="{length}" height="20" fill="#e8d3a3" stroke="#8a6d1f" stroke-width="1.5"/>')
    for i, c in enumerate(bands):
        o.append(f'<rect x="{-length/2 + 6 + i * (length - 12) / 3}" y="-10" width="5" height="20" fill="{c}"/>')
    o.append('</g>')
    for x, y in ((x1, y1), (x2, y2)):
        o.append(f'<rect x="{x-5}" y="{y-5}" width="10" height="10" fill="#555"/>')
    if vertical:
        text(cx + 16, cy + 5, label, 14, weight="bold")
    else:
        text(cx, cy - 16, label, 14, "middle", "bold")

o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">')
rect(0, 0, W, H, "#ffffff")
text(40, 44, "SROT starter kit: breadboard build" + (" (1 flow sensor)" if ONE else ""), 28, weight="bold")
text(40, 72, "The ESP32 sits below the breadboard (too wide to plug in). Connect its pins with male-to-female jumpers.", 16, color=GREY)

# ---------------- flow sensors (above the breadboard)
def sensor(x, y, name, sub):
    rect(x, y, 240, 110, "#fafafa", "#191919", 2)
    text(x + 120, y + 34, name, 17, "middle", "bold")
    text(x + 120, y + 58, sub, 14, "middle", color=GREY)
    text(x + 120, y + 80, "YF-S201", 13, "middle", color=GREY)
sensor(40, 110, "Flow sensor 1 (IN)", "before the leak tap")
if not ONE:
    sensor(1220, 110, "Flow sensor 2 (OUT)", "after the leak tap")

# ---------------- breadboard
rect(290, 300, 870, 570, "#f5f5f0", "#d0d0c8", 2)
rect(300, 318, 850, 52, "#ffffff")
o.append(f'<line x1="300" y1="{RAIL_P}" x2="1150" y2="{RAIL_P}" stroke="{RED}" stroke-width="1.5"/>')
o.append(f'<line x1="300" y1="{RAIL_N}" x2="1150" y2="{RAIL_N}" stroke="{BLUE}" stroke-width="1.5"/>')
text(298, RAIL_P + 5, "+", 18, "end", "bold", RED)
text(298, RAIL_N + 6, "−", 20, "end", "bold", BLUE)
text(1162, RAIL_P + 5, "+ rail = 5V", 14, weight="bold", color=RED)
text(1162, RAIL_N + 5, "− rail = GND", 14, weight="bold", color=BLUE)
rect(300, 566, 850, 18, "#e6e6df")
for c, y in COLS.items():
    text(306, y + 5, c, 12, "end", color=GREY)
for r in range(1, 31):
    x = rx(r)
    for y in (RAIL_P, RAIL_N, BRAIL_N, BRAIL_P):
        hole(x, y)
    for y in COLS.values():
        hole(x, y)
    if r in ((1, 3, 5, 10, 15, 20, 25, 30) if ONE else (1, 3, 5, 10, 13, 15, 20, 25, 30)):
        key = r in ((3, 10) if ONE else (3, 10, 13, 20))
        text(x, 832, str(r), 13 if key else 12, "middle", "bold" if key else "normal", "#191919" if key else GREY)
text(305, 856, "row numbers", 12, color=GREY)
text(1162, 470, "In each row,", 13, color=GREY)
text(1162, 488, "holes a–e are", 13, color=GREY)
text(1162, 506, "connected.", 13, color=GREY)

# ---------------- resistors
TEN, TWENTY = ["#795548", "#222", "#ff9800"], ["#d32f2f", "#222", "#ff9800"]
resistor(rx(3), COLS["c"], rx(10), COLS["c"], "10k", TEN)
if not ONE:
    resistor(rx(13), COLS["c"], rx(20), COLS["c"], "10k", TEN)
resistor(rx(10), COLS["a"], rx(10), RAIL_N, "20k", TWENTY)
if not ONE:
    resistor(rx(13), COLS["a"], rx(13), RAIL_N, "20k", TWENTY)

# ---------------- sensor wires
jumper(130, 220, rx(1), RAIL_P, RED, -40)
jumper(160, 220, rx(2), RAIL_N, BLACK, -20)
jumper(190, 220, rx(3), COLS["b"], YEL, 0)
if not ONE:
    jumper(1280, 220, rx(28), RAIL_P, RED, 0)
    jumper(1310, 220, rx(29), RAIL_N, BLACK, 0)
    jumper(1340, 220, rx(20), COLS["b"], YEL, 120)
for x, lbl in ((130, "red"), (160, "black"), (190, "yellow")):
    pass

# ---------------- ESP32 (below; USB on the left; its pin header along the top edge)
ESP_PINS = ["5V", "CMD", "D3", "D2", "13", "GND", "12", "14", "27", "26", "25", "33", "32", "35", "34", "VN", "VP", "EN", "3V3"]
px = {p: 330 + i * 34 for i, p in enumerate(ESP_PINS)}
rect(300, ESP_TOP, 700, 130, "#1f3b57")
rect(260, ESP_TOP + 45, 40, 40, "#9e9e9e")
text(250, ESP_TOP + 72, "USB", 13, "end", color=GREY)
text(650, ESP_TOP + 95, "ESP32 DevKitC (38-pin), lying flat, USB port on the left", 17, "middle", "bold", "#ffffff")
text(650, ESP_TOP + 117, "These pins are on the edge nearest the breadboard", 13, "middle", color="#c8d6e5")
USED = {"27": GREEN, "GND": BLACK, "5V": RED} if ONE else {"27": GREEN, "26": BLUE, "GND": BLACK, "5V": RED}
for p, x in px.items():
    c = USED.get(p)
    rect(x - 6, ESP_TOP - 4, 12, 12, c if c else "#9e9e9e", "#ffffff" if c else "none", 2 if c else 0)
    if c:
        rect(x - 19, ESP_TOP + 16, 38, 20, c, "#ffffff", 1.5)
        text(x, ESP_TOP + 31, p, 13, "middle", "bold", "#ffffff")
    else:
        text(x, ESP_TOP + 30, p, 11, "middle", color="#8fa3b8")
text(1010, ESP_TOP + 40, "← power bank plugs", 14, color=GREY)
text(1010, ESP_TOP + 58, "into the USB port", 14, color=GREY)

# ---------------- ESP32 jumpers
jumper(px["5V"], ESP_TOP, rx(6), RAIL_P, RED, -260)
jumper(px["GND"], ESP_TOP, rx(7), RAIL_N, BLACK, -230)
jumper(px["27"], ESP_TOP, rx(10), COLS["e"], GREEN, 0)
if not ONE:
    jumper(px["26"], ESP_TOP, rx(13), COLS["e"], BLUE, 0)

# ---------------- steps
steps = [
    ("1", "ESP32 5V → + rail, row 6", "red jumper", RED),
    ("2", "ESP32 GND → − rail, row 7", "black jumper", BLACK),
    ("3", "ESP32 GPIO 27 → hole e10", "jumper", GREEN),
    ("4", "ESP32 GPIO 26 → hole e13", "jumper", BLUE),
    ("5", "10k resistor: c3 to c10", "brown-black-orange", "#795548"),
    ("6", "10k resistor: c13 to c20", "brown-black-orange", "#795548"),
    ("7", "20k resistor: a10 to − rail (row 10)", "red-black-orange", RED),
    ("8", "20k resistor: a13 to − rail (row 13)", "red-black-orange", RED),
    ("9", "Flow sensor 1 (IN): yellow → b3, red → + rail row 1, black → − rail row 2", "", YEL),
    ("10", "Flow sensor 2 (OUT): yellow → b20, red → + rail row 28, black → − rail row 29", "", YEL),
]
if ONE:
    steps = [st for st in steps if st[0] not in ("4", "6", "8", "10")]
    steps = [(str(i + 1),) + st[1:] for i, st in enumerate(steps)]
y0 = 1120
text(40, y0, "Build steps", 20, weight="bold")
for i, (n, s, note, c) in enumerate(steps):
    col, row = (i // 3, i % 3) if ONE else (i // 5, i % 5)
    x, y = 40 + col * 720, y0 + 36 + row * 30
    rect(x, y - 15, 22, 20, c)
    text(x + 11, y, n, 12, "middle", "bold", "#ffffff")
    text(x + 34, y, s, 15)
    if note:
        text(x + 34 + 7.4 * len(s) + 12, y, note, 13, color=GREY)
text(40, y0 + 212, "Push male-to-male jumpers into each flow sensor's 3-pin plug to reach the breadboard.", 14, color=GREY)
text(40, y0 + 236, "Check every connection before powering on. Plug in the power bank last.", 14, color=GREY)

o.append("</svg>")
Path(__file__).with_name("starter-kit-breadboard-1sensor.svg" if ONE else "starter-kit-breadboard.svg").write_text("\n".join(o), encoding="utf-8")
print("written")

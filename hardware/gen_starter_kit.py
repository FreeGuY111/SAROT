"""Generates hardware/starter-kit-wiring.svg: the ₹1,500 water-loss starter kit
(ESP32 + 2 × YF-S201 flow sensors, powered by a USB power bank).   python gen_starter_kit.py
"""
import sys
from pathlib import Path

ONE = "--one" in sys.argv   # single flow sensor build

W, H = 1500, 1080
o = []

RED, BLACK, YEL, BLUE, GREY = "#d32f2f", "#222222", "#e0a800", "#0a66c2", "#666666"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=15, anchor="start", weight="normal", color="#191919"):
    o.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{esc(s)}</text>')


def wire(points, color, w=4):
    pts = " ".join(f"{x},{y}" for x, y in points)
    o.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>')


def dot(x, y, color):
    o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}"/>')


def box(x, y, w, h, fill="#ffffff", stroke="#191919", sw=2):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def resistor_h(x1, x2, y, label):
    """Horizontal resistor body between x1 (right) and x2 (left), x1 > x2."""
    body_l, body_r = x2 + 15, x1 - 15
    wire([(x1, y), (body_r, y)], BLUE)
    wire([(body_l, y), (x2, y)], BLUE)
    box(body_l, y - 12, body_r - body_l, 24, fill="#f3e5c0", stroke="#8a6d1f")
    text((body_l + body_r) / 2, y - 20, label, 14, "middle", "bold")


def resistor_v(x, y1, y2, label):
    body_t, body_b = y1 + 12, y2 - 12
    wire([(x, y1), (x, body_t)], BLACK)
    wire([(x, body_b), (x, y2)], BLACK)
    box(x - 12, body_t, 24, body_b - body_t, fill="#f3e5c0", stroke="#8a6d1f")
    text(x + 20, (body_t + body_b) / 2 + 5, label, 14, weight="bold")


def ground(x, y):
    wire([(x, y), (x, y + 8)], BLACK, 3)
    for i, half in enumerate((14, 9, 4)):
        wire([(x - half, y + 8 + i * 6), (x + half, y + 8 + i * 6)], BLACK, 3)


o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">')
o.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(40, 50, "SROT starter kit: circuit diagram (1 flow sensor)" if ONE else "SROT starter kit: water-loss monitor wiring", 28, weight="bold")
text(40, 80, ("ESP32 + 1 flow sensor" if ONE else "ESP32 + 2 flow sensors") + ", powered by a power bank. No soldering: build it on the breadboard.", 16, color=GREY)

# ---- power bank + USB cable
box(30, 390, 150, 90, fill="#f4f2ee")
text(105, 430, "Power bank", 17, "middle", "bold")
text(105, 455, "5 V USB", 14, "middle", color=GREY)
wire([(180, 435), (200, 435), (200, 720), (340, 720), (340, 668)], GREY, 6)
text(215, 745, "USB cable (data cable)", 14, color=GREY)

# ---- ESP32
box(220, 200, 240, 450, fill="#eaf2fb", stroke=BLUE, sw=2.5)
text(340, 240, "ESP32 DevKitC", 20, "middle", "bold")
text(340, 263, "38-pin", 14, "middle", color=GREY)
box(320, 648, 40, 20, fill="#cccccc")
text(372, 690, "USB port", 13, color=GREY)
for y, label in ((300, "5V"), (360, "GPIO 27"), (600, "GND")) if ONE else ((300, "5V"), (360, "GPIO 27"), (500, "GPIO 26"), (600, "GND")):
    o.append(f'<rect x="452" y="{y-7}" width="16" height="14" fill="#191919"/>')
    text(440, y + 5, label, 16, "end", "bold")

# ---- 5 V rail (red) and GND rail (black)
RED_END = 320 if ONE else 480
wire([(468, 300), (500, 300), (500, 150), (1220, 150), (1220, RED_END)], RED)
text(860, 140, "5V  (red wires)", 15, "middle", "bold", RED)
wire([(468, 600), (500, 600), (500, 840), (1280, 840), (1280, 390 if ONE else 380)], BLACK)
text(860, 870, "GND  (black wires)", 15, "middle", "bold", BLACK)

# ---- flow sensors
SENSORS = [(280, 360, 320, 390, 360, 640, "Flow sensor" if ONE else "Flow sensor 1 (IN)"),
           (440, 500, 480, 560, 500, 600, "Flow sensor 2 (OUT)")]
for i, (top, yel, red, blk, gpio_y, node_x, name) in enumerate(SENSORS[:1] if ONE else SENSORS):
    box(920, top, 230, 140, fill="#fafafa")
    text(1035, top + 32, name, 17, "middle", "bold")
    text(1035, top + 56, "YF-S201", 14, "middle", color=GREY)
    # terminals
    for y, c in ((yel, YEL),):
        o.append(f'<rect x="912" y="{y-7}" width="16" height="14" fill="{c}"/>')
    for y, c in ((red, RED), (blk, BLACK)):
        o.append(f'<rect x="1142" y="{y-7}" width="16" height="14" fill="{c}"/>')
    text(935, yel + 5, "yellow", 13, color="#7a5c00")
    text(1135, red + 5, "red", 13, "end", color=RED)
    text(1135, blk + 5, "black", 13, "end")
    # red to 5V rail, black to GND rail (hop over the red rail where they cross)
    wire([(1158, red), (1220, red)], RED)
    dot(1220, red, RED)
    if blk < RED_END:   # crosses the red rail: draw a small hop
        o.append(f'<path d="M1158 {blk} H1211 A9 9 0 0 1 1229 {blk} H1280" fill="none" stroke="{BLACK}" stroke-width="4"/>')
    else:
        wire([(1158, blk), (1280, blk)], BLACK)
    dot(1280, blk, BLACK)
    # signal: yellow -> 10k -> node -> GPIO ; node -> 20k -> GND
    wire([(912, yel), (840, yel)], YEL)
    resistor_h(840, 720, yel, "10k")
    wire([(720, yel), (node_x, yel)], BLUE)
    wire([(node_x, yel), (468, gpio_y)], BLUE)
    dot(node_x, yel, BLUE)
    resistor_v(node_x, yel, yel + 80, "20k")
    ground(node_x, yel + 80)

text(560, 640, "⏚ = connect to GND (black rail)", 14, color=GREY)

# ---- notes
notes = [
    "1. Red wire of the sensor goes to the ESP32 5V pin. Black wire goes to GND." if ONE else
    "1. Red wires of both sensors go to the ESP32 5V pin. Black wires go to GND.",
    "2. The yellow wire goes through a 10k resistor to GPIO 27. A 20k resistor goes from GPIO 27 to GND." if ONE else
    "2. Each yellow wire goes through a 10k resistor to its GPIO pin. A 20k resistor goes from that pin to GND.",
    "3. The resistors bring the sensor's 5 V signal down to 3.3 V. Do not skip them.",
    "4. Wires that cross without a dot are not connected.",
]
for i, n in enumerate(notes):
    text(40, 920 + i * 24, n, 15)

# ---- plumbing strip
py = 1030
items = [("Home tap", 40), ("Flow sensor", 260), ("Tee + leak tap", 520), ("Bucket", 780)] if ONE else \
    [("Home tap", 40), ("Flow sensor 1", 260), ("Tee + leak tap", 520), ("Flow sensor 2", 780), ("Bucket", 1040)]
for label, x in items:
    box(x, py - 26, 180, 40, fill="#eaf2fb", stroke=BLUE)
    text(x + 90, py, label, 15, "middle", "bold")
for (_, a), (_, b) in zip(items, items[1:]):
    wire([(a + 180, py - 6), (b - 6, py - 6)], BLUE, 3)
    o.append(f'<polygon points="{b-6},{py-12} {b+2},{py-6} {b-6},{py}" fill="{BLUE}"/>')
text(980 if ONE else 1240, py, "Water flow", 15, color=GREY)

o.append("</svg>")
Path(__file__).with_name("starter-kit-wiring-1sensor.svg" if ONE else "starter-kit-wiring.svg").write_text("\n".join(o), encoding="utf-8")
print("written")

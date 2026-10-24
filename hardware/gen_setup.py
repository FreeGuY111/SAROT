"""Setup illustration for the 1-sensor starter kit: pipe, sensor, electronics, Wi-Fi, phone.
python gen_setup.py  ->  starter-kit-setup.svg
"""
from pathlib import Path

W, H = 1600, 1120
o = []
BLUE, LBLUE, GREY, DARK = "#0a66c2", "#ebf4fd", "#666666", "#191919"
BRASS, HOSE = "#c9a227", "#2e7d32"

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def text(x, y, s, size=16, anchor="start", weight="normal", color=DARK):
    o.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{esc(s)}</text>')
def rect(x, y, w, h, fill, stroke="none", sw=1.5):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def path(d, stroke, w, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da}/>')
def badge(x, y, n):
    rect(x - 15, y - 15, 30, 30, BLUE)
    text(x, y + 6, str(n), 16, "middle", "bold", "#ffffff")

o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">')
rect(0, 0, W, H, "#ffffff")
text(40, 48, "SROT starter kit: how to set it up", 30, weight="bold")
text(40, 78, "One flow sensor. A leak shows up as water that never stops flowing.", 17, color=GREY)

# ---------------- wall + home tap
rect(0, 110, 70, 820, "#e0ddd5")
text(35, 920, "wall", 14, "middle", color=GREY)
rect(70, 232, 70, 26, "#9e9e9e")                     # pipe stub
rect(120, 214, 40, 18, "#c62828")                    # handle
rect(126, 258, 26, 50, "#9e9e9e")                    # spout
text(150, 200, "Home tap", 17, "middle", "bold")
badge(210, 245, 1)

# ---------------- hose from tap to sensor
path("M139 300 C 139 470, 260 560, 400 560", HOSE, 16)
text(205, 455, "garden hose", 15, color=HOSE, weight="bold")

# hose connector + flow sensor
rect(396, 545, 26, 30, BRASS, "#8a6d1f")
rect(422, 532, 190, 56, "#263238")
path("M450 560 H580", "#ffffff", 4)
o.append('<polygon points="580,550 598,560 580,570" fill="#ffffff"/>')
text(517, 620, "Flow sensor (YF-S201)", 16, "middle", "bold")
text(517, 642, "arrow points away from the tap", 14, "middle", color=GREY)
badge(445, 505, 2)

# tee + leak tap + plug
rect(612, 545, 26, 30, BRASS, "#8a6d1f")             # sensor outlet thread
rect(638, 538, 74, 44, BRASS, "#8a6d1f")             # tee body
rect(712, 548, 22, 24, "#757575")                    # plug
text(760, 556, "½ inch plug", 15, weight="bold")
text(760, 576, "(closes this side)", 14, color=GREY)
rect(660, 582, 30, 40, BRASS, "#8a6d1f")             # branch down
rect(652, 622, 46, 22, "#9e9e9e")                    # leak tap body
rect(640, 612, 22, 10, "#c62828")                    # leak tap handle
rect(667, 644, 16, 30, "#9e9e9e")                    # leak tap spout
text(675, 520, "Tee", 15, "middle", "bold")
badge(675, 488, 3)
text(560, 700, "Small tap = the \"leak\"", 15, "end", weight="bold")
for i in range(4):
    o.append(f'<path d="M675 {690 + i * 26} q -5 9 0 14 q 5 -5 0 -14 z" fill="#4fc3f7"/>')

# bucket + floor
path("M590 790 L610 930 L740 930 L760 790 Z", "#5d6d7e", 3, "#d6eaf8")
text(675, 870, "Bucket", 16, "middle", "bold")
rect(70, 930, 1530, 6, "#bdbdbd")

# ---------------- shelf + electronics box
rect(440, 318, 520, 12, "#8d6e63")
text(700, 350, "shelf or table, above the pipe", 14, "middle", color=GREY)
rect(470, 150, 460, 168, "#f4f2ee", "#757575", 2)
text(700, 140, "Plastic box: keeps the electronics dry", 16, "middle", "bold")
rect(495, 200, 150, 90, "#f5f5f0", "#bdbdbd")       # breadboard
for r in range(8):
    for c in range(4):
        rect(505 + r * 17, 212 + c * 18, 5, 5, "#bdbdbd", "none", 0)
text(570, 192, "breadboard", 13, "middle", color=GREY)
rect(665, 205, 130, 70, "#1f3b57")                   # ESP32
text(730, 245, "ESP32", 16, "middle", "bold", "#ffffff")
rect(815, 205, 95, 70, "#37474f")                    # power bank
text(862, 238, "Power", 13, "middle", "bold", "#ffffff")
text(862, 255, "bank", 13, "middle", "bold", "#ffffff")
path("M795 250 H815", "#9e9e9e", 5)
badge(940, 175, 4)
badge(940, 240, 5)

# sensor cable up to the box
for dx, c in ((-6, "#d32f2f"), (0, "#222222"), (6, "#e0a800")):
    path(f"M{510 + dx} 532 C {510 + dx} 450, {560 + dx} 380, {560 + dx} 290", c, 3)
text(470, 440, "3 sensor wires", 14, "end", weight="bold")
text(470, 458, "(red, black, yellow)", 13, "end", color=GREY)

# ---------------- router + Wi-Fi
rect(1080, 200, 130, 46, "#455a64")
text(1145, 229, "Wi-Fi router", 14, "middle", "bold", "#ffffff")
for r in (20, 34, 48):
    path(f"M{1145 - r} {196 - r * 0.2} Q 1145 {176 - r} {1145 + r} {196 - r * 0.2}", BLUE, 3)
path("M930 230 H1078", BLUE, 3, dash="8 8")
path("M1210 230 C 1290 230, 1320 300, 1320 360", BLUE, 3, dash="8 8")
text(1005, 222, "Wi-Fi", 14, "middle", color=BLUE, weight="bold")
text(1145, 280, "Same 2.4 GHz Wi-Fi for", 14, "middle", color=GREY)
text(1145, 298, "the monitor and the phone", 14, "middle", color=GREY)
badge(1240, 175, 6)

# ---------------- phone
rect(1230, 370, 220, 440, "#191919")
rect(1242, 392, 196, 396, "#f4f2ee")
rect(1242, 392, 196, 44, "#ffffff")
text(1256, 421, "SROT", 18, weight="bold", color=BLUE)
# notification
rect(1250, 446, 180, 58, "#ffffff", "#e0dfdc")
rect(1250, 446, 4, 58, "#915907", "none", 0)
text(1262, 466, "Water running nonstop", 13, weight="bold")
text(1262, 484, "My test pipe", 12, color=GREY)
text(1262, 499, "Check taps and pipes.", 12, color=GREY)
# card
rect(1250, 516, 180, 150, "#ffffff", "#e0dfdc")
text(1262, 540, "My test pipe", 14, weight="bold")
text(1262, 557, "Main pipe monitor", 11, color=GREY)
rect(1262, 568, 8, 8, "#915907", "none", 0)
text(1276, 577, "Water running nonstop", 11, weight="bold", color="#915907")
text(1262, 604, "Flow in", 11, color=GREY)
text(1262, 626, "2.1 L/min", 17, weight="bold")
text(1340, 835, "Phone with the SROT app", 15, "middle", "bold")

# ---------------- steps
steps = [
    "Connect the garden hose to the home tap with a hose clip.",
    "Flow sensor: hose connector on the inlet, arrow pointing away from the tap. PTFE tape on threads.",
    "Screw the tee onto the sensor outlet. Small tap points down into the bucket, plug closes the other side.",
    "Electronics in a plastic box on a shelf, above the pipe and away from splashes.",
    "Power bank plugged into the ESP32 (plug it in last, after checking the wiring).",
    "Phone and monitor on the same 2.4 GHz Wi-Fi. Set up with Add → Set up new monitor.",
]
y0 = 975
text(40, y0 - 10, "Setup", 20, weight="bold")
for i, s in enumerate(steps):
    col, row = i // 3, i % 3
    x, y = 40 + col * 790, y0 + 22 + row * 34
    badge(x + 15, y - 6, i + 1)
    text(x + 42, y, s, 15)

# ---------------- test box
rect(1000, 560, 200, 300, LBLUE)
text(1100, 590, "How to test", 17, "middle", "bold", BLUE)
for i, s in enumerate([
    "1. Home tap open,",
    "   small tap closed:",
    "   flow 0. Normal.",
    "2. Open the small tap",
    "   a little and leave it.",
    "3. After the set time:",
    "   Water running",
    "   nonstop alert.",
    "Settings → set 1 min",
    "for a quick test.",
]):
    text(1015, 620 + i * 22, s, 14, weight="bold" if i >= 8 else "normal", color=BLUE if i >= 8 else DARK)

o.append("</svg>")
Path(__file__).with_name("starter-kit-setup.svg").write_text("\n".join(o), encoding="utf-8")
print("written")

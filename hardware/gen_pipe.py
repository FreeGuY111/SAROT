"""Pipe assembly diagram for the 1-sensor starter kit (exploded view + assembled view).
python gen_pipe.py  ->  starter-kit-pipe.svg
"""
from pathlib import Path

W, H = 1600, 1150
o = []
BLUE, GREY, DARK = "#0a66c2", "#666666", "#191919"
BRASS, BRASS_D, HOSE, METAL = "#c9a227", "#8a6d1f", "#2e7d32", "#9e9e9e"

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def text(x, y, s, size=15, anchor="start", weight="normal", color=DARK):
    o.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{esc(s)}</text>')
def rect(x, y, w, h, fill, stroke="none", sw=1.5):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def path(d, stroke, w, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da}/>')
def thread_h(x, y, w, h):
    """Male thread (horizontal), hatched, with PTFE tape band."""
    rect(x, y, w, h, BRASS, BRASS_D)
    for i in range(int(w // 6)):
        path(f"M{x + 3 + i * 6} {y} l -3 {h}", BRASS_D, 1.5)
def thread_v(x, y, w, h):
    rect(x, y, w, h, BRASS, BRASS_D)
    for i in range(int(h // 6)):
        path(f"M{x} {y + 3 + i * 6} l {w} -3", BRASS_D, 1.5)
def tape(x, y):
    rect(x - 13, y - 13, 26, 26, "#ffffff", BLUE, 2)
    text(x, y + 5, "T", 14, "middle", "bold", BLUE)
def fits(x1, x2, y):
    path(f"M{x1} {y} H{x2 - 10}", BLUE, 2.5, dash="7 6")
    o.append(f'<polygon points="{x2-12},{y-7} {x2},{y} {x2-12},{y+7}" fill="{BLUE}"/>')
def fits_v(x, y1, y2):
    path(f"M{x} {y1} V{y2 + 10}", BLUE, 2.5, dash="7 6")
    o.append(f'<polygon points="{x-7},{y2+12} {x},{y2} {x+7},{y2+12}" fill="{BLUE}"/>')
def label(x, y, title, sub=None):
    text(x, y, title, 15, "middle", "bold")
    if sub:
        text(x, y + 19, sub, 13, "middle", color=GREY)

# parts --------------------------------------------------------------------
def home_tap(x, y):
    rect(x - 70, y - 60, 30, 130, "#e0ddd5")               # wall
    rect(x - 40, y - 10, 70, 22, METAL)
    rect(x + 6, y - 28, 34, 16, "#c62828")
    rect(x + 12, y + 12, 22, 40, METAL)
def hose_clip(x, y, vertical=True):
    rect(x - 4, y - 16, 8, 32, "#78909c") if vertical else rect(x - 16, y - 4, 32, 8, "#78909c")
def hose_connector(x, y):
    """Hose tail on the left, ½" female nut on the right."""
    for i in range(3):
        o.append(f'<polygon points="{x + i * 14},{y - 9} {x + 14 + i * 14},{y - 13} {x + 14 + i * 14},{y + 13} {x + i * 14},{y + 9}" fill="{BRASS}" stroke="{BRASS_D}" stroke-width="1.2"/>')
    rect(x + 42, y - 20, 38, 40, BRASS, BRASS_D)
    path(f"M{x + 48} {y - 20} V{y + 20} M{x + 61} {y - 20} V{y + 20} M{x + 74} {y - 20} V{y + 20}", BRASS_D, 1.2)
def sensor(x, y):
    thread_h(x, y - 13, 34, 26)
    rect(x + 34, y - 28, 140, 56, "#263238")
    path(f"M{x + 56} {y} H{x + 140}", "#ffffff", 4)
    o.append(f'<polygon points="{x+140},{y-9} {x+156},{y} {x+140},{y+9}" fill="#ffffff"/>')
    thread_h(x + 174, y - 13, 34, 26)
    for dx, c in ((-6, "#d32f2f"), (0, "#222222"), (6, "#e0a800")):
        path(f"M{x + 104 + dx} {y - 28} v -38", c, 3)
def tee(x, y):
    rect(x, y - 22, 90, 44, BRASS, BRASS_D)
    rect(x + 23, y + 22, 44, 30, BRASS, BRASS_D)
    for cx, cy in ((x + 6, y), (x + 84, y), (x + 45, y + 46)):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{BRASS_D}"/>')
def plug(x, y):
    thread_h(x, y - 11, 26, 22)
    rect(x + 26, y - 17, 22, 34, "#757575")
def small_tap(x, y):
    thread_v(x - 11, y, 22, 28)
    rect(x - 22, y + 28, 44, 26, METAL)
    rect(x - 34, y + 30, 14, 10, "#c62828")
    rect(x - 7, y + 54, 14, 28, METAL)

o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">')
rect(0, 0, W, H, "#ffffff")

# title ----------------------------------------------------------------------
text(40, 48, "SROT starter kit: pipe assembly (1 flow sensor)", 30, weight="bold")
text(40, 78, "Parts in order, then the finished pipe. T = wrap PTFE (teflon) tape on that thread first.", 17, color=GREY)

# ---- exploded view
Y = 260
text(40, 150, "1. Parts in order", 20, weight="bold", color=BLUE)
home_tap(120, Y - 40)
path(f"M143 {Y + 12} C 160 {Y + 70}, 230 {Y + 70}, 270 {Y}", HOSE, 16)
hose_clip(262, Y)
label(120, Y + 130, "Home tap")
label(215, Y + 130, "Garden hose", "+ 2 hose clips")
hose_connector(320, Y)
label(360, Y + 130, "Hose connector", "½ inch female thread")
fits(410, 488, Y)
sensor(490, Y)
tape(507, Y - 50)
tape(681, Y - 50)
label(594, Y + 130, "Flow sensor YF-S201", "arrow points away from the tap")
text(594, Y - 80, "3 wires to the ESP32", 13, "middle", color=GREY)
fits(700, 788, Y)
tee(790, Y)
label(835, Y - 60, "Tee", "3 female threads")
fits(880, 958, Y)
plug(960, Y)
tape(973, Y - 40)
label(990, Y + 130, "½ inch plug", "closes this side")
fits_v(835, Y + 60, Y + 98)
small_tap(835, Y + 100)
tape(880, Y + 114)
text(895, Y + 175, "Small tap (the \"leak\")", 15, weight="bold")

# ---- assembled view
Y2 = 690
text(40, 560, "2. Finished pipe", 20, weight="bold", color=BLUE)
home_tap(120, Y2 - 40)
path(f"M143 {Y2 + 12} C 160 {Y2 + 70}, 250 {Y2 + 60}, 312 {Y2}", HOSE, 16)
hose_clip(300, Y2)
hose_connector(320, Y2)
sensor(400, Y2)
tee(608, Y2)
plug(698, Y2)
small_tap(653, Y2 + 52)
for i in range(3):
    o.append(f'<path d="M653 {Y2 + 150 + i * 22} q -5 9 0 14 q 5 -5 0 -14 z" fill="#4fc3f7"/>')
path(f"M578 {Y2 + 215} L596 {Y2 + 330} L710 {Y2 + 330} L728 {Y2 + 215} Z", "#5d6d7e", 3, "#d6eaf8")
text(653, Y2 + 285, "Bucket", 15, "middle", "bold")
o.append(f'<path d="M190 {Y2 - 110} H560" stroke="{GREY}" stroke-width="1.5" fill="none"/>')
text(190, Y2 - 120, "water flow →", 14, color=GREY)

# ---- steps
steps = [
    ("Wrap PTFE tape 5–6 turns clockwise on every male thread:", "both ends of the sensor, the small tap and the plug."),
    ("Screw the hose connector onto the sensor inlet", "(the end the arrow starts from)."),
    ("Screw the tee onto the sensor outlet.", "Hand-tight plus a quarter turn. Do not over-tighten plastic."),
    ("Screw the small tap into the bottom of the tee", "and the plug into the side."),
    ("Push the hose onto the hose connector and tighten a clip.", "Other end on the home tap, also with a clip."),
    ("Put the bucket under the small tap. Turn the home tap on slowly", "and check every joint for drips. Re-tape any that leak."),
]
x0 = 960
text(x0, 560, "3. How to assemble", 20, weight="bold", color=BLUE)
for i, (a, b) in enumerate(steps):
    y = 600 + i * 72
    rect(x0, y - 16, 28, 28, BLUE)
    text(x0 + 14, y + 4, str(i + 1), 15, "middle", "bold", "#ffffff")
    text(x0 + 40, y + 2, a, 15)
    text(x0 + 40, y + 23, b, 14, color=GREY)

o.append("</svg>")
Path(__file__).with_name("starter-kit-pipe.svg").write_text("\n".join(o), encoding="utf-8")
print("written")

"""Generates hardware/srot-node-v1-schematic.svg (net-label style schematic).

Nets with the same label are electrically connected, as in KiCad. Edit the tables
below and re-run:  python gen_schematic.py
"""
from pathlib import Path

W, H = 2600, 1780
out = []

NET_COLORS = {
    "pwr": "#c62828", "gnd": "#333333", "i2c": "#1565c0", "ana": "#2e7d32",
    "dig": "#ef6c00", "uart": "#6a1b9a", "spi": "#00838f", "nc": "#9e9e9e",
}


def net_kind(n):
    if n in ("+12V", "+5V", "+3V3", "VMODEM", "TDS_PWR", "PH_PWR", "+12V_SW"):
        return "pwr"
    if n == "GND":
        return "gnd"
    if n.startswith("I2C") or n == "ADS1_RDY":
        return "i2c"
    if n.endswith(("_SIG", "_ADC", "_OUT", "_SENSE")):
        return "ana"
    if n.startswith(("GPS", "MODEM", "PZEM")):
        return "uart"
    if n.startswith("SD_"):
        return "spi"
    if n in ("NC", "DO NOT USE", "USB SERIAL"):
        return "nc"
    return "dig"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=13, anchor="start", weight="normal", color="#222", italic=False):
    st = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
               f'font-weight="{weight}" fill="{color}"{st}>{esc(s)}</text>')


def line(x1, y1, x2, y2, color="#222", w=1.6):
    out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"/>')


def dot(x, y, color="#222"):
    out.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{color}"/>')


def rect(x, y, w, h, fill="#fffdf6", stroke="#37474f", rx=6, sw=1.8):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
               f'stroke="{stroke}" stroke-width="{sw}"/>')


def flag(x, y, net, side):
    """Net label flag. side='L' means the flag extends to the left of (x,y)."""
    c = NET_COLORS[net_kind(net)]
    tw = 7.6 * len(net) + 14
    if side == "L":
        pts = f"{x},{y} {x-8},{y-9} {x-8-tw},{y-9} {x-8-tw},{y+9} {x-8},{y+9}"
        tx = x - 8 - tw / 2
    else:
        pts = f"{x},{y} {x+8},{y-9} {x+8+tw},{y-9} {x+8+tw},{y+9} {x+8},{y+9}"
        tx = x + 8 + tw / 2
    out.append(f'<polygon points="{pts}" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="1.3"/>')
    text(tx, y + 4.5, net, 12, "middle", "bold", c)


def module(x, y, w, title, sub, left=(), right=(), stub=26, pitch=26, fill="#fffdf6"):
    """left/right: list of (pin_name, net). Returns box height."""
    n = max(len(left), len(right), 1)
    h = 44 + n * pitch
    rect(x, y, w, h, fill=fill)
    text(x + w / 2, y + 18, title, 14, "middle", "bold")
    if sub:
        text(x + w / 2, y + 34, sub, 11, "middle", color="#555", italic=True)
    for i, (pin, net) in enumerate(left):
        py = y + 52 + i * pitch
        line(x - stub, py, x, py, NET_COLORS[net_kind(net)])
        text(x + 6, py + 4, pin, 12)
        flag(x - stub, py, net, "L")
    for i, (pin, net) in enumerate(right):
        py = y + 52 + i * pitch
        line(x + w, py, x + w + stub, py, NET_COLORS[net_kind(net)])
        text(x + w - 6, py + 4, pin, 12, "end")
        flag(x + w + stub, py, net, "R")
    return h


def resistor_v(x, y1, y2, label, left=False):
    """Vertical zig-zag resistor between y1 and y2 at x."""
    body = 34
    m = (y1 + y2) / 2
    a, b = m - body / 2, m + body / 2
    line(x, y1, x, a)
    line(x, b, x, y2)
    pts = [f"{x},{a}"]
    for i in range(1, 7):
        pts.append(f"{x + (7 if i % 2 else -7)},{a + i * body / 7}")
    pts.append(f"{x},{b}")
    out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#222" stroke-width="1.6"/>')
    if left:
        text(x - 12, m + 4, label, 11, "end")
    else:
        text(x + 12, m + 4, label, 11)


def cap_v(x, y1, y2, label):
    m = (y1 + y2) / 2
    line(x, y1, x, m - 4)
    line(x, m + 4, x, y2)
    line(x - 9, m - 4, x + 9, m - 4, w=2.2)
    line(x - 9, m + 4, x + 9, m + 4, w=2.2)
    text(x + 13, m + 4, label, 11)


def gnd(x, y):
    line(x, y, x, y + 6)
    line(x - 9, y + 6, x + 9, y + 6, w=2)
    line(x - 5, y + 10, x + 5, y + 10, w=2)
    line(x - 2, y + 14, x + 2, y + 14, w=2)


def section(x, y, w, h, title):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" '
               f'stroke="#90a4ae" stroke-width="1.4" stroke-dasharray="7 5"/>')
    text(x + 12, y + 20, title, 14, weight="bold", color="#455a64")


# ---------------------------------------------------------------- canvas
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Segoe UI, Arial, sans-serif">')
out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(40, 46, "SROT Node v1 — Universal ESP32 Node (Sentinel / Scout / Quality / Tank)", 26, weight="bold")
text(40, 72, "Net-label schematic: every flag with the same name is the same wire. "
             "All grounds common. Analog sensors are 5 V; everything entering the ESP32/ADS1115 is ≤ 3.3 V.",
     14, color="#555")

# ---------------------------------------------------------------- power (top-left)
section(30, 95, 610, 425, "A. POWER (USB power bank or 5 V phone charger)")
text(50, 138, "J1  USB 5 V in: power bank via a USB-A to screw-terminal adapter", 12, weight="bold")
text(52, 180, "+", 14, weight="bold", color="#c62828")
line(64, 175, 100, 175, "#c62828", 2)
rect(100, 162, 70, 26, fill="#fff")
text(135, 180, "F1 1A PTC", 11, "middle")
line(170, 175, 225, 175, "#c62828", 2)
dot(225, 175, "#c62828")
flag(225, 175, "+5V", "R")
text(52, 225, "-", 16, weight="bold")
line(64, 220, 100, 220, "#333", 2)
gnd(100, 220)

text(50, 262, "Bulk capacitors", 12, weight="bold")
for i, (net, lab) in enumerate([("+5V", "C1 470uF/16V (at J1)"), ("+5V", "C10 100uF (at ESP 5V pin)")]):
    x0 = 80 + i * 120
    text(x0, 288, net, 11, "middle", "bold", NET_COLORS["pwr"])
    cap_v(x0, 294, 334, "")
    gnd(x0, 334)
    text(x0, 368, lab.split()[0], 11, "middle")
    text(x0, 382, " ".join(lab.split()[1:]), 10, "middle", color="#555")

text(330, 270, "ESP32 is powered from +5V through its 5V pin.", 11, color="#555")
text(330, 286, "Do not also plug its USB port into a PC while", 11, color="#555")
text(330, 302, "the power bank is connected.", 11, color="#555")
text(50, 420, "+3V3 comes from the ESP32 DevKit's on-board regulator (500 mA budget:", 11, color="#555")
text(50, 436, "ADS1115 x2, DS3231, GPS, DS18B20). Never feed 5 V into any ESP32 GPIO.", 11, color="#555")
text(50, 456, "Draw is about 0.2-0.3 A: a 10,000 mAh power bank lasts roughly 1 day.", 11, color="#c62828")
text(50, 476, "Use a power bank without auto-off (or with a low-current mode).", 11, color="#c62828")
text(50, 496, "The +5V rail is also the reference for the ratiometric pressure sensors.", 11, color="#555")

# ---------------------------------------------------------------- signal conditioning (left, bottom)
section(30, 535, 610, 1210, "B. SIGNAL CONDITIONING (dividers, pull-ups, filters)")
dividers = [
    ("P1_SIG", "P1_ADC", "R1 10k", "R2 20k", "C3 10nF", "Pressure 1 (fast, NPW)"),
    ("P2_SIG", "P2_ADC", "R3 10k", "R4 20k", "C4 10nF", "Pressure 2"),
    ("TURB_SIG", "TURB_ADC", "R5 10k", "R6 20k", "C5 100nF", "Turbidity"),
    ("PH_SIG", "PH_ADC", "R7 10k", "R8 20k", "C6 100nF", "pH board Po"),
    ("FLOW1_SIG", "FLOW1", "R9 10k", "R10 20k", None, "Flow 1 pulses (Tank role: ECHO)"),
    ("FLOW2_SIG", "FLOW2", "R11 10k", "R12 20k", None, "Flow 2 pulses (Tank role: TRIG)"),
    ("+5V", "VBUS_SENSE", "R13 20k", "R14 10k", "C7 100nF", "5 V rail monitor (ratiometric)"),
]
for i, (inp, outp, rt, rb, c, desc) in enumerate(dividers):
    col, row = i % 2, i // 2
    x = 70 + col * 300
    y = 590 + row * 240
    text(x - 20, y - 8, desc, 12, weight="bold", color="#455a64")
    flag(x + 60, y + 20, inp, "L")
    line(x + 60, y + 20, x + 90, y + 20)
    resistor_v(x + 90, y + 20, y + 95, rt)
    dot(x + 90, y + 95)
    line(x + 90, y + 95, x + 190, y + 95)
    flag(x + 190, y + 95, outp, "R")
    resistor_v(x + 90, y + 95, y + 170, rb)
    gnd(x + 90, y + 170)
    if c:
        line(x + 150, y + 95, x + 150, y + 125)
        dot(x + 150, y + 95)
        cap_v(x + 150, y + 125, y + 165, c)
        gnd(x + 150, y + 165)

# pull-ups
yb = 1545
text(50, yb, "Pull-ups", 12, weight="bold", color="#455a64")
for i, (net, lab) in enumerate([("ONEWIRE", "R17 4.7k"), ("ADS1_RDY", "R18 10k")]):
    x = 110 + i * 300
    text(x, yb + 22, "+3V3", 11, "middle", "bold", NET_COLORS["pwr"])
    resistor_v(x, yb + 28, yb + 100, lab)
    dot(x, yb + 100)
    line(x, yb + 100, x + 60, yb + 100)
    flag(x + 60, yb + 100, net, "R")
text(50, yb + 140, "ADS1_RDY is open-drain and GPIO34 has no internal pull-up, so R18 is required.", 11, color="#555")
text(50, yb + 156, "TDS module output (0–2.3 V) goes straight to ADS #2 A2 — no divider (only C9 100nF).", 11, color="#555")

# ---------------------------------------------------------------- ESP32 (center)
section(660, 95, 640, 1050, "C. MCU — ESP32-WROOM-32 DevKitC V4 (38-pin, USB at bottom)")
esp_left = [
    ("3V3", "+3V3"), ("EN", "NC"), ("VP / 36", "NC"), ("VN / 39", "VBUS_SENSE"),
    ("34", "ADS1_RDY"), ("35", "GPS_PPS"), ("32", "MODEM_TXD"), ("33", "MODEM_RXD"),
    ("25", "MODEM_PWRKEY"), ("26", "FLOW2"), ("27", "FLOW1"), ("14", "TDS_EN"),
    ("12", "NC"), ("GND", "GND"), ("13", "PH_EN"), ("SD2 / 9", "DO NOT USE"),
    ("SD3 / 10", "DO NOT USE"), ("CMD / 11", "DO NOT USE"), ("5V", "+5V"),
]
esp_right = [
    ("GND", "GND"), ("23", "SD_MOSI"), ("22", "I2C_SCL"), ("TX0 / 1", "USB SERIAL"),
    ("RX0 / 3", "USB SERIAL"), ("21", "I2C_SDA"), ("GND", "GND"), ("19", "SD_MISO"),
    ("18", "SD_SCK"), ("5", "SD_CS"), ("17", "GPS_RXD"), ("16", "GPS_TXD"),
    ("4", "ONEWIRE"), ("0", "BOOT_BTN"), ("2", "STATUS_LED"), ("15", "SOL_EN"),
    ("SD1 / 8", "DO NOT USE"), ("SD0 / 7", "DO NOT USE"), ("CLK / 6", "DO NOT USE"),
]
module(870, 140, 220, "U1  ESP32 DevKitC", "pins in physical order",
       left=esp_left, right=esp_right, stub=40, pitch=40, fill="#eef5ff")
text(980, 990, "GPIO0 = on-board BOOT button (hold 3 s → setup mode)", 11, "middle", color="#555")
text(980, 1006, "GPIO2 = on-board blue LED (status)", 11, "middle", color="#555")
text(980, 1030, "GPIO12 left free: strapping pin, must be LOW at boot.", 11, "middle", color="#c62828")
text(980, 1046, "GPIO 6–11 are the SPI flash — never connect.", 11, "middle", color="#c62828")
text(980, 1070, "UART naming is from the module's side: GPS_TXD = GPS TX → ESP RX (16).", 11, "middle", color="#555")
text(980, 1086, "MODEM_TXD = modem TX → ESP RX (32);  MODEM_RXD = ESP TX (33) → modem RX.", 11, "middle", color="#555")

# ---------------------------------------------------------------- switches (center bottom)
section(660, 1160, 640, 585, "D. PROBE POWER SWITCHES + SOLENOID DRIVER")
for i, (en, pwr, q1, q2, r1, r2) in enumerate([
        ("TDS_EN", "TDS_PWR", "Q1 IRF9540N", "Q3 BC547", "R19 10k", "R21 1k"),
        ("PH_EN", "PH_PWR", "Q2 IRF9540N", "Q4 BC547", "R20 10k", "R22 1k")]):
    x = 720 + i * 300
    y = 1200
    text(x, y + 10, f"High-side switch → {pwr}", 12, weight="bold", color="#455a64")
    # P-MOSFET box
    rect(x + 60, y + 70, 110, 70, fill="#fff")
    text(x + 115, y + 92, q1.split()[0], 12, "middle", "bold")
    text(x + 115, y + 108, q1.split()[1], 11, "middle")
    text(x + 115, y + 128, "P-ch", 10, "middle", color="#555")
    # S at top
    line(x + 115, y + 45, x + 115, y + 70, NET_COLORS["pwr"])
    text(x + 122, y + 62, "S", 11)
    text(x + 115, y + 40, "+5V", 11, "middle", "bold", NET_COLORS["pwr"])
    # D at bottom → PWR flag
    line(x + 115, y + 140, x + 115, y + 170, NET_COLORS["pwr"])
    text(x + 122, y + 158, "D", 11)
    flag(x + 115, y + 170, pwr, "R")
    # G left, pull-up to +5V
    line(x + 20, y + 105, x + 60, y + 105)
    text(x + 46, y + 100, "G", 11)
    dot(x + 20, y + 105)
    resistor_v(x + 20, y + 40, y + 105, r1, left=True)
    text(x + 20, y + 35, "+5V", 11, "middle", "bold", NET_COLORS["pwr"])
    # NPN below gate
    line(x + 20, y + 105, x + 20, y + 200)
    rect(x - 10, y + 200, 90, 60, fill="#fff")
    text(x + 35, y + 222, q2.split()[0], 12, "middle", "bold")
    text(x + 35, y + 238, q2.split()[1] + " NPN", 11, "middle")
    text(x + 26, y + 197, "C", 11)
    line(x + 20, y + 260, x + 20, y + 280)
    text(x + 26, y + 274, "E", 11)
    gnd(x + 20, y + 280)
    # base resistor
    line(x + 80, y + 230, x + 100, y + 230)
    text(x + 84, y + 225, "B", 11)
    out.append(f'<polyline points="{x+100},{y+230} {x+105},{y+222} {x+113},{y+238} {x+121},{y+222} '
               f'{x+129},{y+238} {x+137},{y+222} {x+142},{y+230}" fill="none" stroke="#222" stroke-width="1.6"/>')
    text(x + 121, y + 255, r2, 11, "middle")
    line(x + 142, y + 230, x + 165, y + 230)
    flag(x + 165, y + 230, en, "R")
text(720, 1520, "GPIO HIGH → NPN on → gate pulled to GND → P-FET on → probe powered.", 11, color="#555")
text(720, 1536, "Only one electrochemical probe is powered at a time (pH and TDS interfere).", 11, color="#555")

# solenoid driver
x, y = 720, 1560
text(x, y + 10, "Flush solenoid (Quality role)", 12, weight="bold", color="#455a64")
rect(x + 150, y + 60, 110, 60, fill="#fff")
text(x + 205, y + 84, "Q5 IRLZ44N", 12, "middle", "bold")
text(x + 205, y + 102, "N-ch logic", 10, "middle", color="#555")
line(x + 100, y + 90, x + 150, y + 90)
text(x + 140, y + 85, "G", 11)
out.append(f'<polyline points="{x+60},{y+90} {x+65},{y+82} {x+73},{y+98} {x+81},{y+82} {x+89},{y+98} '
           f'{x+95},{y+90} {x+100},{y+90}" fill="none" stroke="#222" stroke-width="1.6"/>')
text(x + 80, y + 115, "R23 1k", 11, "middle")
line(x + 40, y + 90, x + 60, y + 90)
flag(x + 40, y + 90, "SOL_EN", "L")
dot(x + 120, y + 90)
line(x + 120, y + 90, x + 120, y + 120)
resistor_v(x + 120, y + 120, y + 165, "R24 100k", left=True)
gnd(x + 120, y + 165)
line(x + 205, y + 120, x + 205, y + 145)
text(x + 212, y + 138, "S", 11)
gnd(x + 205, y + 145)
line(x + 205, y + 60, x + 205, y + 40)
text(x + 212, y + 55, "D", 11)
rect(x + 290, y + 20, 120, 50, fill="#fff")
text(x + 350, y + 42, "SV1 solenoid", 11, "middle", "bold")
text(x + 350, y + 58, "5 V mini valve", 10, "middle")
line(x + 205, y + 40, x + 290, y + 40)
line(x + 410, y + 40, x + 450, y + 40, NET_COLORS["pwr"])
flag(x + 450, y + 40, "+5V", "R")
text(x + 350, y + 100, "D2 1N4007 across SV1", 11, "middle")
text(x + 350, y + 114, "(cathode to +5V), flyback", 10, "middle", color="#555")

# ---------------------------------------------------------------- digital modules (column C)
section(1320, 95, 560, 1650, "E. ADC, CLOCK, GPS, STORAGE, MODEM")
cy = 130
cy += module(1450, cy, 210, "U2 ADS1115 #1", "addr 0x48 — FAST pressure",
             left=[("VDD", "+3V3"), ("GND", "GND"), ("SCL", "I2C_SCL"), ("SDA", "I2C_SDA"),
                   ("ADDR", "GND"), ("ALRT", "ADS1_RDY")],
             right=[("A0", "P1_ADC"), ("A1", "NC"), ("A2", "NC"), ("A3", "NC")]) + 30
cy += module(1450, cy, 210, "U3 ADS1115 #2", "addr 0x49 — slow channels",
             left=[("VDD", "+3V3"), ("GND", "GND"), ("SCL", "I2C_SCL"), ("SDA", "I2C_SDA"),
                   ("ADDR", "+3V3"), ("ALRT", "NC")],
             right=[("A0", "P2_ADC"), ("A1", "TURB_ADC"), ("A2", "TDS_OUT"), ("A3", "PH_ADC")]) + 30
cy += module(1450, cy, 210, "U4 DS3231 RTC", "addr 0x68 (+ CR2032)",
             left=[("VCC", "+3V3"), ("GND", "GND"), ("SCL", "I2C_SCL"), ("SDA", "I2C_SDA")],
             right=[("SQW", "NC"), ("32K", "NC")]) + 30
cy += module(1450, cy, 210, "U5 GPS NEO-6M / M8N", "9600 baud, PPS = 1 Hz",
             left=[("VCC", "+3V3"), ("GND", "GND")],
             right=[("TX", "GPS_TXD"), ("RX", "GPS_RXD"), ("PPS", "GPS_PPS")]) + 30
cy += module(1450, cy, 210, "U6 microSD module", "SPI, FAT32",
             left=[("VCC", "+5V"), ("GND", "GND")],
             right=[("MISO", "SD_MISO"), ("MOSI", "SD_MOSI"), ("SCK", "SD_SCK"), ("CS", "SD_CS")]) + 30
cy += module(1450, cy, 210, "U9 A7670C 4G (opt.)", "breakout: 5 V in, 3.3 V UART",
             left=[("VIN 5V", "+5V"), ("GND", "GND")],
             right=[("TXD", "MODEM_TXD"), ("RXD", "MODEM_RXD"), ("PWRKEY", "MODEM_PWRKEY")]) + 10
text(1340, cy + 10, "NEO-6M boards: PPS is often only wired to the LED —", 11, color="#555")
text(1340, cy + 26, "solder a wire to the LED's resistor pad or use an M8N board with a PPS pin.", 11, color="#555")
text(1340, cy + 46, "A7670C bare modules use 1.8 V UART — buy a breakout with level shifting.", 11, color="#c62828")

# ---------------------------------------------------------------- sensors (column D)
section(1900, 95, 680, 1650, "F. FIELD SENSORS (3-pin screw terminals / JST-XH)")
sy = 130
sx = 2060
sy += module(sx, sy, 230, "S1 Pressure transducer", "0–0.5 MPa, G1/4, 0.5–4.5 V",
             left=[("Red  +", "+5V"), ("Black −", "GND")], right=[("Yellow sig", "P1_SIG")]) + 22
sy += module(sx, sy, 230, "S2 Pressure transducer", "0–0.5 / 1.2 MPa",
             left=[("Red  +", "+5V"), ("Black −", "GND")], right=[("Yellow sig", "P2_SIG")]) + 22
sy += module(sx, sy, 230, "FS1 Flow YF-xxx", "hall pulse, K pulses/L",
             left=[("Red  +", "+5V"), ("Black −", "GND")], right=[("Yellow", "FLOW1_SIG")]) + 22
sy += module(sx, sy, 230, "FS2 Flow YF-xxx", "",
             left=[("Red  +", "+5V"), ("Black −", "GND")], right=[("Yellow", "FLOW2_SIG")]) + 22
sy += module(sx, sy, 230, "TS1 DS18B20", "waterproof probe",
             left=[("Red VDD", "+3V3"), ("Black GND", "GND")], right=[("Yellow DQ", "ONEWIRE")]) + 22
sy += module(sx, sy, 230, "QS1 Turbidity module", "always powered (optical)",
             left=[("V+", "+5V"), ("G", "GND")], right=[("A out", "TURB_SIG")]) + 22
sy += module(sx, sy, 230, "QS2 TDS module", "switched (Q1)",
             left=[("+", "TDS_PWR"), ("−", "GND")], right=[("A", "TDS_OUT")]) + 22
sy += module(sx, sy, 230, "QS3 pH PH-4502C + E-201", "switched (Q2)",
             left=[("V+", "PH_PWR"), ("G", "GND")], right=[("Po", "PH_SIG"), ("Do / To", "NC")]) + 22
text(1920, sy + 4, "Tank role (instead of FS1/FS2 + GPS):", 12, weight="bold", color="#455a64")
text(1920, sy + 22, "JSN-SR04T: VCC +5V, GND, TRIG → FLOW2_SIG terminal, ECHO → FLOW1_SIG terminal", 11)
text(1920, sy + 38, "(the existing 10k/20k dividers make both pins 3.3 V-safe).", 11, color="#555")
text(1920, sy + 56, "PZEM-004T v3: TTL side 5V pin → +3V3, TX → GPS_TXD, RX → GPS_RXD.", 11)
text(1920, sy + 72, "Mains side of the PZEM must be wired by an electrician.", 11, color="#c62828")

# role population table
rx, ry = 1920, 1250
text(rx, ry, "What to populate per node role (same PCB / perfboard):", 13, weight="bold", color="#455a64")
rows = [("Role", "Populate", "Firmware role"),
        ("Sentinel", "U2 + S1 (+S2/U3), FS1, U5 GPS, U4, U6, U9 or Wi-Fi", "sentinel (860 Hz)"),
        ("Scout", "U2 + S1, Wi-Fi; power bank", "scout (1 Hz)"),
        ("Quality", "U3, QS1–QS3, TS1, Q1–Q5, SV1, U4, U6", "quality"),
        ("Tank/Pump", "U3 + S2, JSN-SR04T, PZEM-004T, U4", "tank"),
        ("Bench demo", "everything; any sensor may be missing", "sim = on fakes it")]
for i, (a, b, c) in enumerate(rows):
    yy = ry + 28 + i * 26
    w = "bold" if i == 0 else "normal"
    if i:
        out.append(f'<line x1="{rx}" y1="{yy-18}" x2="{rx+640}" y2="{yy-18}" stroke="#cfd8dc"/>')
    text(rx, yy, a, 12, weight=w)
    text(rx + 100, yy, b, 12, weight=w)
    text(rx + 500, yy, c, 12, weight=w)
text(rx, ry + 200, "Wiring tips: I²C at 400 kHz, keep I²C wires < 30 cm; sensor cables use shielded 3-core,", 11, color="#555")
text(rx, ry + 216, "shield to GND at the node end only; star-ground the analog returns at the ADS1115s.", 11, color="#555")
text(rx, ry + 236, "C9 100nF: TDS_OUT to GND, at U3.", 11, color="#555")

# legend
lx, ly = 1920, 1660
text(lx, ly, "Net colours:", 12, weight="bold")
for i, (k, name) in enumerate([("pwr", "power"), ("gnd", "ground"), ("i2c", "I²C"), ("ana", "analog"),
                               ("dig", "digital"), ("uart", "UART"), ("spi", "SPI"), ("nc", "unused")]):
    xx = lx + (i % 4) * 160
    yy = ly + 20 + (i // 4) * 24
    out.append(f'<rect x="{xx}" y="{yy-11}" width="16" height="14" fill="{NET_COLORS[k]}" fill-opacity="0.25" '
               f'stroke="{NET_COLORS[k]}"/>')
    text(xx + 22, yy, name, 12)

out.append("</svg>")
Path(__file__).with_name("srot-node-v1-schematic.svg").write_text("\n".join(out), encoding="utf-8")
print("written")

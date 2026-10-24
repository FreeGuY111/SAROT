# SROT hardware shopping list

Powered by a **USB power bank** (or any 5 V phone charger). Prices are approximate (India, Oct 2026). Buy online from Robu.in, Robocraze, ElectronicsComp or Amazon.in, or from a local electronics market (Lamington Road Mumbai, SP Road Bengaluru, Nehru Place Delhi, Ritchie Street Chennai).

**Budget of ₹1,500?** Build the [starter kit](STARTER-KIT.md): one real monitor that detects water loss (about ₹1,250).

## Step 0: test today with just a board (₹400)

| Item | Qty | ₹ |
|---|---|---|
| ESP32-WROOM-32 DevKitC, **38-pin**, with USB cable | 1 | 400 |

Plug it into the power bank, flash the firmware with demo mode on, and the app connects to it over Wi-Fi like a full monitor.

## 1. Main pipe monitor (detects water loss and bursts)

### Budget version (about ₹2,200 each)

| Item | Qty | ₹ |
|---|---|---|
| ESP32-WROOM-32 DevKitC (38-pin) | 1 | 400 |
| ADS1115 16-bit ADC module | 1 | 200 |
| Pressure sensor, 0–0.5 MPa, G1/4, 0.5–4.5 V, 3-wire | **1** | 900–1,100 |
| Water flow sensor YF-S201 (½ inch) | 2 (in + out) | 200 |
| USB-A male to screw-terminal adapter (or cut an old USB cable) | 1 | 40 |
| 1 A PTC resettable fuse | 1 | 20 |
| Perfboard, headers, screw terminals | 1 set | 150 |

### Add later, only if needed

| Item | Why | ₹ |
|---|---|---|
| GPS with **PPS pin** + antenna | Only for finding *where* a burst is, using two monitors | 400–900 |
| Second pressure sensor (outlet) | Pressure drop across the pipe. Not required | 900–1,100 |
| DS3231 clock module | Keeps time without Wi-Fi. Not needed on Wi-Fi | 200 |
| microSD module + card | Stores data when Wi-Fi is down | 330 |

## 2. Water quality monitor (optional, about ₹3,500)

| Item | Qty | ₹ |
|---|---|---|
| ESP32-WROOM-32 DevKitC (38-pin) | 1 | 400 |
| ADS1115 module | 1 | 200 |
| Turbidity sensor module | 1 | 550 |
| TDS sensor module | 1 | 450 |
| pH sensor kit (PH-4502C board + E-201 probe) | 1 | 1,300 |
| pH buffer powder (4.00 and 6.86) | 1 set | 150 |
| DS18B20 waterproof temperature probe | 1 | 120 |
| 5 V mini solenoid valve (optional, auto flush) | 1 | 350 |
| USB-A to terminal adapter + PTC fuse | 1 | 60 |

## 3. Tank monitor (optional, about ₹1,600)

| Item | Qty | ₹ |
|---|---|---|
| ESP32-WROOM-32 DevKitC (38-pin) | 1 | 400 |
| JSN-SR04T waterproof ultrasonic sensor | 1 | 400 |
| PZEM-004T v3 power meter (100 A, with CT coil) | 1 | 750 |
| USB-A to terminal adapter | 1 | 40 |

The PZEM connects to mains power. Get an electrician to wire that side.

## 4. Small parts (one pack covers 3–4 monitors, about ₹1,500)

Resistor kit (1k, 4.7k, 10k, 20k, 100k), capacitor kit (10 nF, 100 nF, 100 µF, 470 µF), 2 × IRF9540N, 5 × BC547, 2 × IRLZ44N, 5 × 1N4007, perfboards, female header strips, screw terminals, jumper wires, IP65 boxes with cable glands, 3-core cable.

## 5. Power

| Item | ₹ |
|---|---|
| Power bank, 10,000 mAh (one per monitor) | you have it / 700–1,000 |
| Or a 5 V 2 A phone charger for monitors near a socket | 200 |

- One monitor draws about 0.2–0.3 A, so a 10,000 mAh power bank lasts **about 1 day**.
- Some power banks switch off when the load is small. If yours does, use its low-current mode (many Mi / Ambrane banks: double-press the button), or a phone charger.
- No 12 V adapter or LM2596 step-down module is needed.

## 6. Plumbing for a demo pipe setup (about ₹4,000 without a pump)

25 m of 1 inch uPVC pipe, tees and elbows, 3–4 ball valves (leak taps), G1/4-to-½ inch adapters, PTFE tape. For water pressure, connect it to a tap fed by an overhead tank instead of buying a pump (a 0.5 HP pump adds ₹3,500–5,000).

## Saving money on pressure sensors

The pressure sensor is the most expensive part. Ways to cut the cost:

1. **Use one per monitor, not two.** The outlet sensor is optional; the firmware and app work without it.
2. **Buy the same sensor from AliExpress** for about ₹400–600. Delivery takes 2–3 weeks. Search: *"pressure transducer 5V G1/4 0.5MPa 0.5-4.5V"*.
3. **Start with flow sensors only (₹400 per monitor).** Two YF-S201 sensors (in and out) already detect water loss and leaks. Add a pressure sensor later for burst detection and pressure alerts. Skip the ADS1115 too until then.
4. **Skip GPS, clock and SD card at first.** GPS is only needed to locate a burst between two monitors. Time comes from the internet over Wi-Fi.

Do not buy the cheap "MPS20N0040D / HX710B" air-pressure modules: they are for air and only measure up to 4 m of water.

## Totals

| Setup | About |
|---|---|
| Just test the app with a real board | ₹400 |
| 1 monitor, flow only (water loss) | ₹1,000 |
| 1 monitor with pressure (budget version) | ₹2,200 |
| 2 monitors with pressure + GPS (burst location) | ₹5,500–6,500 |
| + water quality monitor | + ₹3,500 |
| + tank monitor | + ₹1,600 |
| + small parts | + ₹1,500 |

## Buying tips

- **ESP32:** get the 38-pin DevKitC. The wiring diagram uses its pin layout.
- **Pressure sensor:** 0–0.5 MPa range, 0.5–4.5 V output, 3 wires. Not the 4–20 mA type.
- **GPS (if you add it):** check the board has a **PPS** pin.
- **Flow sensor:** match the pipe size. YF-S201 is ½ inch, YF-B10 is 1 inch.
- Wiring diagram and build steps: `hardware/README.md` and `hardware/srot-node-v1-schematic.png`.

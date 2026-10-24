# Hardware: ESP32 nodes, sensors and bill of materials

This is the design-level parts list for all four node types. For what is actually built and wired today, see [hardware/README.md](../hardware/README.md) and the [shopping list](../hardware/SHOPPING-LIST.md).

Prices are approximate retail in India (Oct 2026, incl. GST) from Robu.in, Robocraze, Zbotic, ElectronicsComp, Indian Hobby Center, Amazon.in and IndiaMART. They vary by about ±30% between sellers. Buy one or two extra of each sensor, since cheap modules differ from unit to unit.

---

## 1. Master sensor list

### Core (needed for SROT to work)

| # | Part | Use | Typical price (₹) | Notes |
|---|---|---|---|---|
| 1 | **ESP32-WROOM-32 DevKitC (38-pin)** | Scout / Quality / Tank nodes | 350–550 | Has Wi-Fi + BLE (BLE is used for commissioning from the app) |
| 2 | **ESP32-S3 DevKit N16R8** (8 MB PSRAM) | Sentinel nodes | 700–1,000 | PSRAM holds a 30 s pressure ring buffer for transient capture |
| 3 | **Pressure transducer, 0.5–4.5 V, G1/4, stainless, 0–0.5 MPa** | Network pressure | 900–1,400 | Use 0–0.5 MPa for distribution (Indian network pressure is usually under 5 bar → better resolution). Use 0–1.2 MPa only at pump discharge. ~1% FS accuracy, ~2 ms response time (fast enough for transients). |
| 4 | **ADS1115 16-bit ADC** (I2C) | Precise analog reads | 150–300 | The ESP32's own ADC is nonlinear and noisy. ADS1115 does 860 samples/s on one channel, which suits NPW. Use two (addresses 0x48/0x49) when one node needs both fast pressure and slow quality channels. |
| 5 | **YF-S201** (½") / **YF-B10 / YF-DN25** (1") / **YF-DN50** (2") hall flow sensor | Flow on test rig / small mains | 150–300 / 400–900 / 1,200–2,200 | ±10% out of the box. **Calibrate with a bucket test** to reach ±2–3%. Pulse output. |
| 6 | **DS18B20 waterproof** | Water temperature (viscosity, EC & pH compensation) | 80–150 | OneWire |
| 7 | **DS3231 RTC** | Timestamps while offline | 150–250 | |
| 8 | **microSD module + 8–16 GB card** | Store-and-forward buffer | 50–100 + 250 | |
| 9 | **SIMCom A7670C 4G LTE Cat-1** | Cellular uplink | 700–1,700 | Works on Indian 4G. **Skip SIM800L**: it's 2G only, and Jio has no 2G network. |

### Water quality (Quality node)

| # | Part | Price (₹) | Notes |
|---|---|---|---|
| 10 | **Turbidity sensor module** (optical, Gravity-style) | 450–900 | Gives relative turbidity, not true NTU. Calibrate against formazin or a lab sample, and rely on it mainly for **trends and first-flush spikes**. The top of the sensor isn't waterproof, so mount it in a flow chamber. |
| 11 | **TDS/EC sensor module** | 400–500 | Temperature-compensate with the DS18B20 |
| 12 | **pH kit (PH-4502C board + E-201 probe)** | 900–1,500 | Calibrate every 1–2 weeks with pH 4/7 buffers. Probe lasts ~6–12 months. Keep it wet. |
| 13 | **ORP sensor kit** *(optional)* | 2,500–4,500 | Combined with pH, gives an estimated **free chlorine** reading. A true residual-chlorine sensor costs ₹20k+. |
| 14 | **12 V solenoid valve ½"** | 250–450 | Flush-and-measure cycle: saves water and makes probes last longer |
| 15 | **Logic-level MOSFETs (IRLZ44N) / 4-ch relay** | 30–150 | Power one probe at a time. pH and TDS probes **interfere electrically** in the same water (the TDS board uses AC excitation). |
| 16 | **DPD chlorine test kit** (manual) | 300–600 | Monthly field calibration for chlorine estimates |

### Transient and timing (Sentinel node)

| # | Part | Price (₹) | Notes |
|---|---|---|---|
| 17 | **u-blox NEO-6M / NEO-M8N GPS + antenna** | 250–450 / 600–1,000 | Provides the **PPS pulse** for µs time sync. Most cheap NEO-6M boards (GY-GPS6MV2) don't break out PPS; it drives the LED. Solder a wire to the LED pad, or buy a board with a PPS pin. |

### Tank / pump node

| # | Part | Price (₹) | Notes |
|---|---|---|---|
| 18 | **JSN-SR04T waterproof ultrasonic** | 300–500 | Tank level (25–450 cm). Gives the tank mass balance (virtual outflow meter). |
| 19 | **PZEM-004T v3.0 (100 A, with CT)** | 600–900 | Pump voltage, current, kW and kWh over UART. **Mains wiring must be done by an electrician.** |
| 20 | **SCT-013-030 clamp CT** *(alternative)* | 350–550 | Non-invasive current only |
| 21 | **Reed / limit switch** | 20–50 | Valve open/closed state |

### Integration and alternative radio

| # | Part | Price (₹) | Notes |
|---|---|---|---|
| 22 | **MAX485 / TTL-RS485 module** | 50–120 | Reads the utility's existing flow meters and PLCs over Modbus RTU |
| 23 | **LoRa SX1276 868 MHz (Ra-01H / RFM95W-868)** | 450–900 | **Use the 865–867 MHz band (IN865)**, which India made licence-exempt (GSR 853(E), 2021). Don't buy 433 MHz modules for this. |

### Pilot-grade upgrades (for a real utility pilot)

| Part | Price (₹) | Why |
|---|---|---|
| 4–20 mA pressure transmitter, 0.25–0.5% accuracy | 2,500–6,000 | ~3× better accuracy, long cables, industrial build. Read through a 150 Ω shunt into ADS1115 (20 mA → 3.0 V). |
| Multi-jet water meter with pulse output, DN15–DN50 | 1,500–6,000 | Proper metrology instead of a hall sensor |
| Existing electromagnetic meters (utility-owned) | — | Read over RS485 Modbus. Don't buy. |

### Experimental

| Part | Price (₹) | Use |
|---|---|---|
| ADXL345 / MPU6050 accelerometer | 100–250 | Acoustic/vibration leak correlation on metal pipes |
| Piezo disc + MAX4466 preamp | 50–200 | Contact "listening" sensor |

### Power and enclosure

| Part | Price (₹) |
|---|---|
| 2× 18650 Li-ion + holder + BMS/TP4056 | 400–700 |
| 6 V 3 W solar panel (Scout) / 12 V 20 W panel (Sentinel) | 250–450 / 1,000–1,600 |
| 12 V 7 Ah LiFePO4 or SLA (Sentinel off-grid) | 1,200–3,000 |
| LM2596 / MP1584 buck, MT3608 boost | 50–100 each |
| IP65/IP67 ABS enclosure + cable glands | 250–600 |
| G1/4 brass tee, ball valve, nipples, PTFE tape | 200–400 |

---

## 2. Node builds and costs

| Node | Contents | Approx. cost (₹) |
|---|---|---|
| **Sentinel (S)** | ESP32-S3, ADS1115, 1–2 pressure transducers, GPS (PPS), A7670C, RTC, SD, flow (YF-DN50 or Modbus to existing meter), 12 V supply/solar, enclosure, fittings | **7,500–11,000** |
| **Scout (P)** | ESP32, ADS1115, 1 pressure transducer, LoRa 868 or A7670C, 2×18650 + 3 W solar, enclosure, fittings | **3,800–5,000** |
| **Quality (Q)** | ESP32, ADS1115, turbidity, TDS, pH, DS18B20, solenoid + MOSFETs, flow chamber, A7670C, power | **5,500–7,000** (+3,500 with ORP) |
| **Tank/Pump (T)** | ESP32, JSN-SR04T, PZEM-004T, 1–2 pressure transducers, ADS1115, Wi-Fi/4G, enclosure | **4,000–5,500** |

For comparison, a commercial utility pressure logger costs ₹40k–1.5 lakh.

---

## 3. Wiring essentials (ESP32)

```text
I2C (ADS1115 ×2, DS3231) ...... SDA GPIO21, SCL GPIO22   (S3: pick any, e.g. 8/9)
ADS1115 ALERT/RDY ............. GPIO34 (interrupt on each conversion → exact sample timing)
Pressure transducer ........... 5 V supply; output 0.5–4.5 V → divider 10k/20k → ADS1115 AIN0
                                 Also read the 5 V rail through a divider on AIN3 → ratiometric correction
Flow sensor pulse ............. GPIO27 via 10k/20k divider (YF outputs 5 V pulses), pull-up, IRAM ISR
DS18B20 ....................... GPIO4 + 4.7k pull-up to 3.3 V
GPS ........................... UART1 RX GPIO16 / TX GPIO17, PPS → GPIO35 (interrupt, captures µs timer)
A7670C 4G ..................... UART2 RX GPIO26 / TX GPIO25, PWRKEY GPIO33; separate 4 V/2 A supply (TX bursts)
microSD ....................... SPI: SCK 18, MISO 19, MOSI 23, CS 5
Quality probe power ........... MOSFET gates GPIO12/13/14 (one probe on at a time)
Solenoid valve ................ MOSFET + flyback diode, GPIO15
RS485 (MAX485) ................ UART2 alt / GPIO + DE/RE pin
```

Rules that save hours of debugging:

- **Use only ADC1 pins (GPIO32–39)** for any direct analog read. ADC2 stops working once Wi-Fi is on.
- **Never feed 5 V into ESP32 pins.** Power the ADS1115 from 3.3 V and divide the sensor outputs (PGA ±4.096 V).
- **Don't fit a pressure snubber on Sentinel nodes.** It damps exactly the transient you need. Scout nodes may use one.
- Give the 4G modem its own supply and a 1000 µF capacitor. Its 2 A TX bursts brown out the ESP32 otherwise.
- **Zero-calibrate** each pressure transducer open to air, then check it against a reference gauge at 2–3 points. Save the offset/gain into the device record from the app.
- A Quality node draws water through a **side tap into a small flow-through chamber**. It never puts probes inside the pressurised main.

---

## 4. Power budgets

| Node | Load | Strategy |
|---|---|---|
| Sentinel | ESP32 + modem + GPS + transducer ≈ 1–1.5 W continuous (~30 Wh/day) | Mains at pump houses/valve chambers, or a 20 W panel + 7 Ah battery (~2 days autonomy) |
| Scout | ESP32 deep-sleep ~10 µA, ULP reads pressure every 1 s; transducer powered only while sampling; LoRa uplink every 5–15 min | 2×18650 + 3 W panel → runs indefinitely in Indian sun. On 4G, batch uploads hourly. |
| Quality | Probes on ~2 min per cycle, solenoid pulses, modem | 10 W panel + battery, or mains |

---

## 5. Test rig (algorithm validation and demos)

The rig recreates leak, burst, blockage and sensor fault on a table-sized network at known positions, so the system's errors can be measured.

```text
   Overhead tank / 0.5 HP pump ──► S1 ──────── 8 m ──────── J1 ──── 6 m ───── S2 ──► return
                                                │
                                              5 m (branch)
                                                │
                                               S3 ──► return
   Leak taps (ball valves) at chainages 2 m, 5 m, 11 m      Gate valve on branch = "blockage"
   Fast-closing solenoid at end = transient source / wave-speed calibration
```

- **Pipe:** rigid uPVC 1" (25 mm) — *not* flexible hose; a hose's wave speed is too low and too variable.
- **Sensors:** 3 pressure (S1–S3) at 860 Hz, 2 flow sensors (inlet + one outlet), 1 Quality chamber on a side tap. GPS on 2 nodes, or one ESP32 reading two ADS1115s for perfect sync on a small rig.
- **Wave speed:** in 1" uPVC, *a* is ~350–450 m/s, so a wave crosses 14 m in ~35 ms, which 860 Hz sampling resolves. The expected location error is under 0.5 m. This is a calculation, not a measurement from the rig.
- **Demo scenarios:**
  1. Open a leak tap → flow imbalance + NPW location + FAVAD loss estimate vs. bucket-measured truth
  2. Partly close the branch gate → classified as blockage, not leak
  3. Unplug/short one sensor → classified as sensor fault
  4. Add a few drops of milk/clay to the tank → turbidity alert + trace upstream
  5. Stop and restart the pump → supply-window detection + first-flush check
- **Rig cost:** ~₹15,000–22,000 including pump, pipes, fittings, 3 pressure transducers, 2 flow sensors, 2–3 ESP32s, one quality set.

---

## 6. Minimum shopping list for the test rig (~₹12–15k)

| Qty | Item |
|---|---|
| 1 | ESP32-S3 N16R8 |
| 2 | ESP32-WROOM-32 DevKitC |
| 3 | Pressure transducer 0–0.5 MPa G1/4 (0.5–4.5 V) |
| 2 | ADS1115 |
| 2 | YF-B10 or YF-DN25 1" flow sensor |
| 1 | NEO-6M/M8N GPS (with PPS) |
| 1 | A7670C 4G (or use Wi-Fi for the demo) |
| 1 each | Turbidity, TDS, pH kit, DS18B20 |
| 1 | JSN-SR04T (tank level) |
| 1 | microSD module, DS3231 |
| — | 1" uPVC pipe ~25 m, tees, 4 ball valves, G1/4 adapters, 0.5 HP pump or tank, enclosure, wires, buck converters |

---

## Sources (price checks)

- [Zbotic: 1.2 MPa G1/4 pressure transducer](https://zbotic.in/product/pressure-transducer-transmitter-sensor-g1-4-1-2mpa-stainless-steel/)
- [Indian Hobby Center: 1.2 MPa pressure transducer](https://www.indianhobbycenter.com/products/1-2mpa-stainless-steel-pressure-transducer-sensor)
- [Robu: 4–20 mA G1/4 pressure sensor](https://robu.in/product/pro-range-pr15c-pas-100-digital-pressure-sensor-010mpa-420ma-g1-4-1m/)
- [KTRON: A7670C 4G board](https://www.ktron.in/product/sim-a7670c-4g-lte-development-board/)
- [IndiaMART: A7670C module](https://www.indiamart.com/proddetail/sim-a7670c-4g-lte-module-2849960704762.html)
- [Robu: turbidity sensor module](https://st.robu.in/product/turbidity-sensor-module/)
- [Robocraze: pH/turbidity/flow sensors](https://robocraze.com/collections/ph-turbidity-flow-sensors)
- [ElectronicsComp: YF-DN50](https://www.electronicscomp.com/2-inch-water-flow-sensor-yf-dn-50)
- [Robu: YF-DN50](https://robu.in/product/water-flow-sensor-sea-yfdn50-flowmeter-g2-10-200l-min-5-24v/)
- [LoRa bands in India: WPC rules for 865–867 MHz](https://www.autoabode.com/blog/lora-frequency-bands-india-wpc-rules-eta-compliance)

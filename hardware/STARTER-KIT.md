# SROT starter kit (budget ₹1,500)

One real monitor that detects **water loss**: a flow sensor before and after a section of pipe. If less water comes out than goes in, there is a leak. No soldering, no pressure sensor.

## Shopping list (about ₹1,350)

| Item | Qty | ₹ |
|---|---|---|
| ESP32-WROOM-32 DevKitC, 38-pin, with USB cable | 1 | 400 |
| YF-S201 water flow sensor (½ inch) | 2 | 400 |
| Breadboard, 400 points | 1 | 80 |
| Jumper wires, male-to-male and male-to-female | 1 pack | 100 |
| Resistors: 10 kΩ ×2 and 20 kΩ ×2 | 4 | 20 |
| ½ inch tee with 3 threaded (female) ends, GI or PVC | 1 | 40 |
| ½ inch small tap (bib cock), this is the "leak" | 1 | 80 |
| ½ inch female thread to hose connector (hose tail) | 2 | 80 |
| ½ inch garden hose | 2 m | 80 |
| Hose clips | 4 | 40 |
| PTFE (teflon) tape | 1 | 20 |
| **Total** | | **about ₹1,350** |

Also needed (you likely have them): a power bank, a USB **data** cable for the board, and a PC once to load the firmware.

Keep the remaining ~₹150 for delivery charges.

## Plumbing

```
home tap ── hose ──► [flow sensor 1] ──► tee ──► [flow sensor 2] ── hose ──► bucket
                                          │
                                       small tap  ("leak")
```

Both flow sensors and the leak tap screw straight into the tee. The hose connectors join the hoses to the free ends of the sensors. The arrow on each flow sensor must point in the direction the water flows. Wrap PTFE tape on every thread.

## Wiring

| From | To |
|---|---|
| Flow sensor 1 and 2: **red** wire | ESP32 **5V** pin (marked 5V or VIN) |
| Flow sensor 1 and 2: **black** wire | ESP32 **GND** |
| Flow sensor 1: **yellow** wire | 10 kΩ resistor → ESP32 **GPIO 27** |
| Flow sensor 2: **yellow** wire | 10 kΩ resistor → ESP32 **GPIO 26** |
| ESP32 GPIO 27 | 20 kΩ resistor → GND |
| ESP32 GPIO 26 | 20 kΩ resistor → GND |

The resistors bring the sensor's 5 V pulses down to 3.3 V. **Do not skip them** or the ESP32 can be damaged.

Breadboard build (hole by hole): [starter-kit-breadboard.png](starter-kit-breadboard.png)
Circuit diagram: [starter-kit-wiring.png](starter-kit-wiring.png)

## Set up

1. Connect the ESP32 to the PC with the USB cable and double-click **`flash-firmware.bat`** in the repository root. Then power the ESP32 from the power bank.
2. In the app: **Add → Set up new monitor**. Choose type **Main pipe monitor**, leave **Demo mode** off.
3. Open the monitor → **Calibrate → Flow meter**. Do the bucket test for **both** sensors. Two cheap sensors can differ by up to 10%, and calibrating stops false alarms.
4. Run water through the pipe. Flow in and flow out should match, and Water loss should be near 0%.
5. Open the small tap. Within about 30 seconds Water loss rises and you get a **Water loss** notification.

The pressure rows show "Sensor not connected". That is expected until you add a pressure sensor.

## Only one flow sensor?

It still works as a leak detector: with all taps closed the flow should be zero, so water that keeps flowing means a leak.

- **Wiring:** follow [starter-kit-breadboard-1sensor.png](starter-kit-breadboard-1sensor.png) (steps for sensor 2 and GPIO 26 are left out).
- **Plumbing:** home tap → hose → flow sensor → tee. Screw the small tap into one side of the tee and close the third side with a ½ inch plug (₹15), or connect a hose to a bucket.
- **Test:** in the app, go to **Settings → Water running nonstop** and set **1** minute. Open the home tap, then crack the small tap open (the "leak") and leave it. After a minute of nonstop flow you get a **Water running nonstop** notification.
- For real use set it back to 30 minutes or more, so a long shower doesn't count as a leak.
- Add a second YF-S201 (₹200) later to get the in-versus-out **Water loss** check.

## Next upgrades

| Add | Gives you | ₹ |
|---|---|---|
| ADS1115 + pressure sensor (0–0.5 MPa, 0.5–4.5 V) | Pressure readings, low/high pressure alerts, burst detection | 200 + 400–1,100 |
| Second monitor + GPS (PPS) on each | Finds where along a pipe a burst happened | 1,500–2,500 |
| Turbidity + TDS sensors | Water quality checks | 1,000 |

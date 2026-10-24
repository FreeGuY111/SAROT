# SROT demo guide (1 flow sensor)

## A. Load the code onto the ESP32 (once)

**Easiest:** connect the ESP32 to the PC with the USB data cable and double-click **`flash-firmware.bat`** in the repository root. If it stays on "Connecting...", hold the **BOOT** button on the board for 2 seconds.

**Or with Arduino IDE:** open `firmware-arduino/SROT/SROT.ino` and follow `firmware-arduino/README.md` (board package esp32 **2.0.17**, board **ESP32 Dev Module**, partition **Minimal SPIFFS**).

Then unplug it from the PC and plug it into the power bank.

| Blue light on the ESP32 | Meaning |
|---|---|
| Slow blink | Setup mode, waiting for the app |
| Fast blink | Trying to join Wi-Fi |
| Steady on | Connected |

## B. Install the latest app

Install the APK as described in [INSTALL-APK.md](INSTALL-APK.md). Installing over an older version keeps your settings. Allow notifications when it asks.

## C. Connect the monitor to the app (once)

1. ESP32 on the power bank, blue light blinking slowly.
2. On the phone, turn **mobile data off**.
3. In SROT: **Add → Set up new monitor**.
4. Tap **Open Wi-Fi settings**, join **SROT-xxxxxx** (password **srot1234**). If Android says "No internet", choose **Stay connected**. Go back to the app and tap **Continue**.
5. Choose the Wi-Fi the monitor will use and enter its password. It must be **2.4 GHz**.
6. Name it (for example "Demo pipe"), type **Main pipe monitor**, Demo mode **off**, tap **Connect**.
7. When it says connected, switch the phone back to that same Wi-Fi and turn mobile data on. Tap **View monitor**. The blue light is now steady.

**At a venue with no Wi-Fi:** use a **second phone's hotspot** (set to 2.4 GHz). Connect both the monitor (step 5) and your demo phone to that hotspot. The phone running the app should not be the hotspot itself.

## D. Before the demo

1. **Settings → Water running nonstop:** set **1** minute.
2. **Settings → Notifications → Send test notification.** Check that it arrives.
3. Optional: **Monitor → Calibrate → Flow meter** bucket test with a 2 litre bottle, for accurate L/min.
4. Keep the SROT app open (or recently open) during the demo. Alerts are checked on the phone.

## E. Demo script (about 5 minutes)

1. **The idea:** "We can't put sensors in every pipe. SROT uses a few cheap sensors plus the physics of water flow to find leaks."
2. **Normal:** home tap open, small tap closed. The app shows the monitor as **Normal**, Flow in **0 L/min**.
3. **Make a leak:** open the small tap a little. Flow in shows the water leaking (L/min), updating live.
4. **Detection:** "Nobody is using water, but it keeps flowing. That is a leak." After 1 minute the phone gets a **Water running nonstop** notification.
5. **Alert:** open it. Show what happened and **What to do**.
6. **Fix it:** close the small tap. Flow returns to 0 and the alert moves to Resolved.
7. **Full system:** **Add → Try demo monitors** shows what more sensors add: pipe-burst location between two monitors, water quality, and tank and pump monitoring.

## F. If something goes wrong

| Problem | Fix |
|---|---|
| Can't see the SROT-xxxxxx Wi-Fi | Hold the ESP32's BOOT button 3 s, wait for the slow blink |
| "Monitor not found" during setup | Mobile data off, stay connected to SROT-xxxxxx, try Continue again |
| Light keeps blinking fast | Wrong Wi-Fi password or a 5 GHz network. Hold BOOT 3 s and set up again |
| Monitor shows Offline in the app | Phone and monitor must be on the same Wi-Fi |
| Flow stays 0 with water running | Check the yellow wire → 10k → GPIO 27 and the 20k to GND. Check the arrow direction. Open the small tap more (needs over about 1 L/min) |
| No notification | Settings → Send test notification. If blocked: Android Settings → Apps → SROT → Notifications → on |

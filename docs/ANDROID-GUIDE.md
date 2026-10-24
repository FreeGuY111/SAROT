# Using SROT on an Android phone

There are three ways to run the app. Most people should start with A.

| | What it is | Needs |
|---|---|---|
| **A. Expo Go (quickest)** | The app runs inside the free Expo Go app, loaded from your PC | PC and phone on the same Wi-Fi, PC running |
| **B. Installable APK** | A normal app icon on the phone that works without the PC | A free Expo account; a cloud build takes ~15 min |
| **C. Real hardware** | The phone talks to a real ESP32 monitor | A monitor flashed with the SROT firmware |

---

## One-time PC setup (needed for A)

The phone has to connect to your PC over Wi-Fi. Windows blocks this on networks marked **Public**.

1. **Mark your Wi-Fi as Private:** Settings → Network & Internet → Wi-Fi → click your network → **Network profile type: Private**.
2. **Allow the SROT ports:** open **PowerShell as Administrator** and run:

```powershell
New-NetFirewallRule -DisplayName "SROT dev (Expo + demo monitors)" -Direction Inbound -Protocol TCP -LocalPort 8081,9000-9011 -Action Allow -Profile Private
```

If Windows instead pops up *"Allow Node.js to communicate…"*, tick **Private networks** and press **Allow**.

Undo later with `Remove-NetFirewallRule -DisplayName "SROT dev (Expo + demo monitors)"`.

---

## A. Run with Expo Go (5 minutes)

1. On the phone, install **Expo Go** from the Play Store.
2. Connect the phone to the **same Wi-Fi** as the PC.
3. On the PC, double-click **`run-demo.bat`** in the repository root (run `npm install` in `mobile/` once first). Two windows open:
   - **SROT demo monitors**: prints a line such as `4 devices on 192.168.1.14`. Note that address.
   - **The app server**: after about a minute it shows a large **QR code**.
4. In Expo Go, tap **Scan QR code** and scan it. The first load takes 1–2 minutes; after that it is fast.
5. In the app, tap **Add** (top right) → **Demo monitors on a PC** → type the address from step 3 (e.g. `192.168.1.14`) → **Add demo monitors**.
6. You will see four monitors. A simulated **pipe burst** happens about every 2 minutes. An urgent bar appears at the bottom; tap **View**, then **Calculate location** with pipe length **600** and material **uPVC**. The demo-monitors window prints the true burst position so you can compare.

**If the QR code does not load in Expo Go:** in the app-server window press **Ctrl+C**, then run the following command and scan the new QR code:

```bash
cd mobile && npx expo start --tunnel
```

Tunnel mode works through any network. The demo monitors still need the firewall step above.

---

## B. Install as a real app (APK)

1. Create a free account at **expo.dev**.
2. Build the APK in the cloud from the `mobile/` folder (first log in, then build):

```bash
npx eas-cli@latest login
```

```bash
npx eas-cli@latest build -p android --profile preview
```

3. When the build finishes (~10–20 min), it prints a **download link and QR code**. Open the link on the phone and download the `.apk`.
4. Tap the file. Android asks you to **allow installing from this source**; allow it, then tap **Install**.
5. Open **SROT** from the app drawer. It no longer needs the PC (the demo monitors still do, if you use them).

---

## C. Use with a real SROT monitor

1. Flash the firmware (see `firmware/README.md`). A new monitor creates a Wi-Fi network named **SROT-xxxxxx**, and its blue light blinks slowly.
2. In the app: **Add → Set up a new monitor**, then follow the 4 steps on screen:
   - **Turn mobile data OFF** first. Android sends app traffic over mobile data when a Wi-Fi network has no internet.
   - Join **SROT-xxxxxx** (password `srot1234`) in Wi-Fi settings, then tap **Continue**.
   - Choose your Wi-Fi, enter its password, give the monitor a place name and choose its type.
   - When it says *connected*, switch the phone back to your normal Wi-Fi and tap **View monitor**.
3. Open the monitor → **Calibrate sensors** and do the pressure zero (and pH or flow, if fitted).
4. **Testing without sensors?** Tick **Demo mode** during setup. A bare ESP32 then produces realistic data, including bursts.

**Monitor already set up and lost?** Use **Add → Find monitors on this Wi-Fi**, or hold the monitor's BOOT button for 3 s to reopen its setup Wi-Fi.

---

## Everyday use

| Screen | What you do there |
|---|---|
| **Home** | See all monitors. The top strip shows how many are Normal, Need attention or Offline. Tap a monitor for details. |
| **Monitor** | The status sentence at the top tells you whether anything is wrong. Readings show the safe range under each value. *Manage* has calibration and settings. |
| **Alerts** | Problems, newest first. Light-blue rows are unread. Each one says **what to do**. |
| **Settings** | Notifications, language (English/हिंदी), pressure unit, alert limits, and how-to steps. |

## Notifications

- On first start the phone asks **"Allow SROT to send notifications?"**. Tap **Allow**.
- Alerts arrive in the **notification bar**, like any other app. Tapping one opens that monitor, or the burst event.
- There are three types, which you can control under Android Settings → Apps → SROT → Notifications:
  - **Urgent**: bursts and dirty water. Plays a sound and vibrates.
  - **Important**: water loss and pressure problems.
  - **Info**: monitor offline, sensor faults.
- In the app, **Settings → Notifications** chooses between *Urgent and important* (default), *All*, or *Off*. Use **Send test notification** to check that they work.
- The phone checks for alerts while the app is open or recently in the background. Alerts with the app fully closed need the SROT server (the next phase), which sends push notifications.

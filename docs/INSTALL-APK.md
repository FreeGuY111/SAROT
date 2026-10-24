# Install SROT on an Android phone (APK)

The APK is a normal Android app. It works on its own: no PC, no Expo Go.

## 1. Download it on the phone

Open the build link on your phone (or scan its QR code). Tap **Install** (or **Download**) to get the `.apk` file.

You can also find every build under **Projects → srot → Builds** on expo.dev after logging in on the phone.

## 2. Install

1. Tap the downloaded file (or open **Files → Download → the .apk**).
2. Android asks to allow installing apps from this source. Tap **Settings**, turn on **Allow from this source**, then go back.
3. Tap **Install**, then **Open**.
4. If *Play Protect* warns about an unknown app, tap **More details → Install anyway**. The warning appears because the app is not from the Play Store.

## 3. First start

1. Tap **Allow** when it asks to send notifications.
2. Choose how to begin:
   - **Try demo:** four sample monitors that run inside the app. A pipe burst happens about every 2 minutes and shows up as a notification.
   - **Set up new monitor:** for a real ESP32 monitor. Follow the steps on screen (mobile data off, join the `SROT-xxxxxx` Wi-Fi, enter your Wi-Fi password).
   - **Find monitors on Wi-Fi:** for monitors that are already set up.

## Building a new version

You need a free Expo account. The first time, run `eas-login.bat` (or `npx eas-cli login` in `mobile/`). Because `mobile/app.json` is tied to the original author's Expo project, run `npx eas-cli init` first to link your own, or edit the `owner` and `extra.eas.projectId` fields.

Then double-click **`cloud-build.bat`**. It uploads the app code (under 1 MB) to Expo's servers, and after 10–30 minutes prints a download link. Install it over the old app; your monitors and settings are kept.

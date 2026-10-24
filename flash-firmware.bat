@echo off
rem Uploads the firmware to an ESP32 connected by USB. Needs PlatformIO (pip install platformio).
title SROT - flash firmware
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\flash.ps1"
echo.
if errorlevel 1 (
  echo  Upload did not finish. Read the message above.
  echo  Tip: hold the BOOT button while it says "Connecting...", release when "Writing" starts.
) else (
  echo  Done. Unplug the ESP32 and power it from a power bank.
  echo  The blue light blinks slowly when it is ready to be set up from the app.
)
pause

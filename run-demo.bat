@echo off
rem Starts the demo monitors (PC emulator) and the Expo dev server.
rem Then open Expo Go on an Android phone and scan the QR code.
title SROT demo
cd /d "%~dp0"
if exist "%~dp0.tools\npm-cache" set npm_config_cache=%~dp0.tools\npm-cache
set EXPO_NO_TELEMETRY=1

echo.
echo  [1/2] Starting the demo monitors in a new window...
start "SROT demo monitors" cmd /k node "%~dp0devsim\device-emulator.mjs"

echo  [2/2] Starting the Expo server. When the QR code appears,
echo        open Expo Go on the phone and tap "Scan QR code".
echo.
cd /d "%~dp0mobile"
call npx expo start --lan

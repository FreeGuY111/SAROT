@echo off
rem Builds an APK on Expo's servers (log in first with eas-login.bat).
rem Prints a download link when the build finishes.
title SROT - cloud APK build
if exist "%~dp0.tools\npm-cache" set npm_config_cache=%~dp0.tools\npm-cache
set EAS_NO_VCS=1
cd /d "%~dp0mobile"
if exist "%~dp0.tools\eas\node_modules\.bin\eas.cmd" (
  call "%~dp0.tools\eas\node_modules\.bin\eas.cmd" build -p android --profile preview
) else (
  call npx eas-cli@latest build -p android --profile preview
)
pause

@echo off
rem Logs in to your Expo account (needed once before cloud-build.bat).
title SROT - Expo login
if exist "%~dp0.tools\npm-cache" set npm_config_cache=%~dp0.tools\npm-cache
cd /d "%~dp0mobile"
echo.
echo  Enter your expo.dev email or username and password below.
echo  The password is not shown while you type.
echo.
if exist "%~dp0.tools\eas\node_modules\.bin\eas.cmd" (
  call "%~dp0.tools\eas\node_modules\.bin\eas.cmd" login
  echo.
  call "%~dp0.tools\eas\node_modules\.bin\eas.cmd" whoami
) else (
  call npx eas-cli@latest login
  echo.
  call npx eas-cli@latest whoami
)
echo.
echo  If your username is shown above, you are logged in.
pause

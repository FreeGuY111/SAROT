# Uploads the firmware to an ESP32 over USB (Windows). Needs PlatformIO: pip install platformio
# Only picks the board's own USB-serial port (CP210x, CH340, FTDI, ESP32-S3 USB), never other COM ports.
#
# Optional local overrides, used only if the folders exist (.tools is not tracked by git):
#   .tools\pio-venv         a PlatformIO virtualenv
#   .tools\.platformio      PlatformIO core dir
#   .tools\win-roots.pem    CA bundle for networks that intercept TLS
$root = Split-Path $PSScriptRoot -Parent
$tools = Join-Path $root '.tools'

if (Test-Path "$tools\.platformio") { $env:PLATFORMIO_CORE_DIR = "$tools\.platformio" }
if (Test-Path "$tools\win-roots.pem") {
  $env:REQUESTS_CA_BUNDLE = "$tools\win-roots.pem"
  $env:SSL_CERT_FILE = $env:REQUESTS_CA_BUNDLE
}
$pio = if (Test-Path "$tools\pio-venv\Scripts\pio.exe") { "$tools\pio-venv\Scripts\pio.exe" } else { 'pio' }

$ports = Get-CimInstance Win32_PnPEntity | Where-Object {
  $_.Name -match '\(COM\d+\)' -and ($_.Name -match 'CP210|CH340|CH341|CH910|USB-SERIAL|USB Serial|UART|FTDI' -or $_.PNPDeviceID -match 'VID_10C4|VID_1A86|VID_0403|VID_303A')
}
if (-not $ports) {
  Write-Output ''
  Write-Output ' No ESP32 found.'
  Write-Output ''
  Write-Output ' 1. Plug the board in with a USB data cable.'
  Write-Output ' 2. Install the USB driver for its chip if Windows lists it under "Other devices":'
  Write-Output '    CP210x (silabs.com) or CH340 (wch-ic.com).'
  Write-Output ' 3. Run this again.'
  exit 1
}
$name = @($ports)[0].Name
$port = [regex]::Match($name, 'COM\d+').Value
Write-Output ''
Write-Output " ESP32 found: $name"
Write-Output ' If it stays on "Connecting....", hold the BOOT button until "Writing" appears.'
Write-Output ''
Set-Location (Join-Path $root 'firmware')
& $pio run -t upload --upload-port $port
exit $LASTEXITCODE

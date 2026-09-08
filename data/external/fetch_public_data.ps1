$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$url = "https://archive.ics.uci.edu/static/public/198/steel+plates+faults.zip"
Invoke-WebRequest -Uri $url -OutFile (Join-Path $root "steel_plates_faults.zip")
Write-Host "EXTERNAL_DATA_REFRESH=PASS"

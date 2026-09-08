$ErrorActionPreference = "Stop"
Write-Host "Manufacturing Quality Intelligence Enterprise Acceptance"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
if (-not (Test-Path ".venv\Scripts\python.exe")) { py -3 -m venv .venv }
$python = ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -e ".[dev]"
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "MQI regression failed" }
& $python scripts/portfolio_validation.py
if ($LASTEXITCODE -ne 0) { throw "MQI portfolio validation failed" }
& $python scripts/enterprise_operability.py
if ($LASTEXITCODE -ne 0) { throw "MQI enterprise operability failed" }
Write-Host "MQI_ENTERPRISE_ACCEPTANCE=PASS"

# Run P8 replay smoke test. Use this when "python" is not in PATH.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$py = $null
if (Test-Path ".venv\Scripts\python.exe") { $py = ".venv\Scripts\python.exe" }
elseif (Test-Path "venv\Scripts\python.exe") { $py = "venv\Scripts\python.exe" }
else {
    try { $py = (Get-Command py -ErrorAction Stop).Source }
    catch { }
}
if (-not $py) {
    Write-Host "No Python found. Create a venv first: py -3 -m venv .venv" -ForegroundColor Red
    exit 1
}
& $py scripts\smoke_p8_replay.py
exit $LASTEXITCODE

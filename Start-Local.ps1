# Start the laptop application in this terminal. Existing .env secrets/data are preserved.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'

$candidates = @()
if ($env:SIGNAL_DAILY_PYTHON) {
    $candidates += @{ Path = $env:SIGNAL_DAILY_PYTHON; Args = @() }
}
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand -and $pythonCommand.Source -notlike '*\WindowsApps\*') {
    $candidates += @{ Path = $pythonCommand.Source; Args = @() }
}
$pyCommand = Get-Command py -ErrorAction SilentlyContinue
if ($pyCommand) { $candidates += @{ Path = $pyCommand.Source; Args = @('-3') } }
$bundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundled) { $candidates += @{ Path = $bundled; Args = @() } }

$selected = $null
foreach ($candidate in $candidates) {
    try {
        $prefixArgs = $candidate.Args
        & $candidate.Path @prefixArgs -c 'import sys; assert sys.version_info >= (3, 11)' 2>$null
        if ($LASTEXITCODE -eq 0) { $selected = $candidate; break }
    } catch { continue }
}
if (-not $selected) {
    throw 'Python 3.11+ was not found. Install Python or set SIGNAL_DAILY_PYTHON to its executable.'
}

$overrides = @{
    HOST = '127.0.0.1'; PORT = '8787'; APP_ENV = 'development'
    PUBLIC_URL = 'http://localhost:8787'; EMAIL_DELIVERY_ENABLED = 'false'
    ENABLE_LOCAL_GENERATION = 'true'
}
$previous = @{}
foreach ($key in $overrides.Keys) {
    $previous[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
    [Environment]::SetEnvironmentVariable($key, $overrides[$key], 'Process')
}
Push-Location -LiteralPath $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.env')) {
        $prefixArgs = $selected.Args
        & $selected.Path @prefixArgs tools/setup_local.py
        if ($LASTEXITCODE -ne 0) { throw 'Local configuration setup failed.' }
    }
    Write-Host 'Signal Daily: http://localhost:8787 | Editor: http://localhost:8787/admin'
    Write-Host 'Loopback only. Email disabled. Leave this terminal open; Ctrl+C stops the server.'
    $prefixArgs = $selected.Args
    & $selected.Path @prefixArgs -u run.py
    if ($LASTEXITCODE -ne 0) { throw 'Signal Daily stopped with an error. Check whether it is already running.' }
} finally {
    Pop-Location
    foreach ($key in $overrides.Keys) {
        [Environment]::SetEnvironmentVariable($key, $previous[$key], 'Process')
    }
}

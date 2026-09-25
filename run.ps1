<#
.SYNOPSIS
    Set up (on first run) and start the backend and frontend dev servers.

.DESCRIPTION
    Creates the Python venv, installs dependencies, copies the .env examples,
    applies migrations and seeds roles, then starts Django on :8000 in a new
    window and Next.js on :3000 in this one.

    PostgreSQL must already be running with the database from backend/.env.

.PARAMETER Setup
    Reinstall backend and frontend dependencies even if they are present.

.EXAMPLE
    .\run.ps1
    .\run.ps1 -Setup
#>
param([switch]$Setup)

$ErrorActionPreference = 'Stop'

$backend  = Join-Path $PSScriptRoot 'backend'
$frontend = Join-Path $PSScriptRoot 'frontend'
$python   = Join-Path $backend '.venv\Scripts\python.exe'

# Native commands do not throw on a non-zero exit code in Windows PowerShell.
function Invoke-Checked {
    param([string]$File, [string[]]$Arguments)
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "'$File $Arguments' failed with exit code $LASTEXITCODE"
    }
}

# Exits 0 when the interpreter meets requires-python in backend/pyproject.toml.
$versionCheck = 'import sys; sys.exit(sys.version_info < (3, 12))'

# Returns the command (plus leading args) that runs a Python 3.12+, preferring
# the py launcher because plain `python` is often an older install.
function Find-Python {
    if (Get-Command 'py' -ErrorAction SilentlyContinue) {
        foreach ($version in '-3.13', '-3.12') {
            & py $version -c $versionCheck 2>$null
            if ($LASTEXITCODE -eq 0) { return @('py', $version) }
        }
    }
    if (Get-Command 'python' -ErrorAction SilentlyContinue) {
        & python -c $versionCheck 2>$null
        if ($LASTEXITCODE -eq 0) { return @('python') }
    }
    throw "Python 3.12+ was not found. Install it from https://www.python.org/downloads/."
}

if (-not (Get-Command 'npm' -ErrorAction SilentlyContinue)) {
    throw "'npm' was not found on PATH. See the prerequisites in README.md."
}

# --- Backend ----------------------------------------------------------------
Write-Host "==> Backend" -ForegroundColor Cyan
Push-Location $backend
try {
    $installBackend = $Setup
    if (Test-Path $python) {
        & $python -c $versionCheck 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "backend\.venv uses Python older than 3.12, recreating it" -ForegroundColor Yellow
            Remove-Item '.venv' -Recurse -Force
        }
    }
    if (-not (Test-Path $python)) {
        $base = @(Find-Python)
        $baseArgs = @($base | Select-Object -Skip 1) + @('-m', 'venv', '.venv')
        Invoke-Checked $base[0] $baseArgs
        $installBackend = $true
    }
    if ($installBackend) {
        Invoke-Checked $python @('-m', 'pip', 'install', '-e', '.[dev]')
    }

    if (-not (Test-Path '.env')) {
        Copy-Item '.env.example' '.env'
        Write-Host "Created backend\.env from .env.example" -ForegroundColor Yellow
    }

    # Fail fast instead of letting Django hang on an unreachable database.
    $dbLine = Select-String -Path '.env' -Pattern '^\s*DATABASE_URL\s*=\s*(.+)$' | Select-Object -First 1
    if ($dbLine) {
        $dbUri = [Uri]$dbLine.Matches[0].Groups[1].Value.Trim()
        $dbPort = if ($dbUri.Port -gt 0) { $dbUri.Port } else { 5432 }
        $tcp = New-Object System.Net.Sockets.TcpClient
        try {
            $reachable = $tcp.ConnectAsync($dbUri.Host, $dbPort).Wait(3000)
        }
        catch {
            $reachable = $false
        }
        finally {
            $tcp.Dispose()
        }
        if (-not $reachable) {
            throw "PostgreSQL is not reachable at $($dbUri.Host):$dbPort. Start it (see step 1 in README.md) or fix DATABASE_URL in backend\.env."
        }
    }

    $migrations = Get-ChildItem 'apps\*\migrations\*.py' | Where-Object Name -ne '__init__.py'
    if (-not $migrations) {
        Invoke-Checked $python @('manage.py', 'makemigrations')
    }
    Invoke-Checked $python @('manage.py', 'migrate')
    Invoke-Checked $python @('manage.py', 'seed_roles')
}
finally {
    Pop-Location
}

# --- Frontend ---------------------------------------------------------------
Write-Host "==> Frontend" -ForegroundColor Cyan
Push-Location $frontend
try {
    if ($Setup -or -not (Test-Path 'node_modules')) {
        Invoke-Checked 'npm' @('install')
    }
    if (-not (Test-Path '.env.local')) {
        Copy-Item '.env.example' '.env.local'
        Write-Host "Created frontend\.env.local from .env.example" -ForegroundColor Yellow
    }
}
finally {
    Pop-Location
}

# --- Start ------------------------------------------------------------------
Write-Host "==> Starting Django on http://localhost:8000 (new window)" -ForegroundColor Cyan
Start-Process powershell -WorkingDirectory $backend `
    -ArgumentList "-NoExit -Command & '$python' manage.py runserver"

Write-Host "==> Starting Next.js on http://localhost:3000 (Ctrl+C to stop)" -ForegroundColor Cyan
Push-Location $frontend
try {
    & npm run dev
}
finally {
    Pop-Location
}

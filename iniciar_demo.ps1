# ============================================================
#  AvoLote - Arranque de la demo con un clic
#  Uso:  clic derecho > "Ejecutar con PowerShell"
#        o en terminal:  powershell -ExecutionPolicy Bypass -File .\iniciar_demo.ps1
# ============================================================
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $raiz 'backend'
$frontend = Join-Path $raiz 'frontend'
$python = Join-Path $backend 'venv\Scripts\python.exe'

Write-Host "`n[AvoLote] Preparando la demo..." -ForegroundColor Green

# 1) Entorno Python (solo la primera vez)
if (-not (Test-Path $python)) {
    Write-Host "Creando entorno virtual e instalando dependencias de Django..." -ForegroundColor Yellow
    python -m venv (Join-Path $backend 'venv')
    & $python -m pip install -q -r (Join-Path $backend 'requirements.txt')
}

# 2) Dependencias de Angular (solo la primera vez)
if (-not (Test-Path (Join-Path $frontend 'node_modules'))) {
    Write-Host "Instalando dependencias de Angular (npm install)..." -ForegroundColor Yellow
    Push-Location $frontend; npm install; Pop-Location
}

# 3) Liberar puertos 8000 / 4200 si quedaron ocupados
foreach ($puerto in 8000, 4200) {
    Get-NetTCPConnection -LocalPort $puerto -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

# 4) Base de datos en estado demo (usuarios + 9 lotes, stock inicial, sin apartados)
Write-Host "Reiniciando base de datos demo..." -ForegroundColor Yellow
Push-Location $backend; & $python manage.py init_demo; Pop-Location

# 5) Levantar servidores en ventanas separadas
Start-Process powershell -ArgumentList '-NoExit', '-Command', "Set-Location '$backend'; & '$python' manage.py runserver 8000"
Start-Process powershell -ArgumentList '-NoExit', '-Command', "Set-Location '$frontend'; npx ng serve --port 4200"

Write-Host "`nEsperando a que Angular compile..." -ForegroundColor Yellow
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 2
    try { Invoke-WebRequest 'http://localhost:4200' -UseBasicParsing -TimeoutSec 2 | Out-Null; break } catch {}
}

Start-Process 'http://localhost:4200'
Write-Host "`n[OK] Frontend http://localhost:4200   |   API http://localhost:8000/api" -ForegroundColor Green
Write-Host "   Admin:   admin@sena.edu.co / admin123"
Write-Host "   Cliente: cliente@sena.edu.co / cliente123`n"

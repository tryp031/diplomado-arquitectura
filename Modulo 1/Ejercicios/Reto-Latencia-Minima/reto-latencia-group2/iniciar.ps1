# iniciar.ps1 — arranca el proyecto en Windows.
#
# Este archivo NO duplica la logica de iniciar.sh: es un lanzador. Todo lo que
# decide algo (que falta, que se puede correr) vive en doctor.py y servidor.py,
# en Python, que corre igual en los tres sistemas. Dos implementaciones de la
# misma comprobacion divergen; en este proyecto ya paso una vez.
#
#   .\iniciar.ps1           arranca en el puerto 8080
#   .\iniciar.ps1 8081      arranca en otro puerto
#   .\iniciar.ps1 -Doctor   solo diagnostica esta maquina

param(
    [int]$Puerto = 8080,
    [switch]$Doctor
)

$ErrorActionPreference = "Stop"
$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── Encontrar un Python usable ───────────────────────────────────────────────
# `py` es el lanzador oficial de Windows y es el que acierta cuando hay varias
# versiones instaladas. `python` a secas en Windows 10/11 puede ser el alias de
# la Microsoft Store, que abre la tienda en vez de ejecutar nada: por eso se
# comprueba que responda de verdad antes de darlo por bueno.
$Python = $null
foreach ($cand in @(@("py", "-3"), @("python3"), @("python"))) {
    $exe = $cand[0]
    if (Get-Command $exe -ErrorAction SilentlyContinue) {
        try {
            $args = @($cand[1..($cand.Length - 1)]) + @("-c", "import sys; print(sys.version_info[:2])")
            $salida = & $exe @args 2>$null
            if ($LASTEXITCODE -eq 0 -and $salida) { $Python = $cand; break }
        } catch { }
    }
}

if (-not $Python) {
    Write-Host ""
    Write-Host "  No encontre Python 3 en esta maquina." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Instalalo desde https://www.python.org/downloads/"
    Write-Host "  IMPORTANTE: marca la casilla «Add python.exe to PATH» al instalar."
    Write-Host ""
    Read-Host "  Enter para cerrar"
    exit 1
}

function Invoke-Py {
    param([string[]]$Argumentos)
    $exe = $Python[0]
    $pre = @($Python[1..($Python.Length - 1)])
    & $exe @($pre + $Argumentos)
}

# ── Diagnostico ──────────────────────────────────────────────────────────────
if ($Doctor) {
    Invoke-Py @((Join-Path $Aqui "doctor.py"))
    Read-Host "`n  Enter para cerrar"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "  Reto de Latencia Minima - Group 2" -ForegroundColor Cyan
Write-Host ""

# ── Compilar las variantes en C, si esta maquina puede ───────────────────────
if (Get-Command make -ErrorAction SilentlyContinue) {
    Write-Host "  Compilando las variantes en C..."
    Get-ChildItem -Path (Join-Path $Aqui "sistema") -Directory | ForEach-Object {
        if (Test-Path (Join-Path $_.FullName "Makefile")) {
            & make -C $_.FullName *> $null
            if ($LASTEXITCODE -eq 0) { Write-Host "    $($_.Name) ok" }
        }
    }
} else {
    # Escenario previsto, no un fallo: ver README, «Tres caminos».
    Write-Host "  Sin compilador de C: camino Windows nativo." -ForegroundColor Yellow
    Write-Host "  Funcionan la interfaz y las variantes en Python (B, y A y C cuando esten)."
    Write-Host "  Las variantes en C y la medicion oficial necesitan WSL2:  wsl --install"
}

Write-Host ""
Write-Host "  Abriendo http://127.0.0.1:$Puerto"
Write-Host "  Ctrl-C para bajar todo."
Write-Host ""

Start-Job -ScriptBlock {
    param($u)
    Start-Sleep -Seconds 2
    Start-Process $u
} -ArgumentList "http://127.0.0.1:$Puerto" | Out-Null

Invoke-Py @((Join-Path $Aqui "app\servidor.py"), "--puerto", "$Puerto")

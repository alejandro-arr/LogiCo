param(
    [string]$SonarHostUrl = "http://localhost:9000",
    [string]$ProjectKey = "logico",
    [string]$ProjectName = "LogiCo"
)

$ErrorActionPreference = "Stop"

if (-not $env:SONAR_TOKEN) {
    Write-Error "Define SONAR_TOKEN antes de ejecutar. Ejemplo: `$env:SONAR_TOKEN='tu_token'"
}

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Pysonar = Join-Path $ProjectRoot "venv\Scripts\pysonar.exe"

if (-not (Test-Path $Pysonar)) {
    Write-Error "No se encontro pysonar en venv. Ejecuta: .\venv\Scripts\python.exe -m pip install -r requirements.txt"
}

& $Pysonar `
    --sonar-host-url=$SonarHostUrl `
    --sonar-token $env:SONAR_TOKEN `
    --sonar-project-key=$ProjectKey `
    --sonar-project-name=$ProjectName `
    --sonar-sources=app_movimientos,proyecto_logico,manage.py `
    --sonar-python-version=3.12 `
    --sonar-source-encoding=UTF-8

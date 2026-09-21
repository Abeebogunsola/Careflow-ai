<#
.SYNOPSIS
    CareFlow AI — Local Development Service Status Script.
.DESCRIPTION
    Checks whether Docker is running and inspects the current status, ports,
    and health of the local development containers (PostgreSQL and n8n).
.NOTES
    Safe to run repeatedly at any time.
#>

[CmdletBinding()]
param()

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "       CareFlow AI — Local Development Service Status       " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Step 1: Check Docker availability
# -----------------------------------------------------------------------------
$dockerCmd = Get-Command "docker" -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "[ERROR] Docker CLI was not found in PATH." -ForegroundColor Red
    exit 1
}

# Verify Docker daemon is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[STATUS] Docker Desktop daemon is currently stopped." -ForegroundColor Red
    Write-Host "Start Docker Desktop to use containerized local services." -ForegroundColor Yellow
    exit 0
}

# -----------------------------------------------------------------------------
# Step 2: Query Docker Compose service states
# -----------------------------------------------------------------------------
Write-Host "`nLocal Container Status (docker-compose.yml):" -ForegroundColor Yellow
docker compose -f docker-compose.yml ps

# -----------------------------------------------------------------------------
# Step 3: Inspect specific container health and display endpoints
# -----------------------------------------------------------------------------
$pgStatus = docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' careflow-postgres 2>$null
$n8nStatus = docker inspect --format '{{.State.Status}}' careflow-n8n 2>$null

Write-Host "`nService Health Summary:" -ForegroundColor White
if ($pgStatus -eq "healthy") {
    Write-Host "  * PostgreSQL Database : RUNNING & HEALTHY (localhost:5432)" -ForegroundColor Green
} elseif ($pgStatus) {
    Write-Host "  * PostgreSQL Database : $pgStatus" -ForegroundColor Yellow
} else {
    Write-Host "  * PostgreSQL Database : STOPPED" -ForegroundColor DarkGray
}

if ($n8nStatus -eq "running") {
    Write-Host "  * n8n Workflow Engine : RUNNING (http://localhost:5678)" -ForegroundColor Green
} elseif ($n8nStatus) {
    Write-Host "  * n8n Workflow Engine : $n8nStatus" -ForegroundColor Yellow
} else {
    Write-Host "  * n8n Workflow Engine : STOPPED" -ForegroundColor DarkGray
}

Write-Host "`nQuick Actions:" -ForegroundColor White
Write-Host "  * Start services : .\start.ps1" -ForegroundColor Cyan
Write-Host "  * Stop services  : .\stop.ps1" -ForegroundColor Cyan
Write-Host ""

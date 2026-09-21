<#
.SYNOPSIS
    CareFlow AI — Local Development Shutdown Script.
.DESCRIPTION
    Cleanly stops the local background containers (careflow-postgres and careflow-n8n)
    without removing persistent volumes or deleting local PostgreSQL database records.
    Safe to run repeatedly.
.NOTES
    Important: This command runs 'docker compose down' without the '-v' flag.
    Omitting '-v' guarantees that the PostgreSQL data volume (careflow_postgres_data)
    and n8n workflow storage (careflow_n8n_data) are preserved intact.
#>

[CmdletBinding()]
param()

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "       CareFlow AI — Stopping Local Development Services    " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Step 1: Verify that Docker CLI is available
# -----------------------------------------------------------------------------
$dockerCmd = Get-Command "docker" -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "[ERROR] Docker CLI was not found in PATH." -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# Step 2: Stop and remove local development containers
# Note: 'docker compose down' removes containers and the local bridge network,
# but PRESERVES all named volumes (your database data is completely safe).
# Never pass '-v' here if you want to keep your development records.
# -----------------------------------------------------------------------------
Write-Host "`nStopping local containers (docker-compose.yml)..." -ForegroundColor Yellow

# Stop services cleanly using the local compose file
docker compose -f docker-compose.yml down

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Local development services stopped cleanly." -ForegroundColor Green
    Write-Host "Persistent data volumes (PostgreSQL database and n8n storage) remain preserved." -ForegroundColor Cyan
    Write-Host "To restart local services at any time, run: .\start.ps1" -ForegroundColor Gray
} else {
    Write-Host "`n[WARNING] 'docker compose down' returned code $LASTEXITCODE." -ForegroundColor Yellow
}
Write-Host ""

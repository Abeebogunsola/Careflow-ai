<#
.SYNOPSIS
    CareFlow AI — Local Development Startup Script.
.DESCRIPTION
    Verifies Docker availability, starts the required local background services
    (PostgreSQL 15 and n8n Workflow Engine) using the existing docker-compose.yml,
    waits for health initialization, and outputs service connection details.
    Safe to run repeatedly.
.NOTES
    This script is for LOCAL development and demonstration only.
    It does not modify or start production infrastructure.
#>

[CmdletBinding()]
param()

# Clear screen or print clean startup banner
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "      CareFlow AI — Starting Local Development Services     " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Step 1: Verify that Docker CLI is installed and available in PATH
# -----------------------------------------------------------------------------
Write-Host "`n[1/4] Checking Docker installation..." -ForegroundColor Yellow
$dockerCmd = Get-Command "docker" -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "[ERROR] Docker is not installed or not found in your system PATH." -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows and try again: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}
Write-Host "      Docker CLI detected: $($dockerCmd.Source)" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 2: Verify that the Docker daemon (Docker Desktop) is actively running
# -----------------------------------------------------------------------------
Write-Host "`n[2/4] Verifying Docker daemon status..." -ForegroundColor Yellow
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker daemon is not running." -ForegroundColor Red
    Write-Host "Please start Docker Desktop and wait until it is fully initialized, then re-run this script." -ForegroundColor Red
    exit 1
}
Write-Host "      Docker daemon is active and responsive." -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 3: Start local development services using existing docker-compose.yml
# This starts careflow-postgres (PostgreSQL 15) and careflow-n8n (Workflow Engine).
# -----------------------------------------------------------------------------
Write-Host "`n[3/4] Starting local development containers (docker-compose.yml)..." -ForegroundColor Yellow
# Run docker compose up in detached (-d) mode using the project's local compose file
docker compose -f docker-compose.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start local Docker containers." -ForegroundColor Red
    exit 1
}
Write-Host "      Containers started in detached mode." -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 4: Wait briefly for PostgreSQL healthcheck to report healthy
# -----------------------------------------------------------------------------
Write-Host "`n[4/4] Waiting for PostgreSQL database initialization..." -ForegroundColor Yellow
$maxAttempts = 20
$attempt = 0
$isHealthy = $false

while ($attempt -lt $maxAttempts) {
    # Check container health status via docker inspect
    $healthStatus = docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' careflow-postgres 2>$null
    if ($healthStatus -eq "healthy") {
        $isHealthy = $true
        break
    }
    Start-Sleep -Seconds 1
    $attempt++
    Write-Host -NoNewline "."
}
Write-Host ""

if ($isHealthy) {
    Write-Host "      PostgreSQL database is ready and accepting connections." -ForegroundColor Green
} else {
    Write-Host "      PostgreSQL is still starting up. You may proceed; it will become ready shortly." -ForegroundColor Yellow
}

# -----------------------------------------------------------------------------
# Display Service Connection Details & Next Steps
# -----------------------------------------------------------------------------
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "           Local Services Ready for Development             " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`nActive Background Services:" -ForegroundColor White
Write-Host "  * PostgreSQL 15 Database : localhost:5432 (DB: careflow_db, User: postgres)" -ForegroundColor Green
Write-Host "  * n8n Workflow Automation: http://localhost:5678" -ForegroundColor Green

Write-Host "`nTo Run the Application Locally:" -ForegroundColor White
Write-Host "  1. Backend API (FastAPI):" -ForegroundColor Yellow
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     .\.venv\Scripts\activate     # (or source .venv/bin/activate on bash)" -ForegroundColor Gray
Write-Host "     alembic upgrade head         # (applies database tables if needed)" -ForegroundColor Gray
Write-Host "     uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host "     -> API Root: http://localhost:8000" -ForegroundColor DarkGray
Write-Host "     -> API Docs: http://localhost:8000/api/v1/docs" -ForegroundColor DarkGray

Write-Host "`n  2. Frontend Web UI (React + Vite):" -ForegroundColor Yellow
Write-Host "     cd frontend" -ForegroundColor Gray
Write-Host "     npm run dev" -ForegroundColor Gray
Write-Host "     -> Web Application: http://localhost:5173" -ForegroundColor DarkGray

Write-Host "`nHelpful Commands:" -ForegroundColor White
Write-Host "  * Check container status : .\status.ps1" -ForegroundColor Cyan
Write-Host "  * Stop local containers  : .\stop.ps1" -ForegroundColor Cyan
Write-Host ""

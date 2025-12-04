#!/usr/bin/env pwsh
# Script to run integration tests locally with environment variables

# Check if environment variables are set
if (-not $env:HUCKLEBERRY_EMAIL) {
    Write-Host "ERROR: HUCKLEBERRY_EMAIL environment variable not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Set it with:"
    Write-Host '  $env:HUCKLEBERRY_EMAIL = "your-email@example.com"' -ForegroundColor Yellow
    exit 1
}

if (-not $env:HUCKLEBERRY_PASSWORD) {
    Write-Host "ERROR: HUCKLEBERRY_PASSWORD environment variable not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Set it with:"
    Write-Host '  $env:HUCKLEBERRY_PASSWORD = "your-password"' -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Environment variables set" -ForegroundColor Green
Write-Host "  Email: $env:HUCKLEBERRY_EMAIL" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
try {
    $uvVersion = uv --version
    Write-Host "✓ uv is installed ($uvVersion)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: uv is not installed" -ForegroundColor Red
    Write-Host "Install it from: https://docs.astral.sh/uv/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Cyan
uv sync --dev

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Running integration tests..." -ForegroundColor Cyan
Write-Host ""

uv run pytest tests/ -v

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    exit 1
}

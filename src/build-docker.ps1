# Docker Build and Deployment Script for FastAPI Invoice Generator

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  FastAPI Invoice Generator - Docker Build" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Build the Docker image using docker-compose
Write-Host "Building Docker image..." -ForegroundColor Green
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Docker image built successfully!" -ForegroundColor Green
    
    # Show image info
    Write-Host ""
    Write-Host "Image details:" -ForegroundColor Cyan
    docker images | Select-String "fastapi-invoice-app"
    
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Yellow
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Check docker-compose.yml and comment/uncomment" -ForegroundColor White
    Write-Host "   the API_BASE_URL for your environment:" -ForegroundColor White
    Write-Host "   - Production: https://readapi.accountingonweb.com" -ForegroundColor Cyan
    Write-Host "   - Development: https://localhost:7047" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Start the container:" -ForegroundColor White
    Write-Host "   docker-compose up -d" -ForegroundColor Green
    Write-Host ""
    Write-Host "3. View logs:" -ForegroundColor White
    Write-Host "   docker-compose logs -f" -ForegroundColor Green
    Write-Host ""
    Write-Host "4. Stop the container:" -ForegroundColor White
    Write-Host "   docker-compose down" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✗ Docker build failed!" -ForegroundColor Red
    exit 1
}

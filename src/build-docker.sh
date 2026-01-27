#!/bin/bash

# Docker Build and Deployment Script for FastAPI Invoice Generator

echo "=================================================="
echo "  FastAPI Invoice Generator - Docker Build"
echo "=================================================="
echo ""

# Build the Docker image using docker-compose
echo "Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Docker image built successfully!"
    
    # Show image info
    echo ""
    echo "Image details:"
    docker images | grep "fastapi-invoice-app"
    
    echo ""
    echo "=================================================="
    echo "Next Steps:"
    echo ""
    echo "1. Check docker-compose.yml and comment/uncomment"
    echo "   the API_BASE_URL for your environment:"
    echo "   - Production: https://readapi.accountingonweb.com"
    echo "   - Development: https://localhost:7047"
    echo ""
    echo "2. Start the container:"
    echo "   docker-compose up -d"
    echo ""
    echo "3. View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "4. Stop the container:"
    echo "   docker-compose down"
    echo "=================================================="
else
    echo ""
    echo "✗ Docker build failed!"
    exit 1
fi

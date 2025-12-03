# Docker Hub Push Script
# Usage: .\scripts\push_to_dockerhub.ps1 -Username "your_username" [-Version "v1.0.0"]

param(
    [Parameter(Mandatory = $true)]
    [string]$Username,
    
    [Parameter(Mandatory = $false)]
    [string]$Version = "latest"
)

$ImageName = "app-backend-fastapi"
$LocalImage = "app-backend-fastapi-api:latest"
$line = "=" * 70

Write-Host $line -ForegroundColor Cyan
Write-Host "Docker Hub Push Script" -ForegroundColor Cyan
Write-Host $line -ForegroundColor Cyan
Write-Host ""

# 1. Check local image
Write-Host "[Step 1] Checking local image..." -ForegroundColor Yellow
$localImageExists = docker images $LocalImage -q
if (-not $localImageExists) {
    Write-Host "ERROR: Local image not found: $LocalImage" -ForegroundColor Red
    Write-Host "Build the image first with: docker-compose build" -ForegroundColor Yellow
    exit 1
}

$imageInfo = docker images $LocalImage --format "{{.Size}}"
Write-Host "OK Local image found" -ForegroundColor Green
Write-Host "  Image: $LocalImage" -ForegroundColor Gray
Write-Host "  Size: $imageInfo" -ForegroundColor Gray
Write-Host ""

# 2. Check Docker login
Write-Host "[Step 2] Checking Docker login..." -ForegroundColor Yellow
$loginCheck = docker info 2>&1 | Select-String "Username"
if (-not $loginCheck) {
    Write-Host "WARNING: Not logged in to Docker Hub" -ForegroundColor Yellow
    Write-Host "Attempting to login..." -ForegroundColor Yellow
    docker login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Login failed" -ForegroundColor Red
        exit 1
    }
}
Write-Host "OK Logged in to Docker Hub" -ForegroundColor Green
Write-Host ""

# 3. Tag image
Write-Host "[Step 3] Tagging image..." -ForegroundColor Yellow
$taggedImage = "$Username/$ImageName`:$Version"
docker tag $LocalImage $taggedImage

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Tagged as: $taggedImage" -ForegroundColor Green
}
else {
    Write-Host "ERROR: Failed to tag image" -ForegroundColor Red
    exit 1
}

# Also tag as latest if version is specified
if ($Version -ne "latest") {
    $latestTag = "$Username/$ImageName`:latest"
    docker tag $LocalImage $latestTag
    Write-Host "OK Also tagged as: $latestTag" -ForegroundColor Green
}
Write-Host ""

# 4. Push to Docker Hub
Write-Host "[Step 4] Pushing to Docker Hub..." -ForegroundColor Yellow
Write-Host "This may take several minutes (image size: $imageInfo)..." -ForegroundColor Gray
Write-Host "Please wait..." -ForegroundColor Gray
Write-Host ""

docker push $taggedImage

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "OK Successfully pushed: $taggedImage" -ForegroundColor Green
    
    # Push latest tag if version was specified
    if ($Version -ne "latest") {
        Write-Host ""
        Write-Host "Pushing latest tag..." -ForegroundColor Yellow
        docker push $latestTag
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK Successfully pushed: $latestTag" -ForegroundColor Green
        }
    }
}
else {
    Write-Host ""
    Write-Host "ERROR: Failed to push image" -ForegroundColor Red
    Write-Host "Check your internet connection and Docker Hub credentials" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host $line -ForegroundColor Cyan
Write-Host "SUCCESS! Image pushed to Docker Hub" -ForegroundColor Green
Write-Host $line -ForegroundColor Cyan
Write-Host ""
Write-Host "Image URL:" -ForegroundColor Yellow
Write-Host "  https://hub.docker.com/r/$Username/$ImageName" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pull commands:" -ForegroundColor Yellow
Write-Host "  docker pull $taggedImage" -ForegroundColor Cyan
if ($Version -ne "latest") {
    Write-Host "  docker pull $latestTag" -ForegroundColor Cyan
}
Write-Host ""
Write-Host $line -ForegroundColor Cyan

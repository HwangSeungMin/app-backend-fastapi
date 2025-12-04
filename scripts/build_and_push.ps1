# Elasticsearch 이미지를 빌드하고 Docker Hub에 푸시하는 PowerShell 스크립트

param(
    [string]$DockerUsername = $env:DOCKER_USERNAME
)

$ErrorActionPreference = "Stop"

if (-not $DockerUsername) {
    Write-Host " Docker Hub 사용자명을 입력하세요" -ForegroundColor Red
    Write-Host "사용법: .\build_and_push.ps1 -DockerUsername YOUR_USERNAME"
    Write-Host "또는: `$env:DOCKER_USERNAME='YOUR_USERNAME'; .\build_and_push.ps1"
    exit 1
}

$ImageName = "yakkobak-elasticsearch"
$Tag = "latest"
$FullImageName = "${DockerUsername}/${ImageName}:${Tag}"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Docker Hub에 Elasticsearch 이미지 배포" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " 이미지: ${FullImageName}" -ForegroundColor Yellow
Write-Host ""

# Step 1: 데이터 Export
Write-Host " Step 1/4: Elasticsearch 데이터 export..." -ForegroundColor Green
python scripts\export_es_data.py

if (-not (Test-Path "data\es_data_*.json")) {
    Write-Host " 데이터 export 실패" -ForegroundColor Red
    exit 1
}

Write-Host " 데이터 export 완료" -ForegroundColor Green
Write-Host ""

# Step 2: Docker 이미지 빌드
Write-Host " Step 2/4: Docker 이미지 빌드..." -ForegroundColor Green
docker build -f Dockerfile.elasticsearch.preloaded -t ${FullImageName} .

if ($LASTEXITCODE -ne 0) {
    Write-Host " 이미지 빌드 실패" -ForegroundColor Red
    exit 1
}

Write-Host " 이미지 빌드 완료" -ForegroundColor Green
Write-Host ""

# Step 3: Docker Hub 로그인 확인
Write-Host " Step 3/4: Docker Hub 로그인 확인..." -ForegroundColor Green
$dockerInfo = docker info 2>&1 | Out-String
if ($dockerInfo -notmatch "Username: ${DockerUsername}") {
    Write-Host "  Docker Hub에 로그인되어 있지 않습니다." -ForegroundColor Yellow
    Write-Host "로그인을 진행합니다..." -ForegroundColor Yellow
    docker login
}

Write-Host " Docker Hub 로그인 확인 완료" -ForegroundColor Green
Write-Host ""

# Step 4: Docker Hub에 푸시
Write-Host "  Step 4/4: Docker Hub에 푸시..." -ForegroundColor Green
docker push ${FullImageName}

if ($LASTEXITCODE -ne 0) {
    Write-Host " Docker Hub 푸시 실패" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " 배포 완료!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " 이미지: ${FullImageName}" -ForegroundColor Yellow
Write-Host ""
Write-Host "다른 환경에서 사용하려면:" -ForegroundColor Cyan
Write-Host "  docker pull ${FullImageName}" -ForegroundColor White
Write-Host "  docker run -d -p 9200:9200 -p 9300:9300 ${FullImageName}" -ForegroundColor White
Write-Host ""

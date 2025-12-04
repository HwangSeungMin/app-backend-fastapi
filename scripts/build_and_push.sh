#!/bin/bash
# Elasticsearch 이미지를 빌드하고 Docker Hub에 푸시하는 스크립트

set -e

# Docker Hub 사용자명 (환경변수 또는 인자로 받기)
DOCKER_USERNAME="${DOCKER_USERNAME:-$1}"

if [ -z "$DOCKER_USERNAME" ]; then
    echo "❌ Docker Hub 사용자명을 입력하세요"
    echo "사용법: ./build_and_push.sh <docker-username>"
    echo "또는: DOCKER_USERNAME=<username> ./build_and_push.sh"
    exit 1
fi

IMAGE_NAME="yakkobak-elasticsearch"
TAG="latest"
FULL_IMAGE_NAME="$DOCKER_USERNAME/$IMAGE_NAME:$TAG"

echo "========================================="
echo "🐳 Docker Hub에 Elasticsearch 이미지 배포"
echo "========================================="
echo ""
echo "📦 이미지: $FULL_IMAGE_NAME"
echo ""

# Step 1: 데이터 Export
echo "📤 Step 1/4: Elasticsearch 데이터 export..."
python scripts/export_es_data.py

if [ ! -f data/es_data_*.json ]; then
    echo "❌ 데이터 export 실패"
    exit 1
fi

echo "✅ 데이터 export 완료"
echo ""

# Step 2: Docker 이미지 빌드
echo "🔨 Step 2/4: Docker 이미지 빌드..."
docker build -f Dockerfile.elasticsearch.preloaded -t $FULL_IMAGE_NAME .

echo "✅ 이미지 빌드 완료"
echo ""

# Step 3: Docker Hub 로그인 확인
echo "🔐 Step 3/4: Docker Hub 로그인 확인..."
if ! docker info | grep -q "Username: $DOCKER_USERNAME"; then
    echo "⚠️  Docker Hub에 로그인되어 있지 않습니다."
    echo "로그인을 진행합니다..."
    docker login
fi

echo "✅ Docker Hub 로그인 확인 완료"
echo ""

# Step 4: Docker Hub에 푸시
echo "⬆️  Step 4/4: Docker Hub에 푸시..."
docker push $FULL_IMAGE_NAME

echo ""
echo "========================================="
echo "✅ 배포 완료!"
echo "========================================="
echo ""
echo "📦 이미지: $FULL_IMAGE_NAME"
echo ""
echo "다른 환경에서 사용하려면:"
echo "  docker pull $FULL_IMAGE_NAME"
echo "  docker run -d -p 9200:9200 -p 9300:9300 $FULL_IMAGE_NAME"
echo ""

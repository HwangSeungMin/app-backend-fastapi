#!/bin/bash
# Kibana만 단독으로 실행하는 스크립트 (Linux/Mac)

echo "============================================"
echo "Kibana 단독 실행 스크립트"
echo "============================================"

# Elasticsearch가 실행 중인지 확인
echo "1. Elasticsearch 연결 확인 중..."
if curl -s http://localhost:9200 > /dev/null; then
    echo "✓ Elasticsearch가 실행 중입니다."
    ES_VERSION=$(curl -s http://localhost:9200 | grep -o '"number" : "[^"]*"' | cut -d'"' -f4)
    echo "  버전: $ES_VERSION"
else
    echo "✗ Elasticsearch가 실행되지 않았습니다."
    echo "  먼저 Elasticsearch를 실행해주세요."
    exit 1
fi

# 기존 Kibana 컨테이너 확인
echo ""
echo "2. 기존 Kibana 컨테이너 확인 중..."
if docker ps -a | grep -q health-supplement-kibana; then
    echo "기존 Kibana 컨테이너를 제거합니다..."
    docker rm -f health-supplement-kibana
fi

# Kibana 실행
echo ""
echo "3. Kibana 컨테이너 실행 중..."
docker run -d \
  --name health-supplement-kibana \
  -p 5601:5601 \
  --add-host host.docker.internal:host-gateway \
  -e ELASTICSEARCH_HOSTS=http://host.docker.internal:9200 \
  -e SERVER_NAME=kibana \
  -e SERVER_HOST=0.0.0.0 \
  -e XPACK_SECURITY_ENABLED=false \
  -e I18N_LOCALE=ko-KR \
  docker.elastic.co/kibana/kibana:8.11.0

if [ $? -eq 0 ]; then
    echo "✓ Kibana 컨테이너가 시작되었습니다."
    echo ""
    echo "4. Kibana 초기화 대기 중..."
    echo "   (약 1-2분 소요됩니다. 로그를 확인하세요)"
    echo ""
    echo "============================================"
    echo "Kibana 접속 정보"
    echo "============================================"
    echo "URL: http://localhost:5601"
    echo ""
    echo "로그 확인: docker logs -f health-supplement-kibana"
    echo "중지: docker stop health-supplement-kibana"
    echo "재시작: docker start health-supplement-kibana"
    echo "삭제: docker rm -f health-supplement-kibana"
    echo "============================================"
else
    echo "✗ Kibana 시작에 실패했습니다."
    exit 1
fi

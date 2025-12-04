#!/bin/bash
# Elasticsearch 컨테이너의 entrypoint 스크립트
# 데이터 preload 후 Elasticsearch 시작

set -e

echo "🚀 Elasticsearch with Preloaded Data 시작..."

# Elasticsearch를 백그라운드로 시작
echo "📦 Elasticsearch 시작 중..."
/usr/local/bin/docker-entrypoint.sh elasticsearch &

# Elasticsearch PID 저장
ES_PID=$!

# Elasticsearch가 준비될 때까지 대기
echo "⏳ Elasticsearch 준비 대기 중..."
until curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    sleep 2
done

echo "✅ Elasticsearch 준비 완료"

# 인덱스가 이미 존재하는지 확인
INDEX_NAME="${ES_INDEX_NAME:-health_supplements}"
if curl -s "http://localhost:9200/$INDEX_NAME" > /dev/null 2>&1; then
    echo "ℹ️  인덱스 '$INDEX_NAME'가 이미 존재합니다. Import 생략."
else
    echo "📥 데이터 import 시작..."
    # 데이터 import 스크립트 실행
    bash /usr/share/elasticsearch/scripts/import_es_data.sh
    echo "✅ 데이터 import 완료"
fi

# Elasticsearch 프로세스가 종료될 때까지 대기
echo "🎉 Elasticsearch 실행 중..."
wait $ES_PID

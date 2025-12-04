#!/bin/bash
# Elasticsearch 데이터를 import하는 스크립트
# Docker 컨테이너 시작 시 자동으로 실행됩니다.

set -e

ES_URL="${ES_URL:-http://localhost:9200}"
DATA_FILE="/usr/share/elasticsearch/preload_data/es_data.json"

echo "🔍 Elasticsearch 연결 대기 중..."

# Elasticsearch가 준비될 때까지 대기 (최대 60초)
for i in {1..60}; do
    if curl -s "$ES_URL/_cluster/health" > /dev/null 2>&1; then
        echo "✅ Elasticsearch 연결 성공"
        break
    fi
    echo "⏳ 대기 중... ($i/60)"
    sleep 1
done

# 데이터 파일 존재 확인
if [ ! -f "$DATA_FILE" ]; then
    echo "❌ 데이터 파일이 없습니다: $DATA_FILE"
    exit 1
fi

echo "📦 데이터 파일 발견: $DATA_FILE"

# Python으로 데이터 import
python3 - <<EOF
import json
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# 데이터 파일 읽기
with open('$DATA_FILE', 'r', encoding='utf-8') as f:
    data = json.load(f)

index_name = data['index_name']
settings = data['settings']
mappings = data['mappings']
documents = data['documents']

print(f"📊 인덱스: {index_name}")
print(f"📝 문서 수: {len(documents)}")

# Elasticsearch 클라이언트
es = Elasticsearch(['$ES_URL'])

# 인덱스가 이미 존재하면 삭제
if es.indices.exists(index=index_name):
    print(f"🗑️  기존 인덱스 삭제: {index_name}")
    es.indices.delete(index=index_name)

# 인덱스 생성
print(f"🔨 인덱스 생성: {index_name}")

# settings에서 불필요한 메타데이터 제거
clean_settings = {}
if 'index' in settings:
    for key, value in settings['index'].items():
        # 시스템 생성 필드 제외
        if not key.startswith('provided_name') and \
           not key.startswith('creation_date') and \
           not key.startswith('uuid') and \
           not key.startswith('version'):
            clean_settings[key] = value

es.indices.create(
    index=index_name,
    body={
        'settings': {'index': clean_settings},
        'mappings': mappings
    }
)

# 문서 bulk insert
print(f"📥 문서 import 시작...")

actions = []
for doc in documents:
    actions.append({
        '_index': doc['_index'],
        '_id': doc['_id'],
        '_source': doc['_source']
    })

success, failed = bulk(es, actions, stats_only=True)
print(f"✅ Import 완료: {success}개 성공, {failed}개 실패")

# 인덱스 refresh
es.indices.refresh(index=index_name)

# 최종 확인
count = es.count(index=index_name)['count']
print(f"🎉 최종 문서 수: {count}")
EOF

echo "✅ 데이터 import 완료!"

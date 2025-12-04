"""
Elasticsearch 데이터를 JSON 파일로 export하는 스크립트
Docker 이미지에 포함시킬 데이터를 추출합니다.
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json
import os
from datetime import datetime

# Elasticsearch 설정
ES_HOST = os.getenv('ES_HOST', 'localhost')
ES_PORT = int(os.getenv('ES_PORT', '9200'))
ES_INDEX = os.getenv('ES_INDEX_NAME', 'health_supplements')

def export_index_data():
    """인덱스 데이터를 JSON 파일로 export"""

    # Elasticsearch 클라이언트 생성
    es = Elasticsearch([f'http://{ES_HOST}:{ES_PORT}'])

    # 연결 확인
    if not es.ping():
        print(f"❌ Elasticsearch에 연결할 수 없습니다: {ES_HOST}:{ES_PORT}")
        return False

    print(f"✅ Elasticsearch 연결 성공: {ES_HOST}:{ES_PORT}")

    # 인덱스 존재 확인
    if not es.indices.exists(index=ES_INDEX):
        print(f"❌ 인덱스가 존재하지 않습니다: {ES_INDEX}")
        return False

    print(f"📊 인덱스 '{ES_INDEX}' 데이터 export 시작...")

    # 인덱스 설정 가져오기
    index_settings = es.indices.get_settings(index=ES_INDEX)
    index_mappings = es.indices.get_mapping(index=ES_INDEX)

    # 모든 문서 가져오기
    documents = []
    for doc in scan(es, index=ES_INDEX, query={"query": {"match_all": {}}}):
        documents.append({
            "_index": doc["_index"],
            "_id": doc["_id"],
            "_source": doc["_source"]
        })

    print(f"📝 총 {len(documents)}개 문서 export 완료")

    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)

    # 타임스탬프 추가
    timestamp = datetime.now().strftime('%Y%m%d')

    # JSON 파일로 저장
    export_data = {
        "index_name": ES_INDEX,
        "settings": index_settings[ES_INDEX]["settings"],
        "mappings": index_mappings[ES_INDEX]["mappings"],
        "documents": documents,
        "exported_at": datetime.now().isoformat(),
        "document_count": len(documents)
    }

    output_file = f'data/es_data_{timestamp}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 데이터 export 완료: {output_file}")
    print(f"   - 인덱스: {ES_INDEX}")
    print(f"   - 문서 수: {len(documents)}")
    print(f"   - 파일 크기: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")

    return True

if __name__ == "__main__":
    success = export_index_data()
    exit(0 if success else 1)

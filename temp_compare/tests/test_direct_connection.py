# test_direct_connection.py
from elasticsearch import Elasticsearch
import traceback

def test_connection():
    print("ElasticSearch 직접 연결 테스트")
    print("=" * 60)
    
    try:
        # 연결 생성
        es = Elasticsearch(
            ["http://localhost:9200"],
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
        
        print(f"연결 객체 생성 완료")
        print(f"호스트: http://localhost:9200")
        
        # Ping 테스트
        print("\nPing 테스트 중...")
        result = es.ping()
        print(f"Ping 결과: {result}")
        
        if result:
            # 정보 조회
            print("\nElasticSearch 정보 조회...")
            info = es.info()
            print(f"클러스터명: {info['cluster_name']}")
            print(f"버전: {info['version']['number']}")
            print(f"노드명: {info['name']}")
            
            print("\n✓ 연결 성공!")
            return True
        else:
            print("\n✗ Ping 실패")
            return False
            
    except Exception as e:
        print(f"\n✗ 연결 오류 발생")
        print(f"오류 타입: {type(e).__name__}")
        print(f"오류 메시지: {str(e)}")
        print("\n상세 오류:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection()
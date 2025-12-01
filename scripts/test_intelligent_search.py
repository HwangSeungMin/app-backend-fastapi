"""
지능형 검색 API 간단 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_intelligent_search():
    """지능형 검색 테스트"""
    
    print("=" * 60)
    print("지능형 검색 API 테스트")
    print("=" * 60)
    
    test_queries = [
        {
            "name": "증상 검색",
            "query": "눈이 피로해요",
            "expected_intent": "SYMPTOM_SEARCH"
        },
        {
            "name": "성분 검색",
            "query": "비타민C 성분이 포함된 제품",
            "expected_intent": "INGREDIENT_SEARCH"
        },
        {
            "name": "복용 시간",
            "query": "칼슘은 언제 먹어야 하나요?",
            "expected_intent": "TIMING_QUERY"
        },
        {
            "name": "복합 쿼리",
            "query": "관절 건강에 좋은 MSM 제품",
            "expected_intent": "MIXED"
        },
        {
            "name": "Fallback 테스트",
            "query": "존재하지않는증상12345",
            "expected_fallback": True
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n[테스트 {i}] {test['name']}")
        print(f"쿼리: {test['query']}")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/search/intelligent",
                json={
                    "query": test["query"],
                    "top_k": 3,
                    "enable_fallback": True,
                    "enable_reranking": True
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✓ 성공")
                print(f"  - 의도: {data['query_analysis']['intent']}")
                print(f"  - 선택된 API: {data['routing_info']['selected_api']}")
                print(f"  - Fallback 사용: {data['fallback_used']}")
                
                # 개체명 출력
                entities = data['query_analysis']['entities']
                if any(entities.values()):
                    print(f"  - 추출된 개체명:")
                    for key, values in entities.items():
                        if values:
                            print(f"    • {key}: {', '.join(values)}")
                
                # 결과 개수
                if isinstance(data['results'], list):
                    print(f"  - 검색 결과: {len(data['results'])}개")
                elif isinstance(data['results'], dict):
                    if 'recommendations' in data['results']:
                        print(f"  - 추천 결과: {len(data['results']['recommendations'])}개")
                
                # Fallback 정보
                if data.get('fallback_info'):
                    print(f"  - Fallback 메시지: {data['fallback_info'].get('message', '')[:50]}...")
                
                # 추가 정보
                if data.get('additional_info'):
                    print(f"  - 추가 정보 제공: ✓")
                
            else:
                print(f"✗ 실패 (HTTP {response.status_code})")
                print(f"  {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print("✗ 서버 연결 실패")
            print("  서버가 실행 중인지 확인하세요: http://localhost:8000")
            break
        except Exception as e:
            print(f"✗ 오류: {e}")
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)


def test_health_check():
    """헬스 체크"""
    print("\n서버 상태 확인 중...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ 서버 정상 작동 중")
            return True
        else:
            print(f"✗ 서버 응답 이상 (HTTP {response.status_code})")
            return False
    except:
        print("✗ 서버에 연결할 수 없습니다")
        return False


if __name__ == "__main__":
    if test_health_check():
        test_intelligent_search()
    else:
        print("\n서버를 먼저 시작해주세요:")
        print("  uvicorn api.app:app --reload --host 0.0.0.0 --port 8000")

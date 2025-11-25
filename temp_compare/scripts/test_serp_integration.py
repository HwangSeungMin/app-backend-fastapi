"""
SERP API 통합 테스트 스크립트

Google SERP API가 intelligent search에 제대로 통합되었는지 테스트합니다.
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_intelligent_search_without_serp():
    """SERP 비활성화 테스트"""
    print("\n" + "=" * 60)
    print("테스트 1: SERP 비활성화 (기본)")
    print("=" * 60)
    
    payload = {
        "query": "비타민C 효능",
        "top_k": 5,
        "enable_serp": False
    }
    
    response = requests.post(f"{BASE_URL}/api/search/intelligent", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 성공")
        print(f"  - SERP 활성화: {result.get('serp_enabled', False)}")
        print(f"  - SERP 결과: {len(result.get('serp_results', []))}개")
        print(f"  - RAG 결과: {len(result.get('results', []))}개")
    else:
        print(f"\n✗ 실패: {response.text}")


def test_intelligent_search_with_serp():
    """SERP 활성화 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: SERP 활성화")
    print("=" * 60)
    
    payload = {
        "query": "비타민C 효능",
        "top_k": 5,
        "enable_serp": True,
        "serp_max_results": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/search/intelligent", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 성공")
        print(f"  - SERP 활성화: {result.get('serp_enabled', False)}")
        print(f"  - SERP 결과: {len(result.get('serp_results', []))}개")
        print(f"  - RAG 결과: {len(result.get('results', []))}개")
        
        # SERP 결과 샘플 출력
        if result.get('serp_results'):
            print(f"\nSERP 결과 샘플:")
            for idx, serp in enumerate(result['serp_results'][:3], 1):
                print(f"\n  [{idx}] {serp.get('title', 'N/A')}")
                print(f"      URL: {serp.get('link', 'N/A')}")
                print(f"      설명: {serp.get('snippet', 'N/A')[:100]}...")
    else:
        print(f"\n✗ 실패: {response.text}")


def test_intelligent_search_with_custom_results():
    """SERP 결과 개수 커스터마이징 테스트"""
    print("\n" + "=" * 60)
    print("테스트 3: SERP 결과 개수 커스터마이징 (3개)")
    print("=" * 60)
    
    payload = {
        "query": "오메가3 부작용",
        "top_k": 5,
        "enable_serp": True,
        "serp_max_results": 3
    }
    
    response = requests.post(f"{BASE_URL}/api/search/intelligent", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 성공")
        print(f"  - SERP 활성화: {result.get('serp_enabled', False)}")
        print(f"  - SERP 결과: {len(result.get('serp_results', []))}개")
        print(f"  - 요청한 개수: 3개")
    else:
        print(f"\n✗ 실패: {response.text}")


def test_serp_service_status():
    """SERP 서비스 상태 확인"""
    print("\n" + "=" * 60)
    print("테스트 4: SERP 서비스 상태 확인")
    print("=" * 60)
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        
        from services.serp_service import serp_service
        
        status = serp_service.get_status()
        print(f"\nSERP 서비스 상태:")
        print(f"  - 활성화: {status['enabled']}")
        print(f"  - API 키 설정: {status['api_key_configured']}")
        print(f"  - 최대 결과: {status['max_results']}개")
        print(f"  - 타임아웃: {status['timeout']}초")
        
        if not status['enabled']:
            print(f"\n⚠️ SERP API가 비활성화되어 있습니다.")
            print(f"   .env 파일에서 SERP_API_ENABLED=true로 설정하세요.")
        
        if not status['api_key_configured']:
            print(f"\n⚠️ SERP API 키가 설정되지 않았습니다.")
            print(f"   .env 파일에서 SERP_API_KEY를 설정하세요.")
    
    except Exception as e:
        print(f"\n✗ 오류: {e}")


if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("SERP API 통합 테스트 시작")
        print("=" * 60)
        
        test_serp_service_status()
        test_intelligent_search_without_serp()
        test_intelligent_search_with_serp()
        test_intelligent_search_with_custom_results()
        
        print("\n" + "=" * 60)
        print("✓ 모든 테스트 완료!")
        print("=" * 60)
        
        print("\n💡 참고:")
        print("  - SERP API를 사용하려면 .env 파일에 SERP_API_KEY를 설정하세요")
        print("  - SerpAPI 계정: https://serpapi.com/")
        print("  - 무료: 100회/월, 유료: $50/월 (5,000회)")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"\n✗ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

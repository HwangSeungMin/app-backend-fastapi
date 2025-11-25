"""
Gemini 추천 API 테스트 스크립트

RAG + SERP + Gemini 융합 추천을 테스트합니다.
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_gemini_recommendation_basic():
    """기본 Gemini 추천 테스트"""
    print("\n" + "=" * 60)
    print("테스트 1: 기본 Gemini 추천")
    print("=" * 60)
    
    payload = {
        "query": "눈이 피로하고 시력이 떨어지는 것 같아요",
        "top_k": 5,
        "enable_serp": True,
        "rag_weight": 0.5,
        "max_length": 200
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/gemini", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 성공")
        print(f"\n추천 결과:")
        print(f"{result['recommendation']['text']}")
        print(f"\n구조화된 데이터:")
        print(json.dumps(result['recommendation']['structured'], ensure_ascii=False, indent=2))
        print(f"\n소스 정보:")
        print(f"  - RAG 결과: {result['sources']['rag_count']}개")
        print(f"  - SERP 결과: {result['sources']['serp_count']}개")
        print(f"  - RAG 비중: {result['sources']['rag_weight'] * 100}%")
        print(f"  - Gemini 비중: {result['sources']['gemini_weight'] * 100}%")
        print(f"\n메타데이터:")
        print(f"  - 최대 길이: {result['metadata']['max_length']}자")
        print(f"  - 실제 길이: {result['metadata']['actual_length']}자")
    else:
        print(f"\n✗ 실패: {response.text}")


def test_gemini_high_rag_weight():
    """RAG 비중 높은 추천 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: RAG 비중 높음 (80%)")
    print("=" * 60)
    
    payload = {
        "query": "관절이 아프고 뻣뻣해요",
        "rag_weight": 0.8,  # RAG 80%, Gemini 20%
        "max_length": 250
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/gemini", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 성공")
        print(f"\n추천 결과:")
        print(f"{result['recommendation']['text']}")
        print(f"\n비중:")
        print(f"  - RAG: {result['sources']['rag_weight'] * 100}%")
        print(f"  - Gemini: {result['sources']['gemini_weight'] * 100}%")
    else:
        print(f"\n✗ 실패: {response.text}")


def test_gemini_custom_prompt():
    """커스텀 프롬프트 테스트"""
    print("\n" + "=" * 60)
    print("테스트 3: 커스텀 프롬프트")
    print("=" * 60)
    
    custom_prompt = """
당신은 약사입니다.
사용자의 증상에 맞는 영양제를 추천하되, 
반드시 부작용과 상호작용을 강조해주세요.

출력 형식:
1. 추천 제품
2. 복용 방법
3. 부작용 (상세히)
4. 약물 상호작용

최대 150글자로 작성하세요.
"""
    
    payload = {
        "query": "불면증이 심해요",
        "custom_prompt": custom_prompt,
        "max_length": 150
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/gemini", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 성공")
        print(f"\n추천 결과:")
        print(f"{result['recommendation']['text']}")
    else:
        print(f"\n✗ 실패: {response.text}")


def test_gemini_without_serp():
    """SERP 없이 RAG + Gemini만 테스트"""
    print("\n" + "=" * 60)
    print("테스트 4: SERP 비활성화 (RAG + Gemini만)")
    print("=" * 60)
    
    payload = {
        "query": "피로 회복에 좋은 영양제",
        "enable_serp": False,
        "rag_weight": 0.6,
        "max_length": 180
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/gemini", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 성공")
        print(f"\n추천 결과:")
        print(f"{result['recommendation']['text']}")
        print(f"\nSERP 결과: {result['sources']['serp_count']}개")
    else:
        print(f"\n✗ 실패: {response.text}")


def test_gemini_selective_output():
    """선택적 출력 옵션 테스트"""
    print("\n" + "=" * 60)
    print("테스트 5: 선택적 출력 (제품명과 주의사항만)")
    print("=" * 60)
    
    payload = {
        "query": "혈압이 높아요",
        "include_product_name": True,
        "include_ingredients": False,
        "include_timing": False,
        "include_precautions": True,
        "max_length": 150
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/gemini", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print(f"응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 성공")
        print(f"\n추천 결과:")
        print(f"{result['recommendation']['text']}")
    else:
        print(f"\n✗ 실패: {response.text}")


if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("Gemini 추천 API 테스트 시작")
        print("=" * 60)
        
        test_gemini_recommendation_basic()
        test_gemini_high_rag_weight()
        test_gemini_custom_prompt()
        test_gemini_without_serp()
        test_gemini_selective_output()
        
        print("\n" + "=" * 60)
        print("✓ 모든 테스트 완료!")
        print("=" * 60)
        
        print("\n💡 참고:")
        print("  - Gemini API 키를 .env 파일에 설정하세요")
        print("  - Google AI Studio: https://makersuite.google.com/app/apikey")
        print("  - 무료 할당량: 60 requests/minute")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"\n✗ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

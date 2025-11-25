"""
Timing API 테스트 스크립트 (복수형 통일 버전)

복수 성분 복용 시간 추천 기능을 테스트합니다.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_single_ingredient():
    """단일 성분 테스트 (복수형 배열로 전달)"""
    print("\n" + "=" * 60)
    print("단일 성분 복용 시간 추천 테스트")
    print("=" * 60)
    
    payload = {
        "ingredients": ["철분"]
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/timing", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
    print(f"응답 코드: {response.status_code}")
    print(f"응답 내용:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))


def test_multiple_ingredients_no_conflict():
    """복수 성분 테스트 (충돌 없음)"""
    print("\n" + "=" * 60)
    print("복수 성분 복용 시간 추천 테스트 (충돌 없음)")
    print("=" * 60)
    
    payload = {
        "ingredients": ["비타민D", "비타민C", "오메가3"]
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/timing", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
    print(f"응답 코드: {response.status_code}")
    print(f"응답 내용:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))


def test_multiple_ingredients_with_conflict():
    """복수 성분 테스트 (충돌 있음)"""
    print("\n" + "=" * 60)
    print("복수 성분 복용 시간 추천 테스트 (충돌 있음)")
    print("=" * 60)
    
    payload = {
        "ingredients": ["철분", "칼슘", "비타민D", "마그네슘", "아연"]
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/timing", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
    print(f"응답 코드: {response.status_code}")
    
    result = response.json()
    print(f"\n응답 요약:")
    if 'data' in result and 'summary' in result['data']:
        summary = result['data']['summary']
        print(f"  - 총 성분 수: {summary['total_ingredients']}개")
        print(f"  - 정보 있는 성분: {summary.get('ingredients_with_info', 0)}개")
        print(f"  - 정보 없는 성분: {summary.get('ingredients_without_info', 0)}개")
        print(f"  - 충돌 개수: {summary['conflict_count']}개")
        print(f"  - 복용 시간대: {summary['timing_slots']}개")
    
    print(f"\n최적 복용 스케줄:")
    if 'data' in result and 'optimal_schedule' in result['data']:
        for slot in result['data']['optimal_schedule']:
            print(f"\n  [{slot['time']}] {slot['timing']}")
            print(f"    - 성분: {', '.join(slot['ingredients'])}")
            if slot['notes']:
                for note in slot['notes']:
                    print(f"    - {note}")
    
    print(f"\n충돌 정보:")
    if 'data' in result and 'conflicts' in result['data']:
        for conflict in result['data']['conflicts']:
            print(f"\n  ⚠️ {conflict['warning']}")
            print(f"     해결방안: {conflict['solution']}")
            print(f"     간격: {conflict['time_gap']}")


def test_unknown_ingredients():
    """정보가 없는 성분들 테스트"""
    print("\n" + "=" * 60)
    print("정보가 없는 성분들 테스트 (기본 추천)")
    print("=" * 60)
    
    payload = {
        "ingredients": ["알 수 없는 성분1", "알 수 없는 성분2", "알 수 없는 성분3"]
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/timing", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
    print(f"응답 코드: {response.status_code}")
    
    result = response.json()
    print(f"\n응답:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def test_mixed_ingredients():
    """정보가 있는 성분과 없는 성분 혼합 테스트"""
    print("\n" + "=" * 60)
    print("정보 있는 성분 + 없는 성분 혼합 테스트")
    print("=" * 60)
    
    payload = {
        "ingredients": ["철분", "알 수 없는 성분", "비타민D", "마그네슘"]
    }
    
    response = requests.post(f"{BASE_URL}/api/recommend/timing", json=payload)
    
    print(f"\n요청: {json.dumps(payload, ensure_ascii=False)}")
    print(f"응답 코드: {response.status_code}")
    
    result = response.json()
    print(f"\n응답 요약:")
    if 'data' in result and 'summary' in result['data']:
        summary = result['data']['summary']
        print(f"  - 총 성분 수: {summary['total_ingredients']}개")
        print(f"  - 정보 있는 성분: {summary.get('ingredients_with_info', 0)}개")
        print(f"  - 정보 없는 성분: {summary.get('ingredients_without_info', 0)}개")
    
    if 'data' in result and 'ingredients_without_timing_info' in result['data']:
        print(f"\n정보가 없는 성분:")
        for ing in result['data']['ingredients_without_timing_info']:
            print(f"  - {ing}")


if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("Timing API 테스트 시작 (복수형 통일 버전)")
        print("=" * 60)
        
        test_single_ingredient()
        test_multiple_ingredients_no_conflict()
        test_multiple_ingredients_with_conflict()
        test_unknown_ingredients()
        test_mixed_ingredients()
        
        print("\n" + "=" * 60)
        print("✓ 모든 테스트 완료!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"\n✗ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

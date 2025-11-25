"""
복용 시간 추천 서비스만 테스트하는 스크립트 (Elasticsearch 불필요)
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.timing_service import TimingService

def test_timing_service():
    """복용 시간 추천 테스트"""

    timing_service = TimingService()

    test_ingredients = ['철분', '비타민D', '비타민C', '칼슘', '마그네슘', '오메가3']

    print("\n" + "=" * 80)
    print("복용 시간 추천 테스트")
    print("=" * 80)

    for ingredient in test_ingredients:
        print(f"\n>>> {ingredient} 복용 시간 추천")
        result = timing_service.recommend_timing(ingredient)

        print(f"복용 유형: {result['timing_type']}")
        print(f"이유: {result['reason']}")

        if result.get('avoid_with'):
            print(f"함께 복용 피할 것: {', '.join(result['avoid_with'])}")

        print("추천 시간:")
        for time_rec in result['recommended_times']:
            print(f"  - {time_rec['time']}: {time_rec['description']} (우선순위: {time_rec['priority']})")

        print("-" * 80)

    # 다중 성분 테스트
    print("\n" + "=" * 80)
    print("다중 성분 복용 시간 추천 및 충돌 검사")
    print("=" * 80)

    multi_ingredients = ['철분', '칼슘', '비타민D']
    result = timing_service.recommend_multiple_timing(multi_ingredients)

    print(f"\n{result['message']}")

    if result['conflicts']:
        print("\n⚠️ 복용 충돌 경고:")
        for conflict in result['conflicts']:
            print(f"  - {conflict['recommendation']}")
    else:
        print("\n✓ 복용 충돌 없음")

    print("\n" + "=" * 80)
    print("테스트 완료!")
    print("=" * 80)

if __name__ == '__main__':
    test_timing_service()

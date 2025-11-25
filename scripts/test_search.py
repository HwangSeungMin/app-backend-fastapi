"""
검색 기능 테스트 스크립트
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.search.rag_search import RAGSearchEngine
from app.services.rag.recommendation_service import RecommendationService
from app.services.rag.timing_service import TimingService
from app.utils.logger import get_logger
import argparse
import json

logger = get_logger(__name__)

def print_search_results(results, title="검색 결과"):
    """검색 결과 출력"""
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)
    
    if not results:
        print("결과가 없습니다.")
        return
    
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] {result['product_name']}")
        print(f"    회사: {result['company_name']}")
        print(f"    점수: {result['score']:.2f}")
        print(f"    주요기능: {result['primary_function'][:100]}...")
        
        if result.get('classification'):
            cls = result['classification']
            if cls.get('category'):
                print(f"    카테고리: {cls['category']}")
    
    print("=" * 80)

def test_hybrid_search(engine, query, top_k=5):
    """하이브리드 검색 테스트"""
    print(f"\n>>> 하이브리드 검색: '{query}'")
    results = engine.hybrid_search(query, top_k=top_k)
    print_search_results(results, f"하이브리드 검색 결과 ({query})")

def test_symptom_search(engine, symptom, top_k=5):
    """증상 검색 테스트"""
    print(f"\n>>> 증상 검색: '{symptom}'")
    results = engine.search_by_symptom(symptom, top_k=top_k)
    print_search_results(results, f"증상 검색 결과 ({symptom})")

def test_ingredient_search(engine, ingredient, top_k=5):
    """성분 검색 테스트"""
    print(f"\n>>> 성분 검색: '{ingredient}'")
    results = engine.search_by_ingredient(ingredient, top_k=top_k)
    print_search_results(results, f"성분 검색 결과 ({ingredient})")

def test_recommendation(service, symptom, top_k=3):
    """추천 서비스 테스트"""
    print(f"\n>>> 증상 기반 추천: '{symptom}'")
    result = service.recommend_by_symptom(symptom, top_k=top_k)
    
    print("\n" + "=" * 80)
    print(f"추천 결과 ({symptom})")
    print("=" * 80)
    print(f"메시지: {result['message']}")
    
    for idx, rec in enumerate(result['recommendations'], 1):
        print(f"\n[{idx}] {rec['product_name']}")
        print(f"    회사: {rec['company_name']}")
        print(f"    관련도: {rec['relevance_score']:.2f}")
        print(f"    주요기능: {rec['primary_function'][:100]}...")
        print(f"    주요성분: {', '.join(rec['key_ingredients'])}")
    
    print("=" * 80)

def test_timing_service(service, ingredient):
    """복용 시간 추천 테스트"""
    print(f"\n>>> 복용 시간 추천: '{ingredient}'")
    result = service.recommend_timing(ingredient)
    
    print("\n" + "=" * 80)
    print(f"복용 시간 추천 ({ingredient})")
    print("=" * 80)
    print(f"복용 유형: {result['timing_type']}")
    print(f"이유: {result['reason']}")
    
    if result.get('avoid_with'):
        print(f"함께 복용 피할 것: {', '.join(result['avoid_with'])}")
    
    print("\n추천 시간:")
    for time_rec in result['recommended_times']:
        print(f"  - {time_rec['time']}: {time_rec['description']} (우선순위: {time_rec['priority']})")
    
    print("=" * 80)

def run_all_tests():
    """전체 테스트 실행"""
    logger.info("RAG 검색 시스템 테스트 시작")
    
    # 검색 엔진 초기화
    search_engine = RAGSearchEngine()
    recommendation_service = RecommendationService()
    timing_service = TimingService()
    
    # 테스트 케이스들
    test_cases = {
        'hybrid': [
            '피로 회복',
            '면역력 강화',
            '비타민 D'
        ],
        'symptom': [
            '피곤해요',
            '눈이 침침해요',
            '관절이 아파요'
        ],
        'ingredient': [
            '철분',
            '오메가3',
            '비타민B'
        ]
    }
    
    # 하이브리드 검색 테스트
    print("\n" + "#" * 80)
    print("# 하이브리드 검색 테스트")
    print("#" * 80)
    for query in test_cases['hybrid']:
        test_hybrid_search(search_engine, query, top_k=3)
    
    # 증상 검색 테스트
    print("\n" + "#" * 80)
    print("# 증상 검색 테스트")
    print("#" * 80)
    for symptom in test_cases['symptom']:
        test_symptom_search(search_engine, symptom, top_k=3)
    
    # 성분 검색 테스트
    print("\n" + "#" * 80)
    print("# 성분 검색 테스트")
    print("#" * 80)
    for ingredient in test_cases['ingredient']:
        test_ingredient_search(search_engine, ingredient, top_k=3)
    
    # 추천 서비스 테스트
    print("\n" + "#" * 80)
    print("# 추천 서비스 테스트")
    print("#" * 80)
    test_recommendation(recommendation_service, '피로 회복', top_k=3)
    
    # 복용 시간 추천 테스트
    print("\n" + "#" * 80)
    print("# 복용 시간 추천 테스트")
    print("#" * 80)
    test_timing_service(timing_service, '철분')
    test_timing_service(timing_service, '비타민D')
    
    logger.info("\n테스트 완료!")

def main():
    parser = argparse.ArgumentParser(description='RAG 검색 시스템 테스트')
    parser.add_argument('--mode', type=str, choices=['all', 'hybrid', 'symptom', 'ingredient', 'recommend', 'timing'],
                       default='all', help='테스트 모드')
    parser.add_argument('--query', type=str, help='검색 쿼리 (특정 모드에서 사용)')
    parser.add_argument('--top-k', type=int, default=5, help='반환할 결과 개수 (기본값: 5)')

    args = parser.parse_args()

    # 검색 엔진 및 서비스 초기화
    search_engine = RAGSearchEngine()
    recommendation_service = RecommendationService()
    timing_service = TimingService()

    if args.mode == 'all':
        run_all_tests()

    elif args.mode == 'hybrid':
        query = args.query or '피로 회복'
        test_hybrid_search(search_engine, query, top_k=args.top_k)

    elif args.mode == 'symptom':
        symptom = args.query or '피곤해요'
        test_symptom_search(search_engine, symptom, top_k=args.top_k)

    elif args.mode == 'ingredient':
        ingredient = args.query or '철분'
        test_ingredient_search(search_engine, ingredient, top_k=args.top_k)

    elif args.mode == 'recommend':
        symptom = args.query or '피로 회복'
        test_recommendation(recommendation_service, symptom, top_k=args.top_k)

    elif args.mode == 'timing':
        ingredient = args.query or '철분'
        test_timing_service(timing_service, ingredient)

if __name__ == '__main__':
    main()
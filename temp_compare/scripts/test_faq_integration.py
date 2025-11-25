"""
FAQ 통합 테스트 스크립트

Knowledge Base와 Fallback 시스템이 FAQ 데이터를 제대로 사용하는지 테스트합니다.
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.knowledge_base import HealthKnowledgeBase
from search.fallback_system import FallbackSystem
from search.query_analyzer import QueryAnalyzer
import json


def test_knowledge_base():
    """Knowledge Base 테스트"""
    print("\n" + "=" * 60)
    print("Knowledge Base 테스트")
    print("=" * 60)
    
    kb = HealthKnowledgeBase()
    
    # 테스트 쿼리들
    test_queries = [
        "피로가 심해요",
        "두통이 자주 와요",
        "스트레스 받아요",
        "눈이 피로해요",
        "소화가 안돼요"
    ]
    
    for query in test_queries:
        print(f"\n쿼리: '{query}'")
        rec = kb.get_default_recommendation(query)
        
        if rec:
            print(f"  ✓ 카테고리: {rec['category']}")
            print(f"  ✓ 추천 영양제: {', '.join(rec['products'][:3])}...")
            print(f"  ✓ 건강 팁: {', '.join(rec['tips'][:2])}...")
            if 'faqs' in rec and rec['faqs']:
                print(f"  ✓ FAQ 개수: {len(rec['faqs'])}개")
        else:
            print("  ✗ 매칭 실패")


def test_fallback_system():
    """Fallback 시스템 테스트"""
    print("\n" + "=" * 60)
    print("Fallback 시스템 테스트")
    print("=" * 60)
    
    fallback = FallbackSystem()
    analyzer = QueryAnalyzer()
    
    # 테스트 쿼리
    query = "피로가 심해서 힘들어요"
    
    print(f"\n쿼리: '{query}'")
    
    # 쿼리 분석
    analysis = analyzer.analyze(query)
    
    # Fallback 응답 생성
    response = fallback.generate_fallback_response(query, analysis)
    
    print("\n응답:")
    print(json.dumps(response, ensure_ascii=False, indent=2))


def test_faq_data():
    """FAQ 데이터 통계"""
    print("\n" + "=" * 60)
    print("FAQ 데이터 통계")
    print("=" * 60)
    
    kb = HealthKnowledgeBase()
    
    total_categories = len(kb.DEFAULT_RECOMMENDATIONS)
    total_faqs = sum(
        len(data.get('faqs', [])) 
        for data in kb.DEFAULT_RECOMMENDATIONS.values()
    )
    total_products = len(kb.get_all_ingredients())
    
    print(f"\n총 증상 카테고리: {total_categories}개")
    print(f"총 FAQ 항목: {total_faqs}개")
    print(f"총 영양제 종류: {total_products}개")
    
    print("\n카테고리별 FAQ 개수:")
    for category, data in sorted(kb.DEFAULT_RECOMMENDATIONS.items()):
        faq_count = len(data.get('faqs', []))
        print(f"  - {category}: {faq_count}개")


if __name__ == "__main__":
    try:
        test_knowledge_base()
        test_fallback_system()
        test_faq_data()
        
        print("\n" + "=" * 60)
        print("✓ 모든 테스트 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

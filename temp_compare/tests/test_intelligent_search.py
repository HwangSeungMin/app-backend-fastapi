"""
지능형 검색 시스템 테스트
"""
import pytest
from search.query_analyzer import QueryAnalyzer
from search.smart_router import SmartRouter
from search.fallback_system import FallbackSystem
from search.reranker import ResultReRanker
from utils.knowledge_base import HealthKnowledgeBase


class TestQueryAnalyzer:
    """쿼리 분석기 테스트"""
    
    def setup_method(self):
        self.analyzer = QueryAnalyzer()
    
    def test_symptom_extraction(self):
        """증상 추출 테스트"""
        result = self.analyzer.analyze("눈이 피로해요")
        
        assert "눈" in result["entities"]["body_parts"]
        assert "피로" in result["entities"]["symptoms"]
    
    def test_ingredient_extraction(self):
        """성분 추출 테스트"""
        result = self.analyzer.analyze("비타민C가 필요해요")
        
        assert "비타민C" in result["entities"]["ingredients"]
    
    def test_intent_classification(self):
        """의도 분류 테스트"""
        # 증상 검색
        result1 = self.analyzer.analyze("관절이 아파요")
        assert result1["intent"] in ["SYMPTOM_SEARCH", "MIXED"]
        
        # 성분 검색
        result2 = self.analyzer.analyze("오메가3 성분이 포함된 제품")
        assert result2["intent"] in ["INGREDIENT_SEARCH", "MIXED"]
        
        # 복용 시간
        result3 = self.analyzer.analyze("칼슘은 언제 먹어야 하나요?")
        assert result3["intent"] == "TIMING_QUERY"
    
    def test_query_expansion(self):
        """쿼리 확장 테스트"""
        result = self.analyzer.analyze("피로")
        
        # 확장된 쿼리에 동의어 포함 확인
        expanded = result["expanded_query"]
        assert len(expanded) > len("피로")


class TestKnowledgeBase:
    """지식 베이스 테스트"""
    
    def setup_method(self):
        self.kb = HealthKnowledgeBase()
    
    def test_symptom_nutrient_mapping(self):
        """증상-영양소 매핑 테스트"""
        result = self.kb.get_nutrients_for_symptom("눈이 피로해요")
        
        assert result is not None
        assert "루테인" in result["nutrients"]
    
    def test_interaction_info(self):
        """성분 상호작용 정보 테스트"""
        result = self.kb.get_interaction_info("칼슘")
        
        assert result is not None
        assert "철분" in result["avoid_with"]
        assert "비타민D" in result["synergy_with"]
    
    def test_timing_recommendation(self):
        """복용 시간 추천 테스트"""
        result = self.kb.get_timing_recommendation("칼슘")
        
        assert result is not None
        assert "저녁" in result["timing"]


class TestFallbackSystem:
    """Fallback 시스템 테스트"""
    
    def setup_method(self):
        self.fallback = FallbackSystem()
    
    def test_should_use_fallback(self):
        """Fallback 사용 여부 판단 테스트"""
        # 결과 부족
        assert self.fallback.should_use_fallback([]) == True
        assert self.fallback.should_use_fallback([1]) == True
        
        # 결과 충분
        assert self.fallback.should_use_fallback([1, 2, 3]) == False
    
    def test_fallback_response_generation(self):
        """Fallback 응답 생성 테스트"""
        analysis = {
            "entities": {
                "symptoms": ["피로"],
                "ingredients": [],
                "body_parts": []
            }
        }
        
        result = self.fallback.generate_fallback_response("피로해요", analysis)
        
        assert result["fallback_used"] == True
        assert "message" in result


class TestReRanker:
    """Re-ranking 시스템 테스트"""
    
    def setup_method(self):
        self.reranker = ResultReRanker()
    
    def test_reranking(self):
        """재정렬 테스트"""
        results = [
            {
                "score": 1.0,
                "product_name": "비타민C",
                "company_name": "종근당",
                "report_date": "20230101"
            },
            {
                "score": 0.8,
                "product_name": "일반제품",
                "company_name": "일반회사",
                "report_date": "20100101"
            }
        ]
        
        reranked = self.reranker.rerank(results)
        
        # 재정렬 점수 추가 확인
        assert "rerank_score" in reranked[0]
        assert "score_breakdown" in reranked[0]
    
    def test_diversity_reranking(self):
        """다양성 재정렬 테스트"""
        results = [
            {"score": 1.0, "company_name": "A사", "product_name": "제품1"},
            {"score": 0.9, "company_name": "A사", "product_name": "제품2"},
            {"score": 0.8, "company_name": "A사", "product_name": "제품3"},
            {"score": 0.7, "company_name": "B사", "product_name": "제품4"},
        ]
        
        diverse = self.reranker.rerank_with_diversity(
            results,
            diversity_field="company_name",
            max_per_group=2
        )
        
        # A사 제품이 최대 2개까지만
        a_company_count = sum(1 for r in diverse[:3] if r["company_name"] == "A사")
        assert a_company_count <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

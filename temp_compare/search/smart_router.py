"""
스마트 라우터 (Smart Router)

분석된 쿼리를 적절한 검색 API로 라우팅합니다.
"""
from typing import Dict, Tuple, Optional
from search.rag_search import RAGSearchEngine
from services.recommendation_service import RecommendationService
from services.timing_service import TimingService
from utils.logger import get_logger

logger = get_logger(__name__)


class SmartRouter:
    """지능형 쿼리 라우터"""
    
    def __init__(self):
        self.search_engine = RAGSearchEngine()
        self.recommendation_service = RecommendationService()
        self.timing_service = TimingService()
        
        logger.info("스마트 라우터 초기화 완료")
    
    def route(
        self, 
        analysis: Dict, 
        top_k: int = 5
    ) -> Tuple[str, Dict, any]:
        """
        쿼리 분석 결과를 기반으로 적절한 API로 라우팅
        
        Returns:
            (api_name, routing_info, results)
        """
        
        query = analysis["original_query"]
        intent = analysis["intent"]
        entities = analysis["entities"]
        expanded_query = analysis["expanded_query"]
        
        logger.info(f"라우팅 시작: 의도={intent}")
        
        # 1. 복용 시간 질문
        if intent == "TIMING_QUERY" and entities["ingredients"]:
            ingredient = entities["ingredients"][0]
            logger.info(f"→ 복용 시간 추천 API: {ingredient}")
            
            result = self.timing_service.recommend_timing(ingredient)
            
            return (
                "timing_recommend",
                {
                    "reason": "복용 시간 질문 감지",
                    "ingredient": ingredient
                },
                result
            )
        
        # 2. 성분 검색 (명시적 키워드)
        if intent == "INGREDIENT_SEARCH" and entities["ingredients"]:
            ingredient = entities["ingredients"][0]
            logger.info(f"→ 성분 검색 API: {ingredient}")
            
            results = self.search_engine.search_by_ingredient(
                ingredient=ingredient,
                top_k=top_k
            )
            
            return (
                "ingredient_search",
                {
                    "reason": "성분 키워드 감지",
                    "ingredient": ingredient
                },
                results
            )
        
        # 3. 증상 기반 추천
        if intent == "SYMPTOM_SEARCH" or (entities["symptoms"] and not entities["ingredients"]):
            symptom = entities["symptoms"][0] if entities["symptoms"] else query
            logger.info(f"→ 증상 추천 API: {symptom}")
            
            result = self.recommendation_service.recommend_by_symptom(
                symptom=symptom,
                top_k=top_k
            )
            
            return (
                "symptom_recommend",
                {
                    "reason": "증상 감지",
                    "symptom": symptom
                },
                result
            )
        
        # 4. 복합 쿼리 또는 일반 검색 - 하이브리드 검색 (확장된 쿼리 사용)
        logger.info(f"→ 하이브리드 검색 API: {expanded_query}")
        
        results = self.search_engine.hybrid_search(
            query=expanded_query,
            top_k=top_k
        )
        
        return (
            "hybrid_search",
            {
                "reason": "복합 쿼리 또는 일반 검색",
                "used_expanded_query": True,
                "original_query": query,
                "expanded_query": expanded_query
            },
            results
        )
    
    def route_and_execute(
        self,
        analysis: Dict,
        top_k: int = 5
    ) -> Dict:
        """라우팅 및 실행 (통합 응답 형식)"""
        
        api_name, routing_info, results = self.route(analysis, top_k)
        
        return {
            "api_used": api_name,
            "routing_info": routing_info,
            "results": results
        }

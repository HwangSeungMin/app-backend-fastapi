"""
Fallback 응답 시스템

검색 결과가 없거나 부족할 때 카테고리별 기본 추천을 제공합니다.
"""
from typing import Dict, List, Optional
from utils.knowledge_base import HealthKnowledgeBase
from utils.logger import get_logger

logger = get_logger(__name__)


class FallbackSystem:
    """Fallback 응답 시스템"""
    
    def __init__(self):
        self.kb = HealthKnowledgeBase()
        logger.info("Fallback 시스템 초기화 완료")
    
    def should_use_fallback(
        self, 
        results: any, 
        threshold: int = 2
    ) -> bool:
        """Fallback 사용 여부 판단"""
        
        # 결과가 리스트인 경우
        if isinstance(results, list):
            return len(results) < threshold
        
        # 추천 결과 딕셔너리인 경우
        if isinstance(results, dict):
            if "recommendations" in results:
                return len(results["recommendations"]) < threshold
            if "products" in results:
                return len(results["products"]) < threshold
            if "results" in results:
                return len(results["results"]) < threshold
        
        return False
    
    def generate_fallback_response(
        self, 
        query: str, 
        analysis: Dict
    ) -> Dict:
        """Fallback 응답 생성"""
        
        logger.info(f"Fallback 응답 생성: '{query}'")
        
        # 1. 지식 베이스에서 기본 추천 찾기
        default_rec = self.kb.get_default_recommendation(query)
        
        if default_rec:
            logger.info(f"카테고리 매칭: {default_rec['category']}")
            
            response = {
                "fallback_used": True,
                "category": default_rec["category"],
                "message": default_rec["message"],
                "suggested_products": default_rec["products"],
                "health_tips": default_rec["tips"],
                "note": "정확한 제품 검색 결과가 부족하여 일반적인 추천을 제공합니다."
            }
            
            # FAQ 데이터 추가 (있는 경우)
            if "faqs" in default_rec and default_rec["faqs"]:
                response["related_faqs"] = default_rec["faqs"][:3]  # 상위 3개만
                logger.info(f"관련 FAQ {len(response['related_faqs'])}개 추가")
            
            return response
        
        # 2. 추출된 개체명 기반 추천
        entities = analysis.get("entities", {})
        
        if entities.get("symptoms"):
            symptom = entities["symptoms"][0]
            nutrient_info = self.kb.get_nutrients_for_symptom(symptom)
            
            if nutrient_info:
                return {
                    "fallback_used": True,
                    "detected_symptom": symptom,
                    "message": nutrient_info["description"],
                    "recommended_nutrients": nutrient_info["nutrients"],
                    "note": "증상에 도움이 될 수 있는 영양소를 추천합니다."
                }
        
        if entities.get("ingredients"):
            ingredient = entities["ingredients"][0]
            interaction_info = self.kb.get_interaction_info(ingredient)
            
            if interaction_info:
                return {
                    "fallback_used": True,
                    "detected_ingredient": ingredient,
                    "message": f"{ingredient}에 대한 정보입니다.",
                    "timing": interaction_info.get("timing"),
                    "synergy_with": interaction_info.get("synergy_with", []),
                    "avoid_with": interaction_info.get("avoid_with", []),
                    "note": "성분 정보를 제공합니다."
                }
        
        # 3. 일반적인 Fallback
        return {
            "fallback_used": True,
            "message": "구체적인 증상이나 필요한 성분을 말씀해주시면 더 정확한 추천이 가능합니다.",
            "suggestions": [
                "피로 회복",
                "면역력 강화",
                "눈 건강",
                "관절 건강",
                "소화 개선"
            ],
            "examples": [
                "눈이 피로해요",
                "비타민C 성분이 포함된 제품",
                "관절 통증에 좋은 영양제",
                "칼슘은 언제 먹어야 하나요?"
            ],
            "note": "위와 같은 형태로 질문해주세요."
        }
    
    def enhance_results(
        self,
        results: any,
        query: str,
        analysis: Dict
    ) -> Dict:
        """결과에 추가 정보 보강"""
        
        enhanced = {
            "original_results": results,
            "additional_info": {}
        }
        
        # 증상 관련 추가 정보
        entities = analysis.get("entities", {})
        
        if entities.get("symptoms"):
            symptom = entities["symptoms"][0]
            nutrient_info = self.kb.get_nutrients_for_symptom(symptom)
            
            if nutrient_info:
                enhanced["additional_info"]["symptom_guide"] = {
                    "symptom": symptom,
                    "recommended_nutrients": nutrient_info["nutrients"],
                    "description": nutrient_info["description"]
                }
        
        # 성분 관련 추가 정보
        if entities.get("ingredients"):
            ingredient = entities["ingredients"][0]
            
            # 상호작용 정보
            interaction_info = self.kb.get_interaction_info(ingredient)
            if interaction_info:
                enhanced["additional_info"]["interaction_guide"] = interaction_info
            
            # 복용 시간 정보
            timing_info = self.kb.get_timing_recommendation(ingredient)
            if timing_info:
                enhanced["additional_info"]["timing_guide"] = timing_info
        
        return enhanced

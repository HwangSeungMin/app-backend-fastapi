from typing import List, Dict, Optional
from app.search.rag_search import RAGSearchEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RecommendationService:
    """추천 서비스"""
    
    def __init__(self):
        self.search_engine = RAGSearchEngine()
    
    def recommend_by_symptom(
        self, 
        symptom: str, 
        top_k: int = 3
    ) -> Dict:
        """증상 기반 영양제 추천"""
        
        logger.info(f"증상 기반 추천 시작: '{symptom}'")
        
        # RAG 검색
        search_results = self.search_engine.search_by_symptom(symptom, top_k=top_k)
        
        if not search_results:
            return {
                'symptom': symptom,
                'recommendations': [],
                'message': '관련 영양제를 찾을 수 없습니다.'
            }
        
        # 추천 결과 생성
        recommendations = []
        
        for result in search_results:
            recommendation = {
                'product_name': result['product_name'],
                'company_name': result['company_name'],
                'primary_function': result['primary_function'],
                'key_ingredients': self._extract_key_ingredients(result['raw_materials']),
                'relevance_score': round(result['score'], 2),
                'intake_method': result['classification'].get('intake_method', ''),
                'caution': result['classification'].get('intake_caution', '')
            }
            recommendations.append(recommendation)
        
        return {
            'symptom': symptom,
            'recommendations': recommendations,
            'message': f'{len(recommendations)}개의 추천 제품을 찾았습니다.'
        }
    
    def recommend_by_ingredient(
        self, 
        ingredient: str, 
        top_k: int = 5
    ) -> Dict:
        """성분 기반 영양제 추천"""
        
        logger.info(f"성분 기반 추천 시작: '{ingredient}'")
        
        search_results = self.search_engine.search_by_ingredient(ingredient, top_k=top_k)
        
        if not search_results:
            return {
                'ingredient': ingredient,
                'products': [],
                'message': '해당 성분을 포함한 제품을 찾을 수 없습니다.'
            }
        
        products = []
        
        for result in search_results:
            product = {
                'product_id': result['product_id'],
                'product_name': result['product_name'],
                'company_name': result['company_name'],
                'raw_materials': result['raw_materials'],
                'primary_function': result['primary_function']
            }
            products.append(product)
        
        return {
            'ingredient': ingredient,
            'products': products,
            'count': len(products),
            'message': f'{len(products)}개의 제품을 찾았습니다.'
        }
    
    def _extract_key_ingredients(self, raw_materials: str, limit: int = 3) -> List[str]:
        """주요 성분 추출 (간단한 로직)"""
        
        if not raw_materials:
            return []
        
        # 쉼표나 괄호로 구분된 성분 추출
        ingredients = []
        
        for part in raw_materials.split(','):
            part = part.strip()
            if part and '(' in part:
                part = part.split('(')[0].strip()
            if part:
                ingredients.append(part)
        
        return ingredients[:limit]
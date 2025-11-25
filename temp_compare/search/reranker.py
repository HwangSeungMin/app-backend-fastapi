"""
Re-ranking 시스템

검색 결과를 재정렬하여 품질을 향상시킵니다.
"""
from typing import List, Dict
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class ResultReRanker:
    """검색 결과 재정렬기"""
    
    def __init__(self):
        # 인기 제조사 (신뢰도 높음)
        self.trusted_companies = [
            "종근당", "유한양행", "대웅제약", "동아제약", "한미약품",
            "GC녹십자", "일양약품", "광동제약", "한국야쿠르트", "CJ제일제당"
        ]
        
        logger.info("Re-ranking 시스템 초기화 완료")
    
    def rerank(
        self, 
        results: List[Dict], 
        query: str = "",
        enable_popularity: bool = True,
        enable_trust: bool = True,
        enable_recency: bool = True
    ) -> List[Dict]:
        """
        검색 결과 재정렬
        
        최종 점수 = 검색점수(60%) + 인기도(20%) + 신뢰도(10%) + 최신성(10%)
        """
        
        if not results:
            return results
        
        logger.info(f"Re-ranking 시작: {len(results)}개 결과")
        
        # 각 결과에 추가 점수 계산
        for result in results:
            # 기본 검색 점수 (정규화)
            base_score = result.get('score', 0)
            
            # 인기도 점수 (제품명 길이 기반 - 간단한 휴리스틱)
            popularity_score = 0
            if enable_popularity:
                popularity_score = self._calculate_popularity_score(result)
            
            # 신뢰도 점수 (제조사 평판)
            trust_score = 0
            if enable_trust:
                trust_score = self._calculate_trust_score(result)
            
            # 최신성 점수
            recency_score = 0
            if enable_recency:
                recency_score = self._calculate_recency_score(result)
            
            # 최종 점수 계산
            final_score = (
                base_score * 0.6 +
                popularity_score * 0.2 +
                trust_score * 0.1 +
                recency_score * 0.1
            )
            
            result['rerank_score'] = final_score
            result['score_breakdown'] = {
                'base': base_score,
                'popularity': popularity_score,
                'trust': trust_score,
                'recency': recency_score
            }
        
        # 재정렬
        reranked = sorted(results, key=lambda x: x['rerank_score'], reverse=True)
        
        logger.info("Re-ranking 완료")
        
        return reranked
    
    def _calculate_popularity_score(self, result: Dict) -> float:
        """
        인기도 점수 계산
        
        실제로는 조회수, 구매 데이터 등을 사용해야 하지만,
        현재는 간단한 휴리스틱 사용
        """
        
        # 제품명에 흔한 키워드가 있으면 인기 제품으로 간주
        popular_keywords = [
            "비타민", "오메가", "프로바이오틱스", "유산균", "칼슘",
            "마그네슘", "루테인", "홍삼", "프로폴리스", "콜라겐"
        ]
        
        product_name = result.get('product_name', '').lower()
        
        score = 0
        for keyword in popular_keywords:
            if keyword in product_name:
                score += 0.2
        
        # 정규화 (0~1)
        return min(score, 1.0)
    
    def _calculate_trust_score(self, result: Dict) -> float:
        """신뢰도 점수 (제조사 평판)"""
        
        company_name = result.get('company_name', '')
        
        # 신뢰할 수 있는 제조사
        for trusted in self.trusted_companies:
            if trusted in company_name:
                return 1.0
        
        # 기타 제조사
        return 0.5
    
    def _calculate_recency_score(self, result: Dict) -> float:
        """최신성 점수"""
        
        report_date = result.get('report_date', '')
        
        if not report_date:
            return 0.5
        
        try:
            # 날짜 파싱 (YYYYMMDD 형식 가정)
            if len(report_date) == 8:
                year = int(report_date[:4])
                current_year = datetime.now().year
                
                # 최근 5년 이내
                if current_year - year <= 5:
                    return 1.0
                elif current_year - year <= 10:
                    return 0.7
                else:
                    return 0.3
        except:
            pass
        
        return 0.5
    
    def rerank_with_diversity(
        self,
        results: List[Dict],
        diversity_field: str = 'company_name',
        max_per_group: int = 2
    ) -> List[Dict]:
        """
        다양성을 고려한 재정렬
        
        같은 제조사 제품이 너무 많이 나오지 않도록 조정
        """
        
        if not results:
            return results
        
        logger.info(f"다양성 Re-ranking 시작: 필드={diversity_field}")
        
        # 먼저 기본 re-ranking
        reranked = self.rerank(results)
        
        # 다양성 적용
        diverse_results = []
        group_counts = {}
        
        for result in reranked:
            group_key = result.get(diversity_field, 'unknown')
            
            if group_counts.get(group_key, 0) < max_per_group:
                diverse_results.append(result)
                group_counts[group_key] = group_counts.get(group_key, 0) + 1
        
        # 남은 결과 추가 (다양성 제한 초과한 것들)
        for result in reranked:
            if result not in diverse_results:
                diverse_results.append(result)
        
        logger.info(f"다양성 Re-ranking 완료: {len(diverse_results)}개 결과")
        
        return diverse_results

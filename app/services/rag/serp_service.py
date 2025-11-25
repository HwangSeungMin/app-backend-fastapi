"""
Google SERP API 서비스

SerpAPI를 사용하여 Google 검색 결과를 가져옵니다.
"""
from typing import List, Dict, Optional
import asyncio
from serpapi import GoogleSearch
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SerpService:
    """Google SERP API 서비스"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'SERP_API_KEY', None)
        self.enabled = getattr(settings, 'SERP_API_ENABLED', False)
        self.max_results = getattr(settings, 'SERP_MAX_RESULTS', 5)
        self.timeout = getattr(settings, 'SERP_TIMEOUT', 5)
        
        if self.enabled and not self.api_key:
            logger.warning("SERP API가 활성화되었지만 API 키가 설정되지 않았습니다.")
            self.enabled = False
    
    async def search(
        self, 
        query: str, 
        max_results: Optional[int] = None,
        enabled: Optional[bool] = None
    ) -> List[Dict]:
        """
        Google 검색 수행
        
        Args:
            query: 검색 쿼리 (원본 쿼리)
            max_results: 최대 결과 개수 (기본값: 5)
            enabled: SERP 검색 활성화 여부 (API 파라미터로 제어)
        
        Returns:
            검색 결과 리스트
        """
        # API 파라미터로 비활성화된 경우
        if enabled is False:
            logger.info("SERP 검색이 API 파라미터로 비활성화되었습니다.")
            return []
        
        # 환경변수로 비활성화된 경우
        if not self.enabled:
            logger.info("SERP 검색이 환경변수로 비활성화되었습니다.")
            return []
        
        if not self.api_key:
            logger.warning("SERP API 키가 설정되지 않았습니다.")
            return []
        
        try:
            logger.info(f"SERP 검색 시작: '{query}'")
            
            # 비동기 실행
            results = await asyncio.wait_for(
                self._call_serpapi(query, max_results or self.max_results),
                timeout=self.timeout
            )
            
            parsed_results = self._parse_results(results)
            logger.info(f"SERP 검색 완료: {len(parsed_results)}개 결과")
            
            return parsed_results
            
        except asyncio.TimeoutError:
            logger.error(f"SERP API 타임아웃 ({self.timeout}초)")
            return []
        except Exception as e:
            logger.error(f"SERP API 오류: {e}", exc_info=True)
            return []
    
    async def _call_serpapi(self, query: str, max_results: int) -> Dict:
        """
        SerpAPI 호출
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 개수
        
        Returns:
            SerpAPI 응답
        """
        # 비동기 실행을 위해 run_in_executor 사용
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_call_serpapi,
            query,
            max_results
        )
    
    def _sync_call_serpapi(self, query: str, max_results: int) -> Dict:
        """
        SerpAPI 동기 호출
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 개수
        
        Returns:
            SerpAPI 응답
        """
        # 쿼리 앞에 프리픽스 추가
        enhanced_query = f"[증상에 따른 영양제 또는 약 추천] {query}"
        
        params = {
            "q": enhanced_query,
            "location": "South Korea",
            "hl": "ko",
            "gl": "kr",
            "num": max_results,
            "api_key": self.api_key
        }
        
        logger.info(f"SERP 검색 쿼리: '{enhanced_query}'")
        
        search = GoogleSearch(params)
        return search.get_dict()
    
    def _parse_results(self, raw_results: Dict) -> List[Dict]:
        """
        SerpAPI 결과 파싱
        
        Args:
            raw_results: SerpAPI 원본 응답
        
        Returns:
            표준화된 검색 결과 리스트
        """
        parsed = []
        
        # Organic results 추출
        organic_results = raw_results.get("organic_results", [])
        
        for idx, result in enumerate(organic_results):
            parsed_result = {
                "position": idx + 1,
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "source": "google",
                "displayed_link": result.get("displayed_link", ""),
            }
            
            # 추가 정보 (있는 경우)
            if "date" in result:
                parsed_result["date"] = result["date"]
            
            if "rich_snippet" in result:
                parsed_result["rich_snippet"] = result["rich_snippet"]
            
            parsed.append(parsed_result)
        
        return parsed
    
    def get_status(self) -> Dict:
        """
        SERP 서비스 상태 조회
        
        Returns:
            서비스 상태 정보
        """
        return {
            "enabled": self.enabled,
            "api_key_configured": bool(self.api_key),
            "max_results": self.max_results,
            "timeout": self.timeout
        }


# 싱글톤 인스턴스
serp_service = SerpService()

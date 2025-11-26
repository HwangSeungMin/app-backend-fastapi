import requests
import time
from typing import List, Dict, Optional
from app.core.config import settings
from app.utils.logger import get_logger

config = settings
logger = get_logger(__name__)

class FoodSafetyAPIClient:
    """식약처 C003 API 클라이언트 (건강기능식품 품목제조신고)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.FOOD_SAFETY_API_KEY
        self.base_url = config.FOOD_SAFETY_BASE_URL
        
        if not self.api_key:
            raise ValueError("API 키가 설정되지 않았습니다.")
    
    def _make_request(self, endpoint: str, start_idx: int, end_idx: int) -> List[Dict]:
        """API 요청 실행"""
        url = f"{self.base_url}/{self.api_key}/{endpoint}/json/{start_idx}/{end_idx}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 응답 구조 확인
            if endpoint in data:
                return data[endpoint].get('row', [])
            
            logger.warning(f"예상치 못한 응답 구조: {list(data.keys())}")
            return []
            
        except requests.exceptions.JSONDecodeError:
            logger.error(f"JSON 파싱 실패 ({endpoint}). 응답 내용: {response.text[:500]}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패 ({endpoint}): {e}")
            return []
        except Exception as e:
            logger.error(f"데이터 처리 오류 ({endpoint}): {e}")
            return []
    
    def fetch_health_functional_food(
        self, 
        start_idx: int = 1, 
        end_idx: int = 1000
    ) -> List[Dict]:
        """C003: 건강기능식품 품목제조신고 데이터"""
        logger.info(f"C003 데이터 수집: {start_idx}~{end_idx}")
        return self._make_request('C003', start_idx, end_idx)
    
    def collect_all_data(
        self,
        batch_size: Optional[int] = None,
        max_items: Optional[int] = None,
        start_index: int = 1,
        end_index: Optional[int] = None
    ) -> List[Dict]:
        """C003 API 데이터 수집 (건강기능식품 품목제조신고)

        Args:
            batch_size: API 한 번 요청할 때 가져올 데이터 개수
            max_items: 수집할 최대 아이템 수 (None이면 전체 수집)
            start_index: 수집 시작 인덱스 (기본값: 1)
            end_index: 수집 종료 인덱스 (None이면 끝까지 또는 max_items까지)
        
        Returns:
            List[Dict]: C003 API 제품 데이터 리스트
        """
        batch_size = batch_size or config.API_BATCH_SIZE

        products = []

        # C003 데이터 수집
        logger.info(f"=== C003 데이터 수집 시작 (범위: {start_index} ~ {end_index if end_index else '끝'}) ===")
        if max_items:
            logger.info(f"최대 {max_items}개 아이템으로 제한")

        current_idx = start_index

        while True:
            # 종료 조건 체크
            if end_index and current_idx > end_index:
                logger.info(f"종료 인덱스({end_index})에 도달하여 수집 중단")
                break

            if max_items and len(products) >= max_items:
                logger.info(f"최대 아이템 수({max_items})에 도달하여 수집 중단")
                break

            # 배치 크기 계산
            if end_index:
                remaining_range = end_index - current_idx + 1
                current_batch_size = min(batch_size, remaining_range)
            else:
                current_batch_size = batch_size
            
            if max_items:
                remaining_items = max_items - len(products)
                current_batch_size = min(current_batch_size, remaining_items)

            if current_batch_size <= 0:
                break

            batch_products = self.fetch_health_functional_food(
                current_idx,
                current_idx + current_batch_size - 1
            )

            if not batch_products:
                logger.info("더 이상 데이터가 없습니다.")
                break

            products.extend(batch_products)
            logger.info(f"누적 제품 수: {len(products)}")

            current_idx += current_batch_size
            time.sleep(config.API_REQUEST_DELAY)

        logger.info(f"✓ C003 데이터 수집 완료: {len(products)}개")

        return products
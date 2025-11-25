"""
초기 데이터 구축 스크립트
식약처 API에서 데이터를 수집하고 ElasticSearch에 색인
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.api_client import FoodSafetyAPIClient
from data.data_processor import DataProcessor
from app.search.elasticsearch_manager import ElasticsearchManager
from app.utils.logger import get_logger
from elasticsearch import helpers
import argparse

logger = get_logger(__name__)

def main():
    """메인 실행 함수"""
    
    parser = argparse.ArgumentParser(description='건강기능식품 RAG 데이터 구축')
    parser.add_argument('--api-key', type=str, help='식약처 API 키')
    parser.add_argument('--skip-collect', action='store_true', help='데이터 수집 건너뛰기 (저장된 파일 사용)')
    parser.add_argument('--data-file', type=str, default='data/raw/health_supplements_data.json', help='데이터 파일 경로')
    parser.add_argument('--recreate-index', action='store_true', help='기존 인덱스 삭제 후 재생성')
    parser.add_argument('--max-items', type=int, default=None, help='수집할 최대 아이템 수 (테스트용, 예: 1000)')
    parser.add_argument('--start-index', type=int, default=1, help='수집 시작 인덱스')
    parser.add_argument('--end-index', type=int, default=None, help='수집 종료 인덱스')
    parser.add_argument('--category', type=str, default=None, help='특정 카테고리만 필터링 (예: 비타민)')
    parser.add_argument('--target-api', type=str, default='ALL', help='특정 API만 색인 (ALL, C003)')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info(f"건강기능식품 RAG 시스템 데이터 구축 시작 (대상: {args.target_api})")
    if args.category:
        logger.info(f"필터링 카테고리: {args.category}")
    if args.start_index > 1 or args.end_index:
        logger.info(f"수집 범위: {args.start_index} ~ {args.end_index if args.end_index else '끝'}")
    logger.info("=" * 60)
    
    try:
        # API 클라이언트 및 ES 매니저 초기화
        if not args.api_key:
            logger.error("API 키가 필요합니다. --api-key 옵션을 사용하세요.")
            return
        
        api_client = FoodSafetyAPIClient(api_key=args.api_key)
        es_manager = ElasticsearchManager()
        processor = DataProcessor()

        # C003 또는 ALL인 경우: 기본 색인 프로세스 (기존 로직)
        if args.target_api in ['ALL', 'C003']:
            logger.info("\n[1단계] 기본 데이터(C003) 수집 및 색인")
            
            # 데이터 수집
            collected_data = api_client.collect_all_data(
                max_items=args.max_items,
                include_additional=False,
                start_index=args.start_index,
                end_index=args.end_index
            )
            
            products = collected_data['products']
            classifications = collected_data['classifications']
            
            logger.info(f"✓ 수집 완료 - 제품: {len(products)}, 분류: {len(classifications)}")

            # 전처리
            processed_data = processor.process_product_data(
                products, 
                classifications,
                kibana_optimized=True
            )
            
            # 필터링
            if args.category:
                processed_data = [
                    doc for doc in processed_data 
                    if args.category in doc.get('classification', {}).get('category', '') or 
                       args.category in doc.get('product_name', '')
                ]
            
            # 인덱스 생성 (C003일 때만 재생성 옵션 적용)
            es_manager.create_index(delete_if_exists=args.recreate_index)
            
            # 색인
            es_manager.index_documents(processed_data)
            
        else:
            logger.error(f"지원하지 않는 API 대상입니다: {args.target_api}")
            return

        # 통계 확인
        logger.info("\n[최종] 인덱스 통계 확인")
        stats = es_manager.get_index_stats()
        logger.info(f"인덱스명: {stats['index_name']}")
        logger.info(f"문서 개수: {stats['document_count']:,}")
        
    except KeyboardInterrupt:
        logger.warning("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"\n오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
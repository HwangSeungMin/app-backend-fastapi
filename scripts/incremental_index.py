"""
증분 색인 스크립트 (Incremental Indexing)

이미 색인된 데이터를 제외하고 신규 데이터만 색인합니다.
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.api_client import FoodSafetyAPIClient
from data.data_processor import DataProcessor
from app.search.elasticsearch_manager import ElasticsearchManager
from app.utils.logger import get_logger
import argparse

logger = get_logger(__name__)


def get_existing_product_ids(es_manager: ElasticsearchManager) -> set:
    """
    ElasticSearch에서 기존 제품 ID 목록 조회
    
    Returns:
        set: 기존 제품 ID 집합
    """
    logger.info("기존 제품 ID 조회 중...")
    
    try:
        # 모든 문서의 ID 조회
        query = {
            "size": 10000,  # 최대 10,000개
            "_source": ["product_id"],
            "query": {
                "match_all": {}
            }
        }
        
        results = es_manager.es.search(
            index=es_manager.index_name,
            body=query,
            scroll='2m'
        )
        
        existing_ids = set()
        scroll_id = results['_scroll_id']
        
        # 첫 번째 배치
        for hit in results['hits']['hits']:
            product_id = hit['_source'].get('product_id')
            if product_id:
                existing_ids.add(product_id)
        
        # 스크롤로 나머지 데이터 조회
        while len(results['hits']['hits']) > 0:
            results = es_manager.es.scroll(
                scroll_id=scroll_id,
                scroll='2m'
            )
            
            for hit in results['hits']['hits']:
                product_id = hit['_source'].get('product_id')
                if product_id:
                    existing_ids.add(product_id)
        
        # 스크롤 정리
        es_manager.es.clear_scroll(scroll_id=scroll_id)
        
        logger.info(f"✓ 기존 제품 ID {len(existing_ids)}개 조회 완료")
        
        return existing_ids
        
    except Exception as e:
        logger.error(f"기존 제품 ID 조회 실패: {e}")
        return set()


def filter_new_documents(documents: list, existing_ids: set) -> list:
    """
    신규 문서만 필터링
    
    Args:
        documents: 전체 문서 리스트
        existing_ids: 기존 제품 ID 집합
    
    Returns:
        list: 신규 문서 리스트
    """
    logger.info("신규 문서 필터링 중...")
    
    new_documents = []
    duplicate_count = 0
    
    for doc in documents:
        product_id = doc.get('product_id')
        
        if product_id and product_id not in existing_ids:
            new_documents.append(doc)
        else:
            duplicate_count += 1
    
    logger.info(f"✓ 필터링 완료")
    logger.info(f"  - 전체 문서: {len(documents)}개")
    logger.info(f"  - 중복 문서: {duplicate_count}개")
    logger.info(f"  - 신규 문서: {len(new_documents)}개")
    
    return new_documents


def main():
    """메인 실행 함수"""
    
    parser = argparse.ArgumentParser(description='건강기능식품 증분 색인')
    parser.add_argument('--api-key', type=str, help='식약처 API 키')
    parser.add_argument('--skip-collect', action='store_true', help='데이터 수집 건너뛰기')
    parser.add_argument('--data-file', type=str, default='data/raw/health_supplements_data.json', help='데이터 파일 경로')
    parser.add_argument('--max-items', type=int, default=None, help='수집할 최대 아이템 수')
    parser.add_argument('--batch-size', type=int, default=100, help='색인 배치 크기')
    parser.add_argument('--dry-run', action='store_true', help='실제 색인 없이 테스트만')
    parser.add_argument('--include-additional', action='store_true', help='추가 API 데이터 포함 (I0030, I2790, I0040)')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("건강기능식품 증분 색인 시작")
    logger.info("=" * 60)
    
    try:
        processed_data = None
        
        # 1단계: 데이터 수집
        if not args.skip_collect:
            logger.info("\n[1단계] 식약처 API 데이터 수집")
            logger.info("-" * 60)
            
            if not args.api_key:
                logger.error("API 키가 필요합니다. --api-key 옵션을 사용하세요.")
                logger.info("또는 환경 변수 FOOD_SAFETY_API_KEY를 설정하세요.")
                return
            
            api_client = FoodSafetyAPIClient(api_key=args.api_key)
            
            # 추가 API 데이터 포함 여부
            if args.include_additional:
                logger.info("추가 API 데이터 포함: I0030, I2790, I0040")
                result = api_client.collect_all_data(
                    max_items=args.max_items,
                    include_additional=True
                )
                products = result['products']
                classifications = result['classifications']
                
                logger.info(f"✓ 수집 완료")
                logger.info(f"  - 제품: {len(products)}개")
                logger.info(f"  - 분류: {len(classifications)}개")
                logger.info(f"  - 기능성 원료: {len(result['ingredients'])}개")
                logger.info(f"  - 영업신고: {len(result['businesses'])}개")
                logger.info(f"  - 부작용 정보: {len(result['side_effects'])}개")
            else:
                result = api_client.collect_all_data(max_items=args.max_items)
                products = result['products']
                classifications = result['classifications']
                
                logger.info(f"✓ 수집 완료 - 제품: {len(products)}, 분류: {len(classifications)}")
            
            # 2단계: 데이터 전처리
            logger.info("\n[2단계] 데이터 전처리")
            logger.info("-" * 60)
            
            processor = DataProcessor()
            
            if args.include_additional:
                processed_data = processor.process_product_data(
                    products, 
                    classifications,
                    ingredients=result.get('ingredients'),
                    businesses=result.get('businesses'),
                    side_effects=result.get('side_effects'),
                    kibana_optimized=True
                )
            else:
                processed_data = processor.process_product_data(
                    products, 
                    classifications,
                    kibana_optimized=True
                )
            
            # 데이터 저장
            os.makedirs(os.path.dirname(args.data_file), exist_ok=True)
            processor.save_to_json(processed_data, args.data_file)
            
            logger.info(f"✓ 전처리 완료 - {len(processed_data)}개 문서")
        
        else:
            logger.info("\n[1-2단계] 저장된 데이터 로드")
            logger.info("-" * 60)
            
            if not os.path.exists(args.data_file):
                logger.error(f"데이터 파일을 찾을 수 없습니다: {args.data_file}")
                return
            
            processor = DataProcessor()
            processed_data = processor.load_from_json(args.data_file)
            
            logger.info(f"✓ 데이터 로드 완료 - {len(processed_data)}개 문서")
        
        # 3단계: ElasticSearch 연결 및 기존 ID 조회
        logger.info("\n[3단계] ElasticSearch 연결 및 기존 데이터 확인")
        logger.info("-" * 60)
        
        es_manager = ElasticsearchManager()
        
        # 인덱스 존재 확인
        if not es_manager.es.indices.exists(index=es_manager.index_name):
            logger.warning(f"인덱스가 존재하지 않습니다: {es_manager.index_name}")
            logger.info("인덱스를 생성합니다...")
            es_manager.create_index(delete_if_exists=False)
            existing_ids = set()
        else:
            # 기존 제품 ID 조회
            existing_ids = get_existing_product_ids(es_manager)
        
        # 4단계: 신규 문서 필터링
        logger.info("\n[4단계] 신규 문서 필터링")
        logger.info("-" * 60)
        
        new_documents = filter_new_documents(processed_data, existing_ids)
        
        if len(new_documents) == 0:
            logger.info("\n신규 문서가 없습니다. 색인을 종료합니다.")
            return
        
        # 5단계: 신규 문서 색인
        if args.dry_run:
            logger.info("\n[5단계] Dry-run 모드 (실제 색인 안 함)")
            logger.info("-" * 60)
            logger.info(f"색인될 문서: {len(new_documents)}개")
            logger.info("\n샘플 문서 (처음 3개):")
            for i, doc in enumerate(new_documents[:3], 1):
                logger.info(f"\n[{i}] {doc.get('product_name', 'N/A')}")
                logger.info(f"  - ID: {doc.get('product_id', 'N/A')}")
                logger.info(f"  - 회사: {doc.get('company_name', 'N/A')}")
        else:
            logger.info("\n[5단계] 신규 문서 벡터화 및 색인")
            logger.info("-" * 60)
            
            # 배치 크기 설정
            original_batch_size = es_manager.batch_size
            es_manager.batch_size = args.batch_size
            
            es_manager.index_documents(new_documents)
            
            # 원래 배치 크기로 복원
            es_manager.batch_size = original_batch_size
            
            logger.info("✓ 색인 완료")
        
        # 6단계: 인덱스 통계 확인
        logger.info("\n[6단계] 인덱스 통계 확인")
        logger.info("-" * 60)
        
        stats = es_manager.get_index_stats()
        logger.info(f"인덱스명: {stats['index_name']}")
        logger.info(f"문서 개수: {stats['document_count']:,}")
        logger.info(f"인덱스 크기: {stats['size']:,} bytes")
        
        if not args.dry_run:
            logger.info(f"\n이번 색인:")
            logger.info(f"  - 신규 추가: {len(new_documents)}개")
            logger.info(f"  - 중복 제외: {len(processed_data) - len(new_documents)}개")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ 증분 색인 완료!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"\n오류 발생: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

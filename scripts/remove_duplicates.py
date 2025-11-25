"""
중복 문서 제거 스크립트

ElasticSearch 인덱스에서 중복된 문서를 찾아 제거합니다.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.search.elasticsearch_manager import ElasticsearchManager
from app.utils.logger import get_logger
import argparse
from collections import defaultdict

logger = get_logger(__name__)


def find_duplicates(es_manager: ElasticsearchManager) -> dict:
    """
    중복 문서 찾기
    
    Returns:
        dict: {product_id: [doc_ids]}
    """
    logger.info("중복 문서 검색 중...")
    
    try:
        # 모든 문서 조회
        query = {
            "size": 10000,
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
        
        product_id_map = defaultdict(list)
        scroll_id = results['_scroll_id']
        
        # 첫 번째 배치
        for hit in results['hits']['hits']:
            product_id = hit['_source'].get('product_id')
            doc_id = hit['_id']
            
            if product_id:
                product_id_map[product_id].append(doc_id)
        
        # 스크롤로 나머지 데이터 조회
        while len(results['hits']['hits']) > 0:
            results = es_manager.es.scroll(
                scroll_id=scroll_id,
                scroll='2m'
            )
            
            for hit in results['hits']['hits']:
                product_id = hit['_source'].get('product_id')
                doc_id = hit['_id']
                
                if product_id:
                    product_id_map[product_id].append(doc_id)
        
        # 스크롤 정리
        es_manager.es.clear_scroll(scroll_id=scroll_id)
        
        # 중복만 필터링
        duplicates = {
            pid: doc_ids 
            for pid, doc_ids in product_id_map.items() 
            if len(doc_ids) > 1
        }
        
        logger.info(f"✓ 검색 완료")
        logger.info(f"  - 전체 제품: {len(product_id_map)}개")
        logger.info(f"  - 중복 제품: {len(duplicates)}개")
        
        return duplicates
        
    except Exception as e:
        logger.error(f"중복 검색 실패: {e}")
        return {}


def remove_duplicates(es_manager: ElasticsearchManager, duplicates: dict, dry_run: bool = False):
    """
    중복 문서 제거 (첫 번째 문서만 유지)
    
    Args:
        es_manager: ElasticSearch 매니저
        duplicates: 중복 문서 맵
        dry_run: 실제 삭제 안 함
    """
    logger.info("\n중복 문서 제거 중...")
    
    total_removed = 0
    
    for product_id, doc_ids in duplicates.items():
        # 첫 번째 문서는 유지, 나머지 삭제
        keep_id = doc_ids[0]
        remove_ids = doc_ids[1:]
        
        logger.info(f"\n제품 ID: {product_id}")
        logger.info(f"  - 유지: {keep_id}")
        logger.info(f"  - 삭제: {len(remove_ids)}개")
        
        if not dry_run:
            for doc_id in remove_ids:
                try:
                    es_manager.es.delete(
                        index=es_manager.index_name,
                        id=doc_id
                    )
                    total_removed += 1
                except Exception as e:
                    logger.error(f"  문서 삭제 실패 ({doc_id}): {e}")
    
    if dry_run:
        logger.info(f"\n✓ Dry-run 완료 (실제 삭제 안 함)")
        logger.info(f"  - 삭제 예정: {sum(len(ids) - 1 for ids in duplicates.values())}개")
    else:
        logger.info(f"\n✓ 제거 완료")
        logger.info(f"  - 삭제된 문서: {total_removed}개")


def main():
    """메인 실행 함수"""
    
    parser = argparse.ArgumentParser(description='중복 문서 제거')
    parser.add_argument('--dry-run', action='store_true', help='실제 삭제 없이 테스트만')
    parser.add_argument('--show-samples', action='store_true', help='중복 샘플 표시')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("중복 문서 제거 시작")
    logger.info("=" * 60)
    
    try:
        # ElasticSearch 연결
        logger.info("\n[1단계] ElasticSearch 연결")
        logger.info("-" * 60)
        
        es_manager = ElasticsearchManager()
        
        if not es_manager.es.indices.exists(index=es_manager.index_name):
            logger.error(f"인덱스가 존재하지 않습니다: {es_manager.index_name}")
            return
        
        logger.info(f"✓ 연결 완료: {es_manager.index_name}")
        
        # 중복 찾기
        logger.info("\n[2단계] 중복 문서 검색")
        logger.info("-" * 60)
        
        duplicates = find_duplicates(es_manager)
        
        if len(duplicates) == 0:
            logger.info("\n중복 문서가 없습니다.")
            return
        
        # 샘플 표시
        if args.show_samples:
            logger.info("\n중복 샘플 (처음 5개):")
            for i, (product_id, doc_ids) in enumerate(list(duplicates.items())[:5], 1):
                logger.info(f"\n[{i}] 제품 ID: {product_id}")
                logger.info(f"  - 중복 개수: {len(doc_ids)}개")
                logger.info(f"  - 문서 IDs: {', '.join(doc_ids[:3])}...")
        
        # 중복 제거
        logger.info("\n[3단계] 중복 문서 제거")
        logger.info("-" * 60)
        
        remove_duplicates(es_manager, duplicates, dry_run=args.dry_run)
        
        # 통계 확인
        logger.info("\n[4단계] 인덱스 통계 확인")
        logger.info("-" * 60)
        
        stats = es_manager.get_index_stats()
        logger.info(f"인덱스명: {stats['index_name']}")
        logger.info(f"문서 개수: {stats['document_count']:,}")
        logger.info(f"인덱스 크기: {stats['size']:,} bytes")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ 중복 제거 완료!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"\n오류 발생: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
인덱스 업데이트 스크립트
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.search.elasticsearch_manager import ElasticsearchManager
from data.data_processor import DataProcessor
from app.utils.logger import get_logger
import argparse

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description='ElasticSearch 인덱스 관리')
    parser.add_argument('action', choices=['create', 'delete', 'recreate', 'stats', 'reindex'], 
                       help='실행할 작업')
    parser.add_argument('--data-file', type=str, default='data/raw/health_supplements_data.json',
                       help='데이터 파일 경로 (reindex 작업시 필요)')
    
    args = parser.parse_args()
    
    try:
        es_manager = ElasticsearchManager()
        
        if args.action == 'create':
            logger.info("인덱스 생성 중...")
            es_manager.create_index(delete_if_exists=False)
            logger.info("✓ 인덱스 생성 완료")
        
        elif args.action == 'delete':
            logger.info("인덱스 삭제 중...")
            es_manager.delete_index()
            logger.info("✓ 인덱스 삭제 완료")
        
        elif args.action == 'recreate':
            logger.info("인덱스 재생성 중...")
            es_manager.create_index(delete_if_exists=True)
            logger.info("✓ 인덱스 재생성 완료")
        
        elif args.action == 'stats':
            logger.info("인덱스 통계 조회 중...")
            stats = es_manager.get_index_stats()
            
            print("\n" + "=" * 60)
            print("인덱스 통계")
            print("=" * 60)
            print(f"인덱스명: {stats['index_name']}")
            print(f"문서 개수: {stats['document_count']:,}")
            print(f"인덱스 크기: {stats['size']:,} bytes ({stats['size'] / (1024*1024):.2f} MB)")
            print("=" * 60)
        
        elif args.action == 'reindex':
            if not os.path.exists(args.data_file):
                logger.error(f"데이터 파일을 찾을 수 없습니다: {args.data_file}")
                return
            
            logger.info("데이터 로드 중...")
            processor = DataProcessor()
            data = processor.load_from_json(args.data_file)
            
            logger.info("인덱스 재생성 중...")
            es_manager.create_index(delete_if_exists=True)
            
            logger.info("문서 색인 중...")
            es_manager.index_documents(data)
            
            logger.info("✓ 재색인 완료")
            
            # 통계 출력
            stats = es_manager.get_index_stats()
            print(f"\n✓ {stats['document_count']:,}개 문서 색인 완료")
    
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
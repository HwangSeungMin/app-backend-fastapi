from elasticsearch import Elasticsearch, helpers
from typing import List, Dict
import numpy as np
import time
from app.core.elasticsearch_config import get_elasticsearch_client, get_index_settings
from app.core.config import settings
from app.search.embeddings import EmbeddingGenerator
from app.utils.logger import get_logger

config = settings
logger = get_logger(__name__)

class ElasticsearchManager:
    """ElasticSearch 인덱스 관리"""
    
    def __init__(self, wait_timeout=60):
        logger.info(f"ElasticSearch 연결 시도 시작")
        logger.info(f"호스트: {config.ES_HOST}:{config.ES_PORT}")
        
        try:
            # 연결 객체 생성
            self.es = get_elasticsearch_client()
            logger.info("ElasticSearch 클라이언트 객체 생성 완료")
            
            # 인덱스 이름 설정
            self.index_name = config.ES_INDEX_NAME
            logger.info(f"인덱스명: {self.index_name}")
            
            # 배치 크기 설정
            self.batch_size = 100  # 기본 배치 크기
            
            # 연결 확인 (대기 시간 포함)
            logger.info(f"연결 확인 시작 (최대 {wait_timeout}초 대기)")
            
            if not self._wait_for_connection(wait_timeout):
                error_msg = (
                    f"ElasticSearch 연결 실패\n"
                    f"주소: {config.ES_HOST}:{config.ES_PORT}\n"
                    f"확인사항:\n"
                    f"1. curl http://localhost:9200 명령으로 응답 확인\n"
                    f"2. 방화벽에서 9200 포트 차단 여부 확인\n"
                    f"3. Docker 네트워크 설정 확인"
                )
                logger.error(error_msg)
                raise ConnectionError(error_msg)
            
            # 임베딩 생성기 초기화
            self.embedding_generator = EmbeddingGenerator()
            
            logger.info(f"✓ ElasticSearch 연결 성공: {config.ES_HOST}:{config.ES_PORT}")
            
        except Exception as e:
            logger.error(f"ElasticsearchManager 초기화 실패: {type(e).__name__}")
            logger.error(f"상세 오류: {str(e)}")
            raise
    
    def _wait_for_connection(self, timeout=60):
        """ElasticSearch 연결 대기"""
        start_time = time.time()
        attempt = 0
        last_error = None
        
        logger.info("연결 대기 시작...")
        
        while time.time() - start_time < timeout:
            attempt += 1
            elapsed = int(time.time() - start_time)
            
            try:
                logger.info(f"[시도 {attempt}] Ping 테스트 중... ({elapsed}/{timeout}초)")
                
                if self.es.ping():
                    logger.info(f"✓ Ping 성공 (시도 {attempt}회, {elapsed}초 경과)")
                    
                    # 추가 정보 조회
                    try:
                        info = self.es.info()
                        logger.info(f"클러스터: {info['cluster_name']}, 버전: {info['version']['number']}")
                    except Exception as e:
                        logger.warning(f"정보 조회 실패: {e}")
                    
                    return True
                else:
                    logger.warning(f"[시도 {attempt}] Ping 응답 없음")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"[시도 {attempt}] 연결 오류: {type(e).__name__} - {str(e)[:100]}")
            
            time.sleep(2)
        
        logger.error(f"✗ 연결 시간 초과 ({timeout}초)")
        if last_error:
            logger.error(f"마지막 오류: {type(last_error).__name__} - {str(last_error)}")
        
        return False
    
    def create_index(self, delete_if_exists: bool = False):
        """인덱스 생성"""
        
        if self.es.indices.exists(index=self.index_name):
            if delete_if_exists:
                self.es.indices.delete(index=self.index_name)
                logger.info(f"기존 인덱스 삭제: {self.index_name}")
                # 인덱스 삭제 후 잠시 대기
                time.sleep(1)
            else:
                logger.warning(f"인덱스가 이미 존재합니다: {self.index_name}. 기존 인덱스를 사용합니다.")
                return
        
        # 인덱스 설정 가져오기
        try:
            index_settings = get_index_settings()  # Kibana 최적화 설정 사용
            logger.info(f"새 인덱스 생성: {self.index_name}")
            self.es.indices.create(index=self.index_name, body=index_settings)
            logger.info(f"✓ 인덱스 생성 완료: {self.index_name}")
        except Exception as e:
            logger.error(f"인덱스 생성 실패: {e}")
            raise
    
    def index_documents(
        self,
        documents: List[Dict],
        batch_size: int = 100
    ):
        """문서 색인 (벡터 포함)"""

        total_docs = len(documents)
        logger.info(f"문서 색인 시작: {total_docs}개")

        # 임베딩 생성
        logger.info("임베딩 생성 중...")
        embedding_texts = [doc['embedding_text'] for doc in documents]

        # 배치 단위로 임베딩 생성 (메모리 효율성)
        embeddings = []
        embedding_batch_size = 32  # 임베딩 생성 배치 크기

        for i in range(0, len(embedding_texts), embedding_batch_size):
            batch_texts = embedding_texts[i:i + embedding_batch_size]
            batch_embeddings = self.embedding_generator.generate(batch_texts)
            embeddings.extend(batch_embeddings)

            progress = min(i + embedding_batch_size, len(embedding_texts))
            percentage = (progress / len(embedding_texts)) * 100
            logger.info(f"  임베딩 생성: {progress}/{len(embedding_texts)} ({percentage:.1f}%)")

        logger.info(f"✓ 임베딩 생성 완료: {len(embeddings)}개")

        # 색인 액션 생성 및 실행
        logger.info("ElasticSearch 색인 시작...")
        actions = []
        total_success = 0
        total_failed = 0

        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            action = {
                "_index": self.index_name,
                "_id": doc['product_id'],
                "_source": {
                    **doc,
                    "embedding_vector": embedding.tolist()
                }
            }
            actions.append(action)

            # 배치 단위로 색인
            if len(actions) >= batch_size:
                success, failed = helpers.bulk(
                    self.es,
                    actions,
                    raise_on_error=False
                )
                total_success += success
                total_failed += len(failed) if failed else 0

                progress = idx + 1
                percentage = (progress / total_docs) * 100
                logger.info(f"  색인 진행: {progress}/{total_docs} ({percentage:.1f}%) - 성공: {success}, 실패: {len(failed) if failed else 0}")
                actions = []

        # 나머지 문서 색인
        if actions:
            success, failed = helpers.bulk(
                self.es,
                actions,
                raise_on_error=False
            )
            total_success += success
            total_failed += len(failed) if failed else 0
            logger.info(f"  최종 배치 색인 완료 - 성공: {success}, 실패: {len(failed) if failed else 0}")

        # 인덱스 새로고침
        self.es.indices.refresh(index=self.index_name)

        logger.info(f"✓ 전체 색인 완료: 총 {total_docs}개 문서 (성공: {total_success}, 실패: {total_failed})")

    def update_documents(
        self,
        updates: List[Dict],
        batch_size: int = 100
    ):
        """문서 부분 업데이트 (Bulk Update)
        
        Args:
            updates: 업데이트할 문서 리스트. 각 항목은 {'_id': ..., 'doc': {...}} 형태여야 함.
            batch_size: 배치 크기
        """
        total_updates = len(updates)
        logger.info(f"문서 업데이트 시작: {total_updates}개")
        
        actions = []
        for update in updates:
            action = {
                '_op_type': 'update',
                '_index': self.index_name,
                '_id': update['_id'],
                'doc': update['doc']
            }
            actions.append(action)
            
        # 배치 처리
        for i in range(0, len(actions), batch_size):
            batch_actions = actions[i:i + batch_size]
            
            success, failed = helpers.bulk(
                self.es,
                batch_actions,
                stats_only=True,
                raise_on_error=False
            )
            
            logger.info(f"  업데이트 배치 {i//batch_size + 1} 완료: 성공 {success}, 실패 {failed}")
            
        logger.info("✓ 전체 업데이트 완료")
    
    def get_index_stats(self) -> Dict:
        """인덱스 통계 조회"""
        
        stats = self.es.indices.stats(index=self.index_name)
        doc_count = stats['indices'][self.index_name]['total']['docs']['count']
        
        return {
            'index_name': self.index_name,
            'document_count': doc_count,
            'size': stats['indices'][self.index_name]['total']['store']['size_in_bytes']
        }
    
    def delete_index(self):
        """인덱스 삭제"""
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            logger.info(f"인덱스 삭제 완료: {self.index_name}")
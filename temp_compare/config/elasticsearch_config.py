from elasticsearch import Elasticsearch
from config.settings import get_config
import logging

config = get_config()
logger = logging.getLogger(__name__)

def get_elasticsearch_client():
    """ElasticSearch 클라이언트 생성"""

    # URL 구성
    es_url = f"http://{config.ES_HOST}:{config.ES_PORT}"

    print(f"[DEBUG] ElasticSearch URL: {es_url}")

    # Elasticsearch 8.x 서버와 호환되도록 설정
    client = Elasticsearch(
        [es_url],
        request_timeout=30,
        max_retries=3,
        retry_on_timeout=True,
        # 버전 8과 호환되도록 헤더 설정
        headers={"Accept": "application/vnd.elasticsearch+json; compatible-with=8"}
    )

    return client

def check_nori_plugin(es_client):
    """Nori 플러그인 설치 여부 확인"""
    try:
        plugins = es_client.cat.plugins(format='json')
        for plugin in plugins:
            if 'analysis-nori' in plugin.get('component', ''):
                logger.info("✓ Nori 플러그인이 설치되어 있습니다.")
                return True
        logger.warning("⚠ Nori 플러그인이 설치되어 있지 않습니다. Standard analyzer를 사용합니다.")
        return False
    except Exception as e:
        logger.warning(f"플러그인 확인 중 오류: {e}. Standard analyzer를 사용합니다.")
        return False

def get_index_settings(use_nori=None, kibana_optimized=True):
    """인덱스 설정 반환

    Args:
        use_nori: Nori 플러그인 사용 여부 (None이면 자동 감지)
        kibana_optimized: Kibana 대시보드 최적화 여부 (기본: True)
    """

    # Nori 사용 여부가 지정되지 않은 경우, 자동으로 확인
    if use_nori is None:
        es_client = get_elasticsearch_client()
        use_nori = check_nori_plugin(es_client)

    # Analysis 설정 구성
    analysis_settings = {
        "tokenizer": {
            "ngram_tokenizer": {
                "type": "ngram",
                "min_gram": 2,
                "max_gram": 3,
                "token_chars": ["letter", "digit"]
            }
        },
        "analyzer": {}
    }

    # Nori 사용 가능 시 한국어 분석기 추가
    if use_nori:
        analysis_settings["analyzer"]["korean"] = {
            "type": "custom",
            "tokenizer": "nori_tokenizer",
            "filter": ["lowercase", "nori_part_of_speech"]
        }
        analysis_settings["analyzer"]["korean_ngram"] = {
            "type": "custom",
            "tokenizer": "ngram_tokenizer",
            "filter": ["lowercase"]
        }
        main_analyzer = "korean"
        ngram_analyzer = "korean_ngram"
    else:
        # Nori 없이도 한국어 검색 가능하도록 설정
        analysis_settings["analyzer"]["korean"] = {
            "type": "standard"
        }
        analysis_settings["analyzer"]["korean_ngram"] = {
            "type": "custom",
            "tokenizer": "ngram_tokenizer",
            "filter": ["lowercase"]
        }
        main_analyzer = "standard"
        ngram_analyzer = "korean_ngram"

    # 기본 매핑
    mappings = {
        "properties": {
            # === 기본 정보 ===
            "product_id": {"type": "keyword"},
            "product_name": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "keyword": {"type": "keyword"},  # Kibana 집계용
                    "ngram": {
                        "type": "text",
                        "analyzer": ngram_analyzer
                    }
                }
            },
            "company_name": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "keyword": {"type": "keyword"},  # Kibana 집계용
                    "ngram": {"type": "text", "analyzer": ngram_analyzer}
                }
            },
            
            # === 날짜 필드 (Kibana 시계열 분석용) ===
            "report_date": {
                "type": "date", 
                "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis"
            },
            
            # === 원재료 정보 ===
            "raw_materials": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "keyword": {"type": "keyword"},  # Kibana 집계용
                    "ngram": {"type": "text", "analyzer": ngram_analyzer}
                }
            },
            
            # === 주요 기능 ===
            "primary_function": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "keyword": {"type": "keyword"},  # Kibana 집계용
                    "ngram": {"type": "text", "analyzer": ngram_analyzer}
                }
            },
            
            # === 분류 정보 ===
            "classification": {
                "properties": {
                    "category": {"type": "keyword"},  # Kibana 집계용
                    "detail_category": {"type": "keyword"},  # Kibana 집계용
                    "function_content": {
                        "type": "text",
                        "analyzer": main_analyzer,
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "ngram": {"type": "text", "analyzer": ngram_analyzer}
                        }
                    },
                    "intake_method": {
                        "type": "text",
                        "analyzer": main_analyzer
                    },
                    "intake_caution": {
                        "type": "text",
                        "analyzer": main_analyzer
                    }
                }
            },
            
            # === 메타데이터 ===
            "metadata": {
                "properties": {
                    "manufacturer": {
                        "type": "text",
                        "analyzer": main_analyzer,
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "distribution_company": {
                        "type": "text",
                        "analyzer": main_analyzer,
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "update_date": {"type": "date"}
                }
            },
            
            # === 임베딩 벡터 ===
            "embedding_vector": {
                "type": "dense_vector",
                "dims": config.EMBEDDING_DIM,
                "index": True,
                "similarity": "cosine"
            },
            "embedding_text": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "ngram": {"type": "text", "analyzer": ngram_analyzer}
                }
            }
        }
    }
    
    # Kibana 최적화 필드 추가
    if kibana_optimized:
        # 색인 시간 (자동 추가)
        mappings["properties"]["indexed_at"] = {"type": "date"}
        mappings["properties"]["updated_at"] = {"type": "date"}
        
        # 통계 필드
        mappings["properties"]["stats"] = {
            "properties": {
                "view_count": {"type": "integer"},
                "search_count": {"type": "integer"},
                "popularity_score": {"type": "float"}
            }
        }
        
        # 성분 개수
        mappings["properties"]["ingredient_count"] = {"type": "integer"}
        
        # 가격 범위 (선택)
        mappings["properties"]["price_range"] = {"type": "keyword"}
        
        # 데이터 출처
        if "metadata" not in mappings["properties"]:
            mappings["properties"]["metadata"] = {"properties": {}}
        
        mappings["properties"]["metadata"]["properties"]["source"] = {"type": "keyword"}
        mappings["properties"]["metadata"]["properties"]["version"] = {"type": "keyword"}

    return {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "refresh_interval": "1s",  # Kibana 실시간 업데이트
            "analysis": analysis_settings
        },
        "mappings": mappings
    }
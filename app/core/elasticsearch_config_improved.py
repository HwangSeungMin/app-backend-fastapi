"""
개선된 Elasticsearch 인덱스 설정
C003 API 데이터 구조를 완전히 반영
"""
from elasticsearch import Elasticsearch
from app.core.config import settings
import logging

config = settings
logger = logging.getLogger(__name__)

def get_elasticsearch_client():
    """ElasticSearch 클라이언트 생성"""
    es_url = f"http://{config.ES_HOST}:{config.ES_PORT}"
    
    client = Elasticsearch(
        [es_url],
        request_timeout=30,
        max_retries=3,
        retry_on_timeout=True,
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

def get_improved_index_settings(use_nori=None):
    """개선된 인덱스 설정 반환 (C003 API 완전 지원)
    
    Args:
        use_nori: Nori 플러그인 사용 여부 (None이면 자동 감지)
    """
    
    # Nori 사용 여부 확인
    if use_nori is None:
        es_client = get_elasticsearch_client()
        use_nori = check_nori_plugin(es_client)
    
    # Analysis 설정
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
    
    # Nori 분석기 설정
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
    
    # 개선된 매핑 (C003 API 완전 지원)
    mappings = {
        "properties": {
            # ========== 기본 정보 ==========
            "product_id": {
                "type": "keyword"
            },
            "product_name": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngram": {"type": "text", "analyzer": ngram_analyzer}
                }
            },
            "company_name": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngram": {"type": "text", "analyzer": ngram_analyzer}
                }
            },
            
            # ========== 날짜 정보 ==========
            "report_date": {
                "type": "date",
                "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis"
            },
            "last_update_date": {
                "type": "date",
                "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis"
            },
            "created_date": {
                "type": "date",
                "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis"
            },
            
            # ========== 제품 형태 (NEW!) ==========
            "product_shape": {
                "type": "keyword"  # 캡슐, 정제, 분말, 액상 등
            },
            
            # ========== 원재료 정보 ==========
            "raw_materials": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngram": {"type": "text", "analyzer": ngram_analyzer}
                }
            },
            
            # ========== 기능성 정보 ==========
            "primary_function": {
                "type": "text",
                "analyzer": main_analyzer,
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngram": {"type": "text", "analyzer": ngram_analyzer}
                }
            },
            
            # ========== 섭취 정보 ==========
            "intake_info": {
                "properties": {
                    "method": {
                        "type": "text",
                        "analyzer": main_analyzer
                    },
                    "caution": {
                        "type": "text",
                        "analyzer": main_analyzer
                    }
                }
            },
            
            # ========== 제품 상세 정보 (NEW!) ==========
            "product_details": {
                "properties": {
                    "standards": {
                        "type": "text",
                        "analyzer": main_analyzer
                    },
                    "appearance": {
                        "type": "text",
                        "analyzer": main_analyzer
                    },
                    "shelf_life": {
                        "type": "keyword"
                    },
                    "storage_method": {
                        "type": "text",
                        "analyzer": main_analyzer
                    }
                }
            },
            
            # ========== 인허가 정보 (NEW!) ==========
            "license_info": {
                "properties": {
                    "license_no": {
                        "type": "keyword"
                    },
                    "report_no": {
                        "type": "keyword"
                    }
                }
            },
            
            # ========== 분류 정보 (선택적) ==========
            "classification": {
                "properties": {
                    "category": {"type": "keyword"},
                    "detail_category": {"type": "keyword"},
                    "function_content": {
                        "type": "text",
                        "analyzer": main_analyzer,
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    }
                }
            },
            
            # ========== 메타데이터 ==========
            "metadata": {
                "properties": {
                    "source": {"type": "keyword"},
                    "version": {"type": "keyword"},
                    "indexed_at": {"type": "date"},
                    "updated_at": {"type": "date"},
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
                    }
                }
            },
            
            # ========== 통계 필드 (Kibana용) ==========
            "stats": {
                "properties": {
                    "view_count": {"type": "integer"},
                    "search_count": {"type": "integer"},
                    "popularity_score": {"type": "float"}
                }
            },
            
            # ========== 추가 필드 ==========
            "ingredient_count": {"type": "integer"},
            "price_range": {"type": "keyword"},
            
            # ========== 임베딩 벡터 ==========
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
    
    return {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "refresh_interval": "1s",
            "analysis": analysis_settings
        },
        "mappings": mappings
    }

# 하위 호환성을 위한 별칭
def get_index_settings(use_nori=None, kibana_optimized=True):
    """기존 함수명 유지 (하위 호환성)"""
    return get_improved_index_settings(use_nori=use_nori)

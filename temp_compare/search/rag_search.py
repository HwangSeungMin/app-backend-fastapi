from typing import List, Dict, Optional
from elasticsearch import Elasticsearch
from config.elasticsearch_config import get_elasticsearch_client
from config.settings import get_config
from search.embeddings import EmbeddingGenerator
from utils.logger import get_logger

config = get_config()
logger = get_logger(__name__)

class RAGSearchEngine:
    """RAG 검색 엔진"""
    
    def __init__(self):
        self.es = get_elasticsearch_client()
        self.index_name = config.ES_INDEX_NAME
        self.embedding_generator = EmbeddingGenerator()
        
        logger.info("RAG 검색 엔진 초기화 완료")
    
    def hybrid_search(
        self, 
        query: str, 
        top_k: int = None,
        vector_weight: float = None,
        keyword_weight: float = None
    ) -> List[Dict]:
        """하이브리드 검색: 벡터 + 키워드"""
        
        top_k = top_k or config.DEFAULT_TOP_K
        vector_weight = vector_weight or config.VECTOR_WEIGHT
        keyword_weight = keyword_weight or config.KEYWORD_WEIGHT
        
        logger.info(f"하이브리드 검색: '{query}' (top_k={top_k})")
        
        # 쿼리 임베딩 생성
        query_vector = self.embedding_generator.generate_single(query).tolist()
        
        # 검색 쿼리 구성
        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        # 벡터 유사도 검색
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                                    "params": {"query_vector": query_vector}
                                },
                                "boost": vector_weight
                            }
                        },
                        # 키워드 검색
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "product_name^2",
                                    "primary_function^5",
                                    "raw_materials^1.5",
                                    "classification.function_content^2",
                                    "embedding_text"
                                ],
                                "type": "best_fields",
                                "boost": keyword_weight
                            }
                        }
                    ]
                }
            },
            "_source": {
                "excludes": ["embedding_vector"]
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=search_query)
            results = self._format_results(response)
            
            logger.info(f"검색 완료: {len(results)}개 결과")
            
            return results
            
        except Exception as e:
            logger.error(f"검색 오류: {e}")
            return []
    
    def search_by_symptom(self, symptom: str, top_k: int = None) -> List[Dict]:
        """증상 기반 검색"""
        
        top_k = top_k or config.DEFAULT_TOP_K
        
        logger.info(f"증상 검색: '{symptom}' (top_k={top_k})")
        
        query_vector = self.embedding_generator.generate_single(symptom).tolist()
        
        search_query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "should": [
                                {"match": {"primary_function": symptom}},
                                {"match": {"classification.function_content": symptom}}
                            ]
                        }
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            },
            "_source": {
                "excludes": ["embedding_vector"]
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=search_query)
            results = self._format_results(response)
            
            logger.info(f"증상 검색 완료: {len(results)}개 결과")
            
            return results
            
        except Exception as e:
            logger.error(f"증상 검색 오류: {e}")
            return []
    
    def search_by_ingredient(self, ingredient: str, top_k: int = None) -> List[Dict]:
        """원재료 기반 검색"""
        
        top_k = top_k or config.DEFAULT_TOP_K * 2
        
        logger.info(f"원재료 검색: '{ingredient}' (top_k={top_k})")
        
        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "raw_materials": {
                                    "query": ingredient,
                                    "operator": "and",
                                    "boost": 2.0
                                }
                            }
                        },
                        {
                            "match": {
                                "product_name": {
                                    "query": ingredient,
                                    "boost": 1.5
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "_source": {
                "excludes": ["embedding_vector"]
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=search_query)
            results = self._format_results(response)
            
            logger.info(f"원재료 검색 완료: {len(results)}개 결과")
            
            return results
            
        except Exception as e:
            logger.error(f"원재료 검색 오류: {e}")
            return []
    
    def filter_by_category(
        self, 
        category: str, 
        function_query: Optional[str] = None, 
        top_k: int = None
    ) -> List[Dict]:
        """카테고리 필터링 + 기능 검색"""
        
        top_k = top_k or config.DEFAULT_TOP_K
        
        logger.info(f"카테고리 검색: '{category}', 기능: '{function_query}' (top_k={top_k})")
        
        must_conditions = [
            {"term": {"classification.category": category}}
        ]
        
        if function_query:
            query_vector = self.embedding_generator.generate_single(function_query).tolist()
            
            search_query = {
                "size": top_k,
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "must": must_conditions,
                                "should": [
                                    {"match": {"primary_function": function_query}}
                                ]
                            }
                        },
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                            "params": {"query_vector": query_vector}
                        }
                    }
                },
                "_source": {
                    "excludes": ["embedding_vector"]
                }
            }
        else:
            search_query = {
                "size": top_k,
                "query": {
                    "bool": {
                        "must": must_conditions
                    }
                },
                "_source": {
                    "excludes": ["embedding_vector"]
                }
            }
        
        try:
            response = self.es.search(index=self.index_name, body=search_query)
            results = self._format_results(response)
            
            logger.info(f"카테고리 검색 완료: {len(results)}개 결과")
            
            return results
            
        except Exception as e:
            logger.error(f"카테고리 검색 오류: {e}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """제품 ID로 단일 문서 조회"""
        
        try:
            response = self.es.get(index=self.index_name, id=product_id)
            
            if response['found']:
                result = response['_source']
                result.pop('embedding_vector', None)
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"제품 조회 오류 (ID: {product_id}): {e}")
            return None
    
    def _format_results(self, response: Dict) -> List[Dict]:
        """검색 결과 포맷팅"""
        
        results = []
        
        for hit in response['hits']['hits']:
            source = hit['_source']
            result = {
                'score': hit['_score'],
                'product_id': source.get('product_id'),
                'product_name': source.get('product_name'),
                'company_name': source.get('company_name'),
                'primary_function': source.get('primary_function'),
                'raw_materials': source.get('raw_materials'),
                'classification': source.get('classification', {}),
                'metadata': source.get('metadata', {})
            }
            results.append(result)
        
        return results
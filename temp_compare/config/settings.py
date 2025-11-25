import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """기본 설정"""
    # API 설정
    FOOD_SAFETY_API_KEY = os.getenv('FOOD_SAFETY_API_KEY', '')
    FOOD_SAFETY_BASE_URL = 'http://openapi.foodsafetykorea.go.kr/api'
    
    # ElasticSearch 설정
    ES_HOST = os.getenv('ES_HOST', 'localhost')
    ES_PORT = int(os.getenv('ES_PORT', 9200))
    ES_INDEX_NAME = 'health_supplements'
    
    # 임베딩 모델 설정
    EMBEDDING_MODEL = 'jhgan/ko-sroberta-multitask'
    EMBEDDING_DIM = 768
    
    # 검색 설정
    DEFAULT_TOP_K = 5
    VECTOR_WEIGHT = 0.8
    KEYWORD_WEIGHT = 0.2
    
    # FastAPI 설정
    API_HOST = '0.0.0.0'
    API_PORT = 8000
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # 데이터 수집 설정
    API_BATCH_SIZE = 1000
    API_REQUEST_DELAY = 0.5  # 초
    
    # Google SERP API 설정
    SERP_API_KEY = os.getenv('SERP_API_KEY', '')
    SERP_API_ENABLED = os.getenv('SERP_API_ENABLED', 'false').lower() == 'true'
    SERP_MAX_RESULTS = int(os.getenv('SERP_MAX_RESULTS', 5))
    SERP_TIMEOUT = int(os.getenv('SERP_TIMEOUT', 5))
    
    # Google Gemini LLM 설정
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    GEMINI_TEMPERATURE = float(os.getenv('GEMINI_TEMPERATURE', 0.7))
    GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv('GEMINI_MAX_OUTPUT_TOKENS', 500))
    
    # 비중 설정
    RAG_WEIGHT = float(os.getenv('RAG_WEIGHT', 0.5))
    GEMINI_WEIGHT = float(os.getenv('GEMINI_WEIGHT', 0.5))
    
    # 출력 설정
    MAX_RESPONSE_LENGTH = int(os.getenv('MAX_RESPONSE_LENGTH', 200))
    
    # 로깅 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False

# 환경별 설정 선택
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.getenv('ENV', 'development')
    return config.get(env, config['default'])

# settings 인스턴스 생성
settings = get_config()()
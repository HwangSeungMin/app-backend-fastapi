import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# 선택적 import - Elasticsearch 로깅 라이브러리
try:
    from pythonjsonlogger import jsonlogger
    from cmreslogging.handlers import CMRESHandler
    ES_LOGGING_AVAILABLE = True
except ImportError:
    ES_LOGGING_AVAILABLE = False

from app.core.config import settings

config = settings

def get_logger(name: str) -> logging.Logger:
    """로거 생성"""

    logger = logging.getLogger(name)

    # 이미 핸들러가 설정되어 있으면 반환
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # 기본 포맷 설정
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (크기 기반 로테이션 - Windows에서 안전)
    if config.LOG_FILE:
        try:
            os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)

            # RotatingFileHandler: 파일 크기 기반 로테이션 (Windows에서 더 안정적)
            file_handler = RotatingFileHandler(
                config.LOG_FILE,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=30,          # 최근 30개 파일 보관
                encoding='utf-8',
                delay=True               # 첫 로그까지 파일 생성 지연 (멀티프로세스 환경에서 안전)
            )

            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # 파일 핸들러 추가 실패 시 경고만 출력
            print(f"Warning: Failed to add file handler: {e}", file=sys.stderr)
    
    # Elasticsearch 핸들러 (Kibana 대시보드용)
    if ES_LOGGING_AVAILABLE and config.LOG_TO_ELASTICSEARCH:
        try:
            # JSON 포맷 설정 (Elasticsearch용)
            json_formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            es_handler = CMRESHandler(
                hosts=[{'host': config.ES_HOST, 'port': config.ES_PORT}],
                auth_type=CMRESHandler.AuthType.NO_AUTH,
                es_index_name=config.LOG_ES_INDEX,
                es_additional_fields={
                    'app': config.PROJECT_NAME,
                    'environment': 'development'
                },
                raise_on_indexing_exceptions=False  # 인덱싱 실패해도 앱은 계속 실행
            )
            es_handler.setFormatter(json_formatter)
            logger.addHandler(es_handler)
        except Exception as e:
            # Elasticsearch 연결 실패 시 경고만 출력하고 계속 진행
            logger.warning(f"Failed to connect to Elasticsearch for logging: {e}")
    
    return logger
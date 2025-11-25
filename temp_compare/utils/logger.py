import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import get_config

config = get_config()

def get_logger(name: str) -> logging.Logger:
    """로거 생성"""
    
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있으면 반환
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # 포맷 설정
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러
    if config.LOG_FILE:
        os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
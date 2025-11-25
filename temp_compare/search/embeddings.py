from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from config.settings import get_config
from utils.logger import get_logger

config = get_config()
logger = get_logger(__name__)

class EmbeddingGenerator:
    """임베딩 생성 클래스"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.EMBEDDING_MODEL
        logger.info(f"임베딩 모델 로드 중: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info("임베딩 모델 로드 완료")
    
    def generate(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """텍스트 리스트를 벡터로 변환"""
        
        logger.info(f"임베딩 생성 시작: {len(texts)}개 텍스트")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=show_progress
        )
        
        logger.info(f"임베딩 생성 완료: shape={embeddings.shape}")
        
        return embeddings
    
    def generate_single(self, text: str) -> np.ndarray:
        """단일 텍스트 임베딩"""
        return self.model.encode([text], convert_to_numpy=True)[0]
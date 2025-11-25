from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from config.settings import get_config
from utils.logger import get_logger
import os

logger = get_logger(__name__)

def create_app() -> FastAPI:
    """FastAPI 앱 팩토리"""

    app = FastAPI(
        title="Health Supplement RAG API",
        description="건강기능식품 추천 및 검색 API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # 설정 로드
    config = get_config()

    # CORS 설정 (보안 강화)
    # 프로덕션 환경에서는 특정 도메인만 허용하도록 수정 필요
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5601').split(',')
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # 환경변수로 제어 가능
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # 라우터 등록
    app.include_router(router, prefix="/api")

    # 로그 디렉토리 생성
    os.makedirs('logs', exist_ok=True)

    logger.info("FastAPI 앱 초기화 완료")

    @app.get("/")
    async def root():
        """API 루트"""
        return {
            'message': 'Health Supplement RAG API',
            'version': '1.0.0',
            'docs': '/docs',
            'redoc': '/redoc',
            'endpoints': {
                'health': '/api/health',
                'intelligent_search': '/api/search/intelligent',  # 새로운 지능형 검색
                'hybrid_search': '/api/search/hybrid',
                'symptom_search': '/api/search/symptom',
                'ingredient_search': '/api/search/ingredient',
                'symptom_recommend': '/api/recommend/symptom',
                'timing_recommend': '/api/recommend/timing',
                'product_detail': '/api/product/{product_id}'
            }
        }

    return app

# FastAPI 앱 인스턴스 생성
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

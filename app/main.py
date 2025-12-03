from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router


def create_app() -> FastAPI:
    """
    애플리케이션 팩토리 함수.
    - FastAPI 인스턴스를 만들고
    - 라우터를 등록하고
    - 필요한 초기화 작업을 여기서 수행합니다.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="의약품 관리 앱 FastAPI 백엔드 서버 (OCR/STT)",
        version="0.2.0",
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()


@app.get("/")
def root():
    return {"message": "Welcome to Yakkobak API"}


@app.get("/api/v1/health")
def health_check():
    """Health check endpoint for Docker healthcheck"""
    return {
        "status": "healthy",
        "service": "yakkobak-api",
        "version": "0.2.0"
    }

# app/main.py

from fastapi import FastAPI

from app.core.database import Base, engine
from app.api.v1 import ocr as ocr_router


def create_app() -> FastAPI:
    """
    애플리케이션 팩토리 함수.
    - FastAPI 인스턴스를 만들고
    - 라우터를 등록하고
    - 필요한 초기화 작업을 여기서 수행합니다.
    """
    app = FastAPI(
        title="Team OCR/TTS Backend",
        description="팀 프로젝트용 FastAPI 백엔드 서버",
        version="0.1.0",
    )

    # DB 스키마 생성
    # 실제 프로젝트에서는 Alembic을 사용해서 마이그레이션 관리하는 것을 권장.
    Base.metadata.create_all(bind=engine)

    # v1 라우터 등록
    app.include_router(ocr_router.router, prefix="/api/v1")

    return app


app = create_app()

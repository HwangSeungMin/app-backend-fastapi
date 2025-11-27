# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# SQLAlchemy Base 클래스
Base = declarative_base()

# SQLAlchemy 엔진 생성
# echo=True 로 하면 콘솔에 SQL 로그가 찍힙니다(개발 단계에서만 켜두면 좋음).
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # 디버깅할 때만 True로 변경
    future=True,
)

# 세션 팩토리 설정
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    FastAPI 의존성 주입(Dependency)에서 사용할 DB 세션 의존성입니다.
    엔드포인트에서 `db: Session = Depends(get_db)` 형태로 사용하면,
    요청이 들어올 때마다 세션을 하나 만들고, 요청이 끝난 후 자동으로 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

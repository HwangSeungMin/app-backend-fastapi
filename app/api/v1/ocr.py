# app/api/v1/ocr.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import models
from app.schemas.user_text import UserTextCreate, UserTextResponse

router = APIRouter(
    prefix="/ocr",
    tags=["OCR"],
)


@router.post("/texts", response_model=UserTextResponse)
def create_user_text(
    payload: UserTextCreate,
    db: Session = Depends(get_db),
):
    """
    [예시 엔드포인트]
    - 클라이언트(나중에 Flutter)가 title, content를 보내면
      DB에 저장하고, 저장된 데이터를 반환합니다.
    - 실제 프로젝트에서는, 
      Azure OCR에서 받아온 텍스트를 기반으로 DB에 저장하거나,
      텍스트 수정/확정 후 저장하도록 바꿀 수 있습니다.
    """

    # SQLAlchemy 모델 인스턴스 생성
    user_text = models.UserText(
        title=payload.title,
        content=payload.content,
    )

    # DB에 저장
    db.add(user_text)
    db.commit()
    db.refresh(user_text)

    return user_text

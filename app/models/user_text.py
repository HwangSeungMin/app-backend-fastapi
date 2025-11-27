# app/models/user_text.py

from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class UserText(Base):
    """
    예시용 모델.
    - 사용자가 찍은 이미지에서 추출한 텍스트를 저장한다고 가정.
    """

    __tablename__ = "user_texts"

    id = Column(Integer, primary_key=True, index=True)
    # 나중에 user_id, created_at 같은 컬럼을 추가해도 됨.
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

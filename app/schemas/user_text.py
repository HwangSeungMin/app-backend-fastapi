# app/schemas/user_text.py

from pydantic import BaseModel


class UserTextBase(BaseModel):
    """
    공통 필드 정의 (입력/출력 모두에서 사용하는 베이스)
    """
    title: str
    content: str


class UserTextCreate(UserTextBase):
    """
    생성 시에 사용하는 스키마.
    현재는 UserTextBase와 동일하지만, 나중에 생성 시에만 필요한 필드가 생기면 여기에 추가.
    """
    pass


class UserTextResponse(UserTextBase):
    """
    응답에 사용할 스키마.
    id 같은 읽기 전용 필드를 포함합니다.
    """
    id: int

    class Config:
        orm_mode = True  # SQLAlchemy 모델을 그대로 넣어도 자동으로 변환 가능하게 함

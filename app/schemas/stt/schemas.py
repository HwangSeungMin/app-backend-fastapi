from pydantic import BaseModel
from typing import Optional


class TextInput(BaseModel):
    """텍스트 입력 스키마"""
    text: str


class MedicationData(BaseModel):
    """의약품 복용 정보 스키마"""
    medication_name: Optional[str] = None
    total_duration_days: Optional[int] = None
    daily_frequency: Optional[int] = None
    meal_context: Optional[str] = None  # "pre_meal" | "post_meal" | "at_bedtime"
    specific_offset_minutes: Optional[int] = None
    special_instructions: Optional[str] = None


class STTResponse(BaseModel):
    """STT only 응답 스키마"""
    success: bool
    text: str
    message: str


class ExtractResponse(BaseModel):
    """STT + LLM 추출 응답 스키마"""
    success: bool
    stt_text: str
    data: Optional[MedicationData] = None
    message: str


class ExtractTextResponse(BaseModel):
    """텍스트 추출 응답 스키마"""
    success: bool
    input_text: str
    data: Optional[MedicationData] = None
    message: str


class HealthResponse(BaseModel):
    """헬스체크 응답 스키마"""
    status: str
    service: str

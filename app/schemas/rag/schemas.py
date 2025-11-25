from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class SearchRequest(BaseModel):
    """검색 요청 스키마"""
    query: str = Field(..., min_length=1, description="검색어")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="결과 개수")

class SymptomSearchRequest(BaseModel):
    """증상 검색 요청"""
    symptom: str = Field(..., min_length=1, description="증상")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="추천 개수")

class IngredientSearchRequest(BaseModel):
    """성분 검색 요청"""
    ingredient: str = Field(..., min_length=1, description="성분명")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="결과 개수")

class TimingRecommendationRequest(BaseModel):
    """복용 시간 추천 요청 (복수형 통일)"""
    ingredients: List[str] = Field(..., min_items=1, description="성분 목록 (1개 이상 필수)")
    user_meal_times: Optional[Dict] = Field(None, description="사용자 식사 시간")
    existing_alarms: Optional[List[Dict]] = Field(None, description="기존 알람 목록")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "ingredients": ["마그네슘"]
                },
                {
                    "ingredients": ["철분", "칼슘", "비타민D"],
                    "user_meal_times": {
                        "breakfast": "08:00",
                        "lunch": "12:00",
                        "dinner": "18:00"
                    }
                }
            ]
        }

class ProductDetailRequest(BaseModel):
    """제품 상세 조회 요청"""
    product_id: str = Field(..., description="제품 ID")

class APIResponse(BaseModel):
    """API 응답 기본 스키마"""
    success: bool
    message: str
    data: Optional[Dict] = None

# 새로운 지능형 검색 스키마
class IntelligentSearchRequest(BaseModel):
    """지능형 검색 요청"""
    query: str = Field(..., min_length=1, description="검색어")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="결과 개수")
    enable_fallback: Optional[bool] = Field(True, description="Fallback 응답 사용 여부")
    enable_reranking: Optional[bool] = Field(True, description="Re-ranking 사용 여부")
    enable_diversity: Optional[bool] = Field(False, description="다양성 필터링 사용 여부")
    enable_serp: Optional[bool] = Field(False, description="Google SERP 검색 사용 여부")
    serp_max_results: Optional[int] = Field(5, ge=1, le=10, description="SERP 결과 개수")

class QueryAnalysisResponse(BaseModel):
    """쿼리 분석 결과"""
    original_query: str
    entities: Dict[str, List[str]]
    intent: str
    expanded_query: str
    knowledge_match: Optional[Dict] = None

class IntelligentSearchResponse(BaseModel):
    """지능형 검색 응답"""
    success: bool
    message: str
    query_analysis: Dict[str, Any]
    routing_info: Dict[str, Any]
    results: Any
    fallback_used: bool = False
    fallback_info: Optional[Dict] = None
    serp_results: Optional[List[Dict]] = None
    serp_enabled: bool = False
    additional_info: Optional[Dict] = None

# Gemini LLM 스키마
class GeminiRecommendationRequest(BaseModel):
    """Gemini 추천 요청"""
    query: str = Field(..., min_length=1, description="사용자 증상/질문")
    top_k: int = Field(5, ge=1, le=20, description="RAG 결과 개수")
    enable_serp: bool = Field(True, description="SERP 검색 사용")
    serp_max_results: int = Field(5, ge=1, le=10, description="SERP 결과 개수")
    
    # 비중 설정
    rag_weight: float = Field(0.5, ge=0.0, le=1.0, description="RAG+SERP 참조 비중")
    
    # 출력 설정
    max_length: int = Field(200, ge=50, le=1000, description="최대 글자 수")
    include_product_name: bool = Field(True, description="제품명 포함")
    include_ingredients: bool = Field(True, description="원재료 포함")
    include_timing: bool = Field(True, description="복용시기 포함")
    include_precautions: bool = Field(True, description="주의사항 포함")
    
    # 커스텀 프롬프트
    custom_prompt: Optional[str] = Field(None, description="사용자 정의 프롬프트")
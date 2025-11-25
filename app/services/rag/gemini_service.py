"""
Google Gemini LLM 서비스 (google-genai SDK 사용)

RAG 검색 결과와 SERP 결과를 Gemini로 융합하여 최종 추천을 생성합니다.
"""
from typing import List, Dict, Optional, Any
import asyncio
import re
import os
from google.genai import Client
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiService:
    """Google Gemini LLM 서비스 (새로운 google-genai SDK)"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_output_tokens = settings.GEMINI_MAX_OUTPUT_TOKENS
        
        # Gemini 클라이언트 초기화
        if self.api_key:
            # API 키로 클라이언트 초기화
            self.client = Client(api_key=self.api_key)
            logger.info(f"Gemini 클라이언트 초기화 완료: {self.model_name}")
        else:
            self.client = None
            logger.warning("Gemini API 키가 설정되지 않았습니다.")
    
    async def generate_recommendation(
        self,
        query: str,
        rag_results: List[Dict],
        serp_results: List[Dict],
        rag_weight: float = 0.5,
        max_length: int = 200,
        custom_prompt: Optional[str] = None,
        output_options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        RAG + SERP 결과를 Gemini로 융합하여 추천 생성
        
        Args:
            query: 사용자 질문/증상
            rag_results: RAG 검색 결과
            serp_results: SERP 검색 결과
            rag_weight: RAG+SERP 참조 비중 (0.0~1.0)
            max_length: 최대 출력 길이
            custom_prompt: 사용자 정의 프롬프트
            output_options: 출력 옵션
        
        Returns:
            추천 결과 딕셔너리
        """
        if not self.client:
            raise ValueError("Gemini API 키가 설정되지 않았습니다.")
        
        try:
            logger.info(f"Gemini 추천 생성 시작: '{query}'")
            
            # 출력 옵션 기본값
            if output_options is None:
                output_options = {
                    'include_product_name': True,
                    'include_ingredients': True,
                    'include_timing': True,
                    'include_precautions': True
                }
            
            # 프롬프트 구성
            prompt = self._build_prompt(
                query=query,
                rag_results=rag_results,
                serp_results=serp_results,
                rag_weight=rag_weight,
                max_length=max_length,
                custom_prompt=custom_prompt,
                output_options=output_options
            )
            
            # Gemini API 호출
            response_text = await self._call_gemini(prompt)
            
            # 응답 파싱
            recommendation = self._parse_response(response_text)
            
            logger.info(f"Gemini 추천 생성 완료: {len(response_text)}자")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Gemini 추천 생성 오류: {e}", exc_info=True)
            raise
    
    def _build_prompt(
        self,
        query: str,
        rag_results: List[Dict],
        serp_results: List[Dict],
        rag_weight: float,
        max_length: int,
        custom_prompt: Optional[str],
        output_options: Dict
    ) -> str:
        """프롬프트 구성"""
        
        gemini_weight = 1 - rag_weight
        
        # RAG 결과 포맷팅
        rag_text = self._format_rag_results(rag_results)
        
        # SERP 결과 포맷팅
        serp_text = self._format_serp_results(serp_results)
        
        # 출력 요구사항 포맷팅
        output_requirements = self._format_output_options(output_options)
        
        # 커스텀 프롬프트 또는 기본 프롬프트
        if custom_prompt and custom_prompt != "string":
            system_prompt = custom_prompt
        else:
            system_prompt = f"""
당신은 건강기능식품 전문가입니다.
사용자의 증상에 맞는 영양제와 약을 추천해주세요.

**참조 데이터 비중**: {rag_weight * 100:.0f}%
- RAG 검색 결과 (내부 DB의 실제 제품 정보)
- SERP 검색 결과 (웹 검색 정보)

**Gemini 지식 비중**: {gemini_weight * 100:.0f}%
- 의학적 지식
- 영양학 지식
- 최신 연구 결과

**출력 형식**:
{output_requirements}

**제약 조건**:
- 최대 {max_length}글자 이내로 작성
- 명확하고 간결하게
- 의학적 근거 기반
- 구체적인 제품명 포함
"""
        
        user_prompt = f"""
**사용자 증상**: {query}

**RAG 검색 결과** (내부 DB, 참조 비중 {rag_weight * 100:.0f}%):
{rag_text}

**SERP 검색 결과** (웹 검색, 참조 비중 {rag_weight * 100:.0f}%):
{serp_text}

위 정보를 {rag_weight * 100:.0f}% 참조하고, 당신의 의학 지식을 {gemini_weight * 100:.0f}% 활용하여 
최적의 영양제/약을 추천해주세요.

**중요**: 반드시 {max_length}글자 이내로 작성하세요.
"""
        
        return system_prompt + "\n\n" + user_prompt
    
    def _format_rag_results(self, results: List[Dict]) -> str:
        """RAG 결과 포맷팅"""
        if not results:
            return "검색 결과 없음"
        
        formatted = []
        for idx, result in enumerate(results[:5], 1):
            product_name = result.get('product_name', 'N/A')
            company = result.get('company_name', 'N/A')
            materials = result.get('raw_materials', 'N/A')
            function = result.get('primary_function', 'N/A')
            
            # 길이 제한
            if len(materials) > 100:
                materials = materials[:100] + "..."
            if len(function) > 100:
                function = function[:100] + "..."
            
            formatted.append(f"""
{idx}. {product_name}
   - 제조사: {company}
   - 원재료: {materials}
   - 기능: {function}
""")
        
        return "\n".join(formatted)
    
    def _format_serp_results(self, results: List[Dict]) -> str:
        """SERP 결과 포맷팅"""
        if not results:
            return "검색 결과 없음"
        
        formatted = []
        for idx, result in enumerate(results[:5], 1):
            title = result.get('title', 'N/A')
            snippet = result.get('snippet', 'N/A')
            
            # 길이 제한
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
            
            formatted.append(f"""
{idx}. {title}
   - 내용: {snippet}
""")
        
        return "\n".join(formatted)
    
    def _format_output_options(self, options: Dict) -> str:
        """출력 옵션 포맷팅"""
        requirements = []
        
        if options.get('include_product_name', True):
            requirements.append("1. 추천 약/영양제 종류")
            requirements.append("2. 제품명 (구체적으로 2-3개)")
        
        if options.get('include_ingredients', True):
            requirements.append("3. 주요 원재료 (핵심 성분)")
        
        if options.get('include_timing', True):
            requirements.append("4. 복용 시기 (아침/점심/저녁/취침 전)")
        
        if options.get('include_precautions', True):
            requirements.append("5. 주의사항 (간단히)")
        
        return "\n".join(requirements)
    
    async def _call_gemini(self, prompt: str) -> str:
        """Gemini API 호출 (새로운 google-genai SDK)"""
        try:
            logger.info(f"Gemini API 호출: model={self.model_name}")
            
            # 비동기 실행
            def _sync_generate():
                logger.debug(f"프롬프트 길이: {len(prompt)}자")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={
                        'temperature': self.temperature,
                        'max_output_tokens': self.max_output_tokens
                    }
                )
                
                logger.info(f"응답 객체 타입: {type(response)}")
                
                # 1. response.text 속성 시도 (가장 일반적)
                try:
                    if hasattr(response, 'text') and response.text:
                        logger.info("response.text에서 텍스트 추출 성공")
                        return response.text
                except Exception as e:
                    logger.debug(f"response.text 접근 실패: {e}")

                # 2. candidates 구조 순회
                if hasattr(response, 'candidates') and response.candidates:
                    for i, candidate in enumerate(response.candidates):
                        logger.debug(f"Candidate {i} 확인 중")
                        if hasattr(candidate, 'content') and candidate.content:
                            # parts 확인
                            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        logger.info("candidate.content.parts에서 텍스트 추출 성공")
                                        return part.text
                            # content.text 확인
                            if hasattr(candidate.content, 'text') and candidate.content.text:
                                logger.info("candidate.content.text에서 텍스트 추출 성공")
                                return candidate.content.text
                
                # 3. 최후의 수단: 문자열 변환
                logger.warning(f"텍스트 추출 실패. 응답 객체 구조: {dir(response)}")
                return str(response)
            
            response_text = await asyncio.to_thread(_sync_generate)
            
            if not response_text:
                raise ValueError("Gemini API가 빈 응답을 반환했습니다.")
            
            logger.info(f"응답 텍스트 길이: {len(response_text)}자")
            return response_text
            
        except Exception as e:
            logger.error(f"Gemini API 호출 오류: {e}", exc_info=True)
            raise
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """응답 파싱"""
        # 구조화된 데이터 추출
        structured = {
            'type': self._extract_type(response_text),
            'products': self._extract_products(response_text),
            'ingredients': self._extract_ingredients(response_text),
            'timing': self._extract_timing(response_text),
            'precautions': self._extract_precautions(response_text)
        }
        
        return {
            'text': response_text,
            'structured': structured
        }
    
    def _extract_type(self, text: str) -> str:
        """종류 추출"""
        # "1. 추천 약/영양제 종류" 패턴 찾기
        pattern = r'1\.\s*(?:추천\s*)?(?:약/영양제\s*)?종류[:\s]*([^\n]+)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return "정보 없음"
    
    def _extract_products(self, text: str) -> List[str]:
        """제품명 추출"""
        # "2. 제품명" 패턴 찾기
        pattern = r'2\.\s*제품명[:\s]*([^\n]+)'
        match = re.search(pattern, text)
        if match:
            products_text = match.group(1).strip()
            # 쉼표나 슬래시로 분리
            products = re.split(r'[,/]', products_text)
            return [p.strip() for p in products if p.strip()]
        return []
    
    def _extract_ingredients(self, text: str) -> List[str]:
        """원재료 추출"""
        # "3. 주요 원재료" 패턴 찾기
        pattern = r'3\.\s*(?:주요\s*)?원재료[:\s]*([^\n]+)'
        match = re.search(pattern, text)
        if match:
            ingredients_text = match.group(1).strip()
            # 쉼표로 분리
            ingredients = re.split(r',', ingredients_text)
            return [i.strip() for i in ingredients if i.strip()]
        return []
    
    def _extract_timing(self, text: str) -> str:
        """복용 시기 추출"""
        # "4. 복용 시기" 패턴 찾기
        pattern = r'4\.\s*복용\s*시기[:\s]*([^\n]+)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return "정보 없음"
    
    def _extract_precautions(self, text: str) -> List[str]:
        """주의사항 추출"""
        # "5. 주의사항" 패턴 찾기
        pattern = r'5\.\s*주의사항[:\s]*([^\n]+)'
        match = re.search(pattern, text)
        if match:
            precautions_text = match.group(1).strip()
            # 쉼표나 세미콜론으로 분리
            precautions = re.split(r'[,;]', precautions_text)
            return [p.strip() for p in precautions if p.strip()]
        return []


# 싱글톤 인스턴스
gemini_service = GeminiService()

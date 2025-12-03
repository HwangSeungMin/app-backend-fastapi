# 🤖 `/api/v1/recommend/gemini` 엔드포인트 분석

## 📋 개요

**엔드포인트**: `POST /api/v1/recommend/gemini`

**목적**: Google Gemini LLM을 활용하여 RAG 검색 결과와 SERP 검색 결과를 융합한 개인화된 건강기능식품 추천 생성

**위치**: [`app/api/v1/endpoints/rag/routes.py`](project-folder/app-backend-fastapi/app/api/v1/endpoints/rag/routes.py#L377-L460)

## 🎯 핵심 기능

이 엔드포인트는 **3단계 AI 추천 파이프라인**을 통해 작동합니다:

```
사용자 쿼리
    ↓
1. RAG 검색 (ElasticSearch + 벡터 검색)
    ↓
2. SERP 검색 (Google 검색 - 선택적)
    ↓
3. Gemini LLM 융합
    ├─ RAG 결과 분석
    ├─ SERP 결과 분석
    ├─ 가중치 적용 (RAG vs Gemini 지식)
    └─ 개인화된 추천 생성
    ↓
최종 추천 응답
```

## 📥 요청 스키마

### `GeminiRecommendationRequest`

```python
{
    # 필수 파라미터
    "query": str,                      # 사용자 증상/질문 (필수)
    
    # RAG 검색 설정
    "top_k": int = 5,                  # RAG 결과 개수 (1-20)
    
    # SERP 검색 설정
    "enable_serp": bool = True,        # SERP 검색 사용 여부
    "serp_max_results": int = 5,       # SERP 결과 개수 (1-10)
    
    # 가중치 설정
    "rag_weight": float = 0.5,         # RAG+SERP 참조 비중 (0.0-1.0)
                                       # 0.5 = RAG 50% + Gemini 지식 50%
    
    # 출력 설정
    "max_length": int = 200,           # 최대 글자 수 (50-1000)
    "include_product_name": bool = True,    # 제품명 포함
    "include_ingredients": bool = True,     # 원재료 포함
    "include_timing": bool = True,          # 복용시기 포함
    "include_precautions": bool = True,     # 주의사항 포함
    
    # 커스텀 프롬프트
    "custom_prompt": str = None        # 사용자 정의 프롬프트 (선택)
}
```

### 예시 요청

```bash
curl -X POST "http://localhost:8000/api/v1/recommend/gemini" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "눈이 피로하고 시력이 떨어지는 것 같아요",
    "top_k": 5,
    "enable_serp": true,
    "rag_weight": 0.5,
    "max_length": 300,
    "include_product_name": true,
    "include_ingredients": true,
    "include_timing": true,
    "include_precautions": true
  }'
```

## 📤 응답 구조

```python
{
    "success": bool,
    "message": str,
    "query": str,                      # 원본 쿼리
    
    # Gemini 추천 결과
    "recommendation": {
        "text": str,                   # 전체 추천 텍스트
        "type": str,                   # 추천 종류 (예: "영양제")
        "products": List[str],         # 추천 제품명 목록
        "ingredients": List[str],      # 주요 원재료 목록
        "timing": str,                 # 복용 시기
        "precautions": List[str]       # 주의사항 목록
    },
    
    # 데이터 소스 정보
    "sources": {
        "rag_count": int,              # RAG 검색 결과 개수
        "serp_count": int,             # SERP 검색 결과 개수
        "rag_weight": float,           # RAG+SERP 참조 비중
        "gemini_weight": float         # Gemini 지식 비중
    },
    
    # 메타데이터
    "metadata": {
        "max_length": int,             # 요청한 최대 길이
        "actual_length": int,          # 실제 응답 길이
        "model": str,                  # 사용된 Gemini 모델
        "temperature": float           # 생성 온도
    }
}
```

## 🔧 핵심 컴포넌트 상세 분석

### 1️⃣ RAG 검색 (Hybrid Search)

**파일**: [`app/search/rag_search.py`](project-folder/app-backend-fastapi/app/search/rag_search.py)

#### 기능
- ElasticSearch 하이브리드 검색 (벡터 + 키워드)
- 사용자 쿼리와 가장 관련성 높은 제품 검색
- `top_k`개의 결과 반환

#### 검색 방식
```python
# 벡터 검색 (80%) + 키워드 검색 (20%)
results = elasticsearch.hybrid_search(
    query=query,
    vector_weight=0.8,
    keyword_weight=0.2,
    top_k=5
)
```

---

### 2️⃣ SERP 검색 (Google Search)

**파일**: [`app/services/rag/serp_service.py`](project-folder/app-backend-fastapi/app/services/rag/serp_service.py)

#### 기능
- Google 검색 결과 수집
- 최신 정보 및 외부 리뷰 제공
- RAG 데이터 보완

#### 검색 결과
```python
{
    "title": "눈 건강에 좋은 영양제 추천",
    "link": "https://...",
    "snippet": "루테인과 지아잔틴이 눈 건강에..."
}
```

---

### 3️⃣ Gemini LLM 서비스

**파일**: [`app/services/rag/gemini_service.py`](project-folder/app-backend-fastapi/app/services/rag/gemini_service.py)

#### 주요 기능

**1. 프롬프트 구성**
```python
def _build_prompt(query, rag_results, serp_results, rag_weight, options):
    """
    RAG 결과와 SERP 결과를 프롬프트에 통합
    """
    prompt = f"""
    사용자 질문: {query}
    
    [RAG 검색 결과] (참조 비중: {rag_weight * 100}%)
    {formatted_rag_results}
    
    [Google 검색 결과] (참조 비중: {rag_weight * 100}%)
    {formatted_serp_results}
    
    [Gemini 지식] (참조 비중: {(1-rag_weight) * 100}%)
    
    요구사항:
    - 최대 {max_length}자
    - 포함 정보: {output_options}
    
    위 정보를 종합하여 개인화된 추천을 생성하세요.
    """
```

**2. Gemini API 호출**
```python
async def _call_gemini(prompt):
    """
    Google Gemini API 호출 (google-generativeai SDK)
    """
    model = genai.GenerativeModel(model_name='gemini-2.0-flash')
    response = await model.generate_content_async(
        prompt,
        generation_config={
            'temperature': 0.7,
            'max_output_tokens': 500
        }
    )
    return response.text
```

**3. 응답 파싱**
```python
def _parse_response(response_text):
    """
    Gemini 응답에서 구조화된 정보 추출
    """
    return {
        'text': response_text,
        'type': _extract_type(response_text),
        'products': _extract_products(response_text),
        'ingredients': _extract_ingredients(response_text),
        'timing': _extract_timing(response_text),
        'precautions': _extract_precautions(response_text)
    }
```

---

## 🔄 전체 처리 흐름

### 예시: "눈이 피로하고 시력이 떨어지는 것 같아요"

```
1. RAG 검색
   - 쿼리: "눈이 피로하고 시력이 떨어지는 것 같아요"
   - 하이브리드 검색 실행
   - 결과: 5개 제품 (루테인, 지아잔틴 등)

2. SERP 검색 (비동기)
   - Google에서 "눈 피로 시력 영양제" 검색
   - 결과: 5개 웹 페이지

3. Gemini 프롬프트 구성
   - RAG 결과 포맷팅
   - SERP 결과 포맷팅
   - 가중치 적용 (RAG 50% + Gemini 50%)
   - 출력 옵션 설정

4. Gemini API 호출
   - 모델: gemini-2.0-flash
   - Temperature: 0.7
   - Max tokens: 500

5. 응답 생성
   - 전체 텍스트: "눈 건강을 위해 루테인과 지아잔틴이 함유된..."
   - 제품명: ["루테인 지아잔틴", "오메가3"]
   - 원재료: ["루테인", "지아잔틴", "비타민A"]
   - 복용시기: "식후 30분"
   - 주의사항: ["과다 복용 주의", "임산부 상담 필요"]

6. 최종 응답
   - 구조화된 JSON 응답
   - 소스 정보 포함
   - 메타데이터 포함
```

---

## 📊 응답 예시

### 성공 응답

```json
{
    "success": true,
    "message": "Gemini 추천 완료",
    "query": "눈이 피로하고 시력이 떨어지는 것 같아요",
    "recommendation": {
        "text": "눈 건강을 위해 루테인과 지아잔틴이 함유된 영양제를 추천드립니다. 루테인은 눈의 황반을 보호하고 시력 개선에 도움을 줍니다. 종근당 루테인 지아잔틴이나 대웅제약 아이케어 제품이 좋은 선택입니다. 식후 30분에 복용하시고, 과다 복용은 피하시기 바랍니다.",
        "type": "영양제",
        "products": [
            "종근당 루테인 지아잔틴",
            "대웅제약 아이케어",
            "오메가3"
        ],
        "ingredients": [
            "루테인",
            "지아잔틴",
            "비타민A",
            "오메가3"
        ],
        "timing": "식후 30분",
        "precautions": [
            "과다 복용 주의",
            "임산부는 전문가 상담 필요",
            "알레르기 확인"
        ]
    },
    "sources": {
        "rag_count": 5,
        "serp_count": 5,
        "rag_weight": 0.5,
        "gemini_weight": 0.5
    },
    "metadata": {
        "max_length": 300,
        "actual_length": 187,
        "model": "gemini-2.0-flash",
        "temperature": 0.7
    }
}
```

---

## 🎯 사용 시나리오

### 시나리오 1: 기본 추천 (RAG 50% + Gemini 50%)

```bash
POST /api/v1/recommend/gemini
{
    "query": "피로 회복에 좋은 영양제 추천해주세요",
    "top_k": 5,
    "enable_serp": true,
    "rag_weight": 0.5,
    "max_length": 200
}

→ RAG 검색: 비타민B, 마그네슘 제품 5개
→ SERP 검색: 피로 회복 관련 웹 페이지 5개
→ Gemini 융합: RAG 50% + Gemini 지식 50%
→ 결과: 개인화된 추천 (200자 이내)
```

---

### 시나리오 2: RAG 중심 추천 (RAG 80% + Gemini 20%)

```bash
POST /api/v1/recommend/gemini
{
    "query": "관절 건강 영양제",
    "top_k": 10,
    "enable_serp": true,
    "rag_weight": 0.8,
    "max_length": 300
}

→ RAG 결과를 더 많이 참조
→ Gemini는 보조적으로 정보 보완
→ 결과: 데이터 기반 추천
```

---

### 시나리오 3: Gemini 중심 추천 (RAG 20% + Gemini 80%)

```bash
POST /api/v1/recommend/gemini
{
    "query": "면역력 강화 방법",
    "top_k": 3,
    "enable_serp": false,
    "rag_weight": 0.2,
    "max_length": 500
}

→ RAG 결과는 참고만
→ Gemini의 광범위한 지식 활용
→ 결과: AI 기반 종합 추천
```

---

### 시나리오 4: 커스텀 프롬프트 사용

```bash
POST /api/v1/recommend/gemini
{
    "query": "30대 남성 운동 보조제",
    "top_k": 5,
    "enable_serp": true,
    "rag_weight": 0.5,
    "max_length": 400,
    "custom_prompt": "30대 남성 운동선수에게 적합한 제품을 추천해주세요. 근육 회복과 지구력 향상에 초점을 맞춰주세요."
}

→ 커스텀 프롬프트로 개인화 강화
→ 특정 요구사항 반영
→ 결과: 맞춤형 추천
```

---

### 시나리오 5: 출력 옵션 조정

```bash
POST /api/v1/recommend/gemini
{
    "query": "비타민C 제품",
    "top_k": 5,
    "enable_serp": false,
    "max_length": 150,
    "include_product_name": true,
    "include_ingredients": false,
    "include_timing": true,
    "include_precautions": false
}

→ 제품명과 복용시기만 포함
→ 원재료와 주의사항 제외
→ 결과: 간결한 추천 (150자)
```

---

## ⚙️ 가중치 설정 가이드

### `rag_weight` 파라미터

| 값 | RAG 비중 | Gemini 비중 | 추천 용도 |
|----|----------|-------------|-----------|
| 0.0 | 0% | 100% | Gemini 지식만 사용 (일반 상담) |
| 0.2 | 20% | 80% | Gemini 중심, RAG 참고 |
| 0.5 | 50% | 50% | 균형잡힌 추천 (기본값) |
| 0.8 | 80% | 20% | RAG 중심, Gemini 보완 |
| 1.0 | 100% | 0% | RAG 결과만 사용 (데이터 기반) |

### 선택 가이드

**RAG 비중 높게 (0.7-1.0)**:
- ✅ 정확한 제품 정보 필요
- ✅ 데이터베이스 기반 추천
- ✅ 실제 제품 중심 추천

**균형 (0.4-0.6)**:
- ✅ 일반적인 건강 상담
- ✅ 개인화된 추천
- ✅ 대부분의 경우 (기본값)

**Gemini 비중 높게 (0.0-0.3)**:
- ✅ 일반 건강 정보 제공
- ✅ 광범위한 지식 필요
- ✅ 교육적 내용

---

## 🔍 다른 엔드포인트와의 비교

| 엔드포인트 | 기능 | Gemini 추천 차이점 |
|-----------|------|-------------------|
| `/search/hybrid` | 기본 검색 | ❌ AI 추천 없음<br>❌ 자연어 응답 없음 |
| `/search/intelligent` | 지능형 검색 | ❌ Gemini 미사용<br>❌ 융합 추천 없음 |
| `/recommend/symptom` | 증상 추천 | ❌ 고정된 로직<br>❌ 개인화 부족 |
| **`/recommend/gemini`** | **AI 융합 추천** | ✅ Gemini LLM 사용<br>✅ RAG+SERP 융합<br>✅ 자연어 응답<br>✅ 개인화 추천<br>✅ 가중치 조절 |

---

## 💡 장점

1. **AI 기반 자연어 응답**: 사람이 이해하기 쉬운 형태로 추천
2. **다중 소스 융합**: RAG + SERP + Gemini 지식 통합
3. **가중치 조절**: 데이터 vs AI 지식 비중 조정 가능
4. **개인화**: 사용자 상황에 맞는 맞춤 추천
5. **구조화된 정보**: 제품명, 원재료, 복용시기, 주의사항 자동 추출
6. **유연한 출력**: 길이 및 포함 정보 조절 가능
7. **커스텀 프롬프트**: 특수한 요구사항 반영

---

## ⚠️ 주의사항

### 1. API 키 필요
```bash
# .env 파일
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.7
```

### 2. 비용 발생
- Gemini API 호출 시 비용 발생
- SERP API 사용 시 추가 비용
- 요청 빈도 관리 필요

### 3. 응답 시간
- RAG 검색: ~200ms
- SERP 검색: ~500ms
- Gemini 생성: ~1-3초
- **총 예상 시간: 2-4초**

### 4. 응답 품질
- `temperature` 값에 따라 응답 다양성 변화
- 0.0: 일관적, 보수적
- 0.7: 균형 (기본값)
- 1.0: 창의적, 다양

### 5. 오류 처리
```python
try:
    response = await gemini_service.generate_recommendation(...)
except ValueError as e:
    # 설정 오류 (API 키 없음 등)
    return {"error": "Gemini 설정 오류"}
except Exception as e:
    # API 호출 실패
    return {"error": "추천 생성 실패"}
```

---

## 🔗 관련 파일

- **라우터**: [`app/api/v1/endpoints/rag/routes.py`](project-folder/app-backend-fastapi/app/api/v1/endpoints/rag/routes.py#L377-L460)
- **스키마**: [`app/schemas/rag/schemas.py`](project-folder/app-backend-fastapi/app/schemas/rag/schemas.py#L85-L103)
- **Gemini 서비스**: [`app/services/rag/gemini_service.py`](project-folder/app-backend-fastapi/app/services/rag/gemini_service.py)
- **RAG 검색**: [`app/search/rag_search.py`](project-folder/app-backend-fastapi/app/search/rag_search.py)
- **SERP 서비스**: [`app/services/rag/serp_service.py`](project-folder/app-backend-fastapi/app/services/rag/serp_service.py)

---

## 📝 요약

`/api/v1/recommend/gemini`는 **Google Gemini LLM을 활용한 최첨단 AI 추천 엔드포인트**로, RAG 검색과 SERP 검색 결과를 융합하여 개인화된 자연어 추천을 제공합니다.

**핵심 특징**:
- 🤖 Google Gemini LLM 기반 추천
- 🔍 RAG + SERP 다중 소스 융합
- ⚖️ 가중치 조절 (데이터 vs AI 지식)
- 📝 자연어 응답 생성
- 🎯 구조화된 정보 추출
- 🛠️ 유연한 출력 옵션
- 💬 커스텀 프롬프트 지원

**추천 사용 케이스**: 
- 챗봇 응답 생성
- 개인화된 건강 상담
- 자연어 기반 추천 시스템
- AI 기반 고객 서비스

**설정 요구사항**:
- Gemini API 키 필수
- SERP API 키 (선택)
- 적절한 가중치 설정

# 🔍 `/api/v1/rag/search/intelligent` 엔드포인트 분석

## 📋 개요

**엔드포인트**: `POST /api/v1/search/intelligent`

**목적**: 사용자 쿼리를 지능적으로 분석하여 최적의 검색 결과를 제공하는 고급 검색 API

**위치**: [`app/api/v1/endpoints/rag/routes.py`](project-folder/app-backend-fastapi/app/api/v1/endpoints/rag/routes.py#L221-L334)

## 🎯 핵심 기능

이 엔드포인트는 **7단계 지능형 검색 파이프라인**을 통해 작동합니다:

```
사용자 쿼리
    ↓
1. 쿼리 분석 (Query Analysis)
    ↓
2. SERP 검색 (Google Search - 선택적)
    ↓
3. 스마트 라우팅 (Smart Routing)
    ↓
4. Fallback 처리 (결과 부족 시)
    ↓
5. Re-ranking (결과 재정렬)
    ↓
6. 추가 정보 보강
    ↓
7. 응답 구성
```

## 📥 요청 스키마

### `IntelligentSearchRequest`

```python
{
    "query": str,                    # 검색어 (필수)
    "top_k": int = 5,               # 결과 개수 (1-20)
    "enable_fallback": bool = True, # Fallback 사용 여부
    "enable_reranking": bool = True,# Re-ranking 사용 여부
    "enable_diversity": bool = False,# 다양성 필터링
    "enable_serp": bool = False,    # Google SERP 검색
    "serp_max_results": int = 5     # SERP 결과 개수
}
```

### 예시 요청

```bash
curl -X POST "http://localhost:8000/api/v1/search/intelligent" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "눈이 피로해요",
    "top_k": 5,
    "enable_serp": true,
    "enable_reranking": true
  }'
```

## 📤 응답 구조

```python
{
    "success": bool,
    "message": str,
    
    # 쿼리 분석 결과
    "query_analysis": {
        "original_query": str,        # 원본 쿼리
        "entities": {                 # 추출된 개체명
            "symptoms": List[str],    # 증상
            "ingredients": List[str], # 성분
            "body_parts": List[str],  # 신체 부위
            "effects": List[str]      # 효과
        },
        "intent": str,                # 의도 분류
        "expanded_query": str,        # 확장된 쿼리
        "knowledge_match": Dict       # 지식베이스 매칭
    },
    
    # 라우팅 정보
    "routing_info": {
        "selected_api": str,          # 선택된 API
        "reason": str,                # 선택 이유
        "used_expanded_query": bool   # 확장 쿼리 사용 여부
    },
    
    # 검색 결과
    "results": List[Dict] | Dict,     # 검색 결과
    
    # Fallback 정보 (사용 시)
    "fallback_used": bool,
    "fallback_info": Dict,
    
    # SERP 정보 (사용 시)
    "serp_enabled": bool,
    "serp_results": List[Dict],
    
    # 추가 정보
    "additional_info": Dict
}
```

## 🔧 핵심 컴포넌트 상세 분석

### 1️⃣ 쿼리 분석기 (QueryAnalyzer)

**파일**: [`app/search/query_analyzer.py`](project-folder/app-backend-fastapi/app/search/query_analyzer.py)

#### 기능

1. **개체명 추출 (EntityExtractor)**
   - 증상 키워드 추출 (예: "피로", "통증")
   - 성분 키워드 추출 (예: "비타민C", "오메가3")
   - 신체 부위 추출 (예: "눈", "관절")
   - 효과 키워드 추출 (예: "개선", "완화")

2. **의도 분류 (IntentClassifier)**
   - `SYMPTOM_SEARCH`: 증상 기반 검색
   - `INGREDIENT_SEARCH`: 성분 검색
   - `TIMING_QUERY`: 복용 시간 질문
   - `EFFECT_QUERY`: 효과 질문
   - `PRODUCT_SEARCH`: 제품 검색
   - `GENERAL_SEARCH`: 일반 검색
   - `MIXED`: 복합 의도

3. **쿼리 확장 (QueryExpander)**
   - 동의어 추가 (예: "피로" → "피곤", "지침", "무기력")
   - 컨텍스트 키워드 추가
   - 최대 3배까지 쿼리 확장

#### 예시

```python
# 입력
query = "눈이 피로해요"

# 출력
{
    "original_query": "눈이 피로해요",
    "entities": {
        "symptoms": ["피로"],
        "body_parts": ["눈"],
        "ingredients": [],
        "effects": []
    },
    "intent": "SYMPTOM_SEARCH",
    "expanded_query": "눈 피로 피곤 지침 시력 안구 눈건강 눈피로 시력보호 안구건조",
    "knowledge_match": {
        "nutrients": ["루테인", "지아잔틴", "비타민A"],
        "description": "눈 건강에 도움이 되는 영양소"
    }
}
```

### 2️⃣ 스마트 라우터 (SmartRouter)

**파일**: [`app/search/smart_router.py`](project-folder/app-backend-fastapi/app/search/smart_router.py)

#### 라우팅 로직

```python
if intent == "TIMING_QUERY" and ingredients:
    → timing_recommend API
    
elif intent == "INGREDIENT_SEARCH" and ingredients:
    → ingredient_search API
    
elif intent == "SYMPTOM_SEARCH" or symptoms:
    → symptom_recommend API
    
else:
    → hybrid_search API (확장된 쿼리 사용)
```

#### 라우팅 예시

| 쿼리 | 의도 | 선택된 API |
|------|------|-----------|
| "비타민C 언제 먹어요?" | TIMING_QUERY | `timing_recommend` |
| "비타민C 포함된 제품" | INGREDIENT_SEARCH | `ingredient_search` |
| "눈이 피로해요" | SYMPTOM_SEARCH | `symptom_recommend` |
| "관절에 좋은 영양제" | GENERAL_SEARCH | `hybrid_search` |

### 3️⃣ Fallback 시스템 (FallbackSystem)

**파일**: [`app/search/fallback_system.py`](project-folder/app-backend-fastapi/app/search/fallback_system.py)

#### 작동 조건

- 검색 결과가 2개 미만일 때
- `enable_fallback=True`일 때

#### Fallback 응답 유형

1. **카테고리 기반 기본 추천**
   ```python
   {
       "category": "눈 건강",
       "message": "눈 건강에 도움이 되는 일반적인 제품을 추천합니다.",
       "suggested_products": ["루테인", "지아잔틴", "비타민A"],
       "health_tips": ["...", "..."],
       "related_faqs": [...]
   }
   ```

2. **증상 기반 영양소 추천**
   ```python
   {
       "detected_symptom": "피로",
       "recommended_nutrients": ["비타민B", "마그네슘", "코엔자임Q10"],
       "description": "피로 회복에 도움이 되는 영양소"
   }
   ```

3. **성분 정보 제공**
   ```python
   {
       "detected_ingredient": "칼슘",
       "timing": "식후 30분",
       "synergy_with": ["비타민D", "마그네슘"],
       "avoid_with": ["철분", "카페인"]
   }
   ```

### 4️⃣ Re-ranking 시스템 (ResultReRanker)

**파일**: [`app/search/reranker.py`](project-folder/app-backend-fastapi/app/search/reranker.py)

#### 점수 계산 공식

```
최종 점수 = 검색점수(60%) + 인기도(20%) + 신뢰도(10%) + 최신성(10%)
```

#### 점수 구성 요소

1. **검색 점수 (60%)**
   - Elasticsearch 하이브리드 검색 점수

2. **인기도 점수 (20%)**
   - 인기 키워드 포함 여부
   - 예: "비타민", "오메가", "프로바이오틱스"

3. **신뢰도 점수 (10%)**
   - 신뢰할 수 있는 제조사
   - 예: 종근당, 유한양행, 대웅제약 등

4. **최신성 점수 (10%)**
   - 최근 5년 이내: 1.0
   - 5-10년: 0.7
   - 10년 이상: 0.3

#### 다양성 필터링

`enable_diversity=True`일 때:
- 같은 제조사 제품을 최대 2개까지만 표시
- 다양한 브랜드 노출

### 5️⃣ SERP 검색 (선택적)

**조건**: `enable_serp=True`

**기능**: Google 검색 결과를 비동기로 가져와 추가 정보 제공

**장점**:
- 최신 정보 제공
- 외부 리뷰/블로그 정보
- RAG 데이터 보완

## 🔄 전체 처리 흐름

### 예시: "눈이 피로해요" 검색

```
1. 쿼리 분석
   - 개체명: symptoms=["피로"], body_parts=["눈"]
   - 의도: SYMPTOM_SEARCH
   - 확장: "눈 피로 피곤 시력 안구 루테인 지아잔틴..."

2. SERP 검색 (비동기)
   - Google에서 "눈이 피로해요" 검색
   - 5개 결과 수집

3. 스마트 라우팅
   - 의도가 SYMPTOM_SEARCH
   - → symptom_recommend API 호출
   - 증상: "피로"

4. 검색 실행
   - RecommendationService.recommend_by_symptom("피로")
   - 결과: 3개 제품 추천

5. Fallback 체크
   - 결과 3개 > threshold 2개
   - → Fallback 사용 안 함

6. Re-ranking
   - 각 제품에 점수 재계산
   - 신뢰도 높은 제조사 우선
   - 최신 제품 우선

7. 추가 정보 보강
   - 증상 가이드 추가
   - 추천 영양소: ["루테인", "비타민A", "오메가3"]

8. 최종 응답
   - 재정렬된 3개 제품
   - SERP 결과 5개
   - 증상 가이드
   - 추천 영양소
```

## 📊 응답 예시

### 성공 응답

```json
{
    "success": true,
    "message": "검색 완료 (API: symptom_recommend)",
    "query_analysis": {
        "original_query": "눈이 피로해요",
        "entities": {
            "symptoms": ["피로"],
            "ingredients": [],
            "body_parts": ["눈"],
            "effects": []
        },
        "intent": "SYMPTOM_SEARCH",
        "expanded_query": "눈 피로 피곤 지침 시력 안구 눈건강",
        "knowledge_match": {
            "nutrients": ["루테인", "지아잔틴", "비타민A"],
            "description": "눈 건강에 도움"
        }
    },
    "routing_info": {
        "selected_api": "symptom_recommend",
        "reason": "증상 감지",
        "symptom": "피로"
    },
    "results": {
        "symptom": "피로",
        "recommendations": [
            {
                "product_name": "루테인 지아잔틴",
                "company_name": "종근당",
                "score": 0.95,
                "rerank_score": 0.92,
                "score_breakdown": {
                    "base": 0.95,
                    "popularity": 0.8,
                    "trust": 1.0,
                    "recency": 1.0
                }
            }
        ]
    },
    "fallback_used": false,
    "serp_enabled": true,
    "serp_results": [
        {
            "title": "눈 피로에 좋은 영양제 추천",
            "link": "https://...",
            "snippet": "루테인과 지아잔틴이 눈 건강에..."
        }
    ],
    "additional_info": {
        "symptom_guide": {
            "symptom": "피로",
            "recommended_nutrients": ["루테인", "비타민A", "오메가3"],
            "description": "눈 피로 완화에 도움"
        }
    }
}
```

## 🎯 사용 시나리오

### 시나리오 1: 증상 기반 검색

```bash
POST /api/v1/search/intelligent
{
    "query": "관절이 아파요",
    "top_k": 5,
    "enable_reranking": true
}

→ 의도: SYMPTOM_SEARCH
→ API: symptom_recommend
→ 결과: 글루코사민, 콘드로이틴, MSM 제품 추천
```

### 시나리오 2: 성분 검색

```bash
POST /api/v1/search/intelligent
{
    "query": "비타민C 포함된 제품",
    "top_k": 10,
    "enable_diversity": true
}

→ 의도: INGREDIENT_SEARCH
→ API: ingredient_search
→ 결과: 다양한 브랜드의 비타민C 제품 (제조사당 최대 2개)
```

### 시나리오 3: 복용 시간 질문

```bash
POST /api/v1/search/intelligent
{
    "query": "칼슘은 언제 먹어야 하나요?",
    "top_k": 5
}

→ 의도: TIMING_QUERY
→ API: timing_recommend
→ 결과: 칼슘 복용 시간, 상호작용 정보
```

### 시나리오 4: SERP 통합 검색

```bash
POST /api/v1/search/intelligent
{
    "query": "면역력 강화",
    "top_k": 5,
    "enable_serp": true,
    "serp_max_results": 5
}

→ 의도: GENERAL_SEARCH
→ API: hybrid_search
→ 결과: RAG 검색 5개 + Google 검색 5개
```

## 🔍 다른 엔드포인트와의 비교

| 엔드포인트 | 기능 | 지능형 검색 차이점 |
|-----------|------|------------------|
| `/search/hybrid` | 기본 하이브리드 검색 | ❌ 쿼리 분석 없음<br>❌ 라우팅 없음<br>❌ Fallback 없음 |
| `/search/symptom` | 증상 검색 | ❌ 고정된 API<br>❌ 쿼리 확장 없음 |
| `/search/ingredient` | 성분 검색 | ❌ 고정된 API<br>❌ Re-ranking 없음 |
| **`/search/intelligent`** | **지능형 검색** | ✅ 자동 의도 파악<br>✅ 최적 API 선택<br>✅ 쿼리 확장<br>✅ Re-ranking<br>✅ Fallback<br>✅ SERP 통합 |

## 💡 장점

1. **자동 의도 파악**: 사용자가 어떤 API를 써야 할지 고민할 필요 없음
2. **쿼리 확장**: 동의어/유사어로 검색 범위 확대
3. **스마트 라우팅**: 쿼리에 가장 적합한 API 자동 선택
4. **Fallback**: 결과가 부족해도 유용한 정보 제공
5. **Re-ranking**: 품질 높은 결과 우선 표시
6. **SERP 통합**: 최신 외부 정보 추가
7. **추가 정보**: 증상 가이드, 영양소 추천 등

## ⚠️ 주의사항

1. **SERP 검색**: API 키 필요, 비용 발생 가능
2. **처리 시간**: 여러 단계를 거치므로 기본 검색보다 느릴 수 있음
3. **복잡도**: 디버깅이 어려울 수 있음

## 🔗 관련 파일

- **라우터**: [`app/api/v1/endpoints/rag/routes.py`](project-folder/app-backend-fastapi/app/api/v1/endpoints/rag/routes.py#L221-L334)
- **스키마**: [`app/schemas/rag/schemas.py`](project-folder/app-backend-fastapi/app/schemas/rag/schemas.py)
- **쿼리 분석기**: [`app/search/query_analyzer.py`](project-folder/app-backend-fastapi/app/search/query_analyzer.py)
- **스마트 라우터**: [`app/search/smart_router.py`](project-folder/app-backend-fastapi/app/search/smart_router.py)
- **Fallback 시스템**: [`app/search/fallback_system.py`](project-folder/app-backend-fastapi/app/search/fallback_system.py)
- **Re-ranker**: [`app/search/reranker.py`](project-folder/app-backend-fastapi/app/search/reranker.py)

## 📝 요약

`/api/v1/rag/search/intelligent`는 **가장 고급화된 검색 엔드포인트**로, 사용자 쿼리를 지능적으로 분석하여 최적의 결과를 제공합니다. 

**핵심 특징**:
- 🧠 자동 의도 파악 및 개체명 추출
- 🎯 스마트 라우팅으로 최적 API 선택
- 📈 쿼리 확장으로 검색 범위 확대
- 🔄 Re-ranking으로 품질 향상
- 🛡️ Fallback으로 항상 유용한 응답
- 🌐 SERP 통합으로 최신 정보 제공

**추천 사용 케이스**: 챗봇, 자연어 검색, 통합 검색 인터페이스

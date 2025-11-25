# 지능형 검색 API 사용 가이드

## 개요

새로운 `/api/search/intelligent` 엔드포인트는 쿼리를 지능적으로 분석하여 최적의 검색 결과를 제공합니다.

## 주요 기능

### 1. 쿼리 분석 (Query Analysis)
- **개체명 추출**: 증상, 성분, 신체 부위 자동 인식
- **의도 분류**: 검색 의도 파악 (증상 검색, 성분 검색, 복용 시간 질문 등)
- **쿼리 확장**: 동의어/유사어 자동 추가

### 2. 스마트 라우팅 (Smart Routing)
- 쿼리 의도에 따라 최적의 API 자동 선택
- 복합 쿼리 처리

### 3. Fallback 응답
- 검색 결과 부족 시 카테고리별 기본 추천 제공
- 관련 건강 정보 제공

### 4. Re-ranking
- 검색 관련성, 인기도, 신뢰도, 최신성 종합 고려
- 다양성 필터링 옵션

## API 사용법

### 기본 요청

```bash
POST /api/search/intelligent
Content-Type: application/json

{
  "query": "눈이 피로하고 비타민C가 필요해요",
  "top_k": 5,
  "enable_fallback": true,
  "enable_reranking": true,
  "enable_diversity": false
}
```

### 응답 예시

```json
{
  "success": true,
  "message": "검색 완료 (API: hybrid_search)",
  "query_analysis": {
    "original_query": "눈이 피로하고 비타민C가 필요해요",
    "entities": {
      "symptoms": ["피로"],
      "ingredients": ["비타민C"],
      "body_parts": ["눈"],
      "effects": []
    },
    "intent": "MIXED",
    "expanded_query": "눈 피로 피곤 지침 시력 안구 비타민C 아스코르브산",
    "knowledge_match": {
      "category": "눈",
      "nutrients": ["루테인", "지아잔틴", "빌베리", "아스타잔틴", "비타민A", "오메가3"],
      "description": "눈 건강에는 루테인, 지아잔틴, 오메가3가 도움이 됩니다."
    }
  },
  "routing_info": {
    "selected_api": "hybrid_search",
    "reason": "복합 쿼리 또는 일반 검색",
    "used_expanded_query": true,
    "original_query": "눈이 피로하고 비타민C가 필요해요",
    "expanded_query": "눈 피로 피곤 지침 시력 안구 비타민C 아스코르브산"
  },
  "results": [
    {
      "score": 1.85,
      "rerank_score": 1.92,
      "product_name": "루테인 지아잔틴 비타민C",
      "company_name": "종근당",
      "primary_function": "눈 건강",
      "score_breakdown": {
        "base": 1.85,
        "popularity": 0.6,
        "trust": 1.0,
        "recency": 1.0
      }
    }
  ],
  "fallback_used": false,
  "additional_info": {
    "symptom_guide": {
      "symptom": "피로",
      "recommended_nutrients": ["비타민B1", "비타민B2", "마그네슘"],
      "description": "피로 회복에는 비타민B군과 마그네슘이 도움이 됩니다."
    },
    "interaction_guide": {
      "ingredient": "비타민C",
      "timing": "아침 식후",
      "synergy_with": ["철분", "콜라겐"],
      "avoid_with": []
    }
  }
}
```

## 테스트 쿼리 예시

### 1. 증상 기반 검색
```json
{
  "query": "눈이 피로해요",
  "top_k": 5
}
```
→ 증상 추천 API로 라우팅 → 루테인, 빌베리 제품 추천

### 2. 성분 검색
```json
{
  "query": "비타민C 성분이 포함된 제품",
  "top_k": 10
}
```
→ 성분 검색 API로 라우팅 → 비타민C 함유 제품 목록

### 3. 복용 시간 질문
```json
{
  "query": "칼슘은 언제 먹어야 하나요?",
  "top_k": 5
}
```
→ 복용 시간 추천 API로 라우팅 → 칼슘 복용 가이드

### 4. 복합 쿼리
```json
{
  "query": "관절 건강에 좋고 MSM 성분이 들어있는 제품",
  "top_k": 5
}
```
→ 하이브리드 검색 (확장된 쿼리 사용)

### 5. Fallback 테스트
```json
{
  "query": "존재하지않는증상12345",
  "top_k": 5,
  "enable_fallback": true
}
```
→ 검색 결과 없음 → Fallback 응답 제공

## 파라미터 설명

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `query` | string | 필수 | 검색 쿼리 |
| `top_k` | integer | 5 | 결과 개수 (1-20) |
| `enable_fallback` | boolean | true | Fallback 응답 사용 여부 |
| `enable_reranking` | boolean | true | Re-ranking 사용 여부 |
| `enable_diversity` | boolean | false | 다양성 필터링 (같은 회사 제품 제한) |

## 응답 필드 설명

### query_analysis
- `original_query`: 원본 쿼리
- `entities`: 추출된 개체명 (증상, 성분, 신체 부위)
- `intent`: 분류된 의도
- `expanded_query`: 확장된 쿼리 (동의어 포함)
- `knowledge_match`: 지식 베이스 매칭 결과

### routing_info
- `selected_api`: 선택된 API
- `reason`: 라우팅 이유
- `used_expanded_query`: 확장 쿼리 사용 여부

### results
- 검색 결과 목록
- `rerank_score`: 재정렬 점수 (enable_reranking=true 시)
- `score_breakdown`: 점수 구성 (관련성, 인기도, 신뢰도, 최신성)

### additional_info (선택)
- `symptom_guide`: 증상 관련 가이드
- `interaction_guide`: 성분 상호작용 정보
- `timing_guide`: 복용 시간 가이드

### fallback_info (fallback 사용 시)
- `category`: 매칭된 카테고리
- `message`: 안내 메시지
- `suggested_products`: 추천 제품 목록
- `health_tips`: 건강 팁

## 기존 API와의 차이점

| 기능 | 기존 API | 지능형 검색 API |
|-----|---------|---------------|
| 쿼리 분석 | ❌ | ✅ 개체명 추출, 의도 분류 |
| 자동 라우팅 | ❌ | ✅ 의도에 따라 최적 API 선택 |
| 쿼리 확장 | ❌ | ✅ 동의어/유사어 자동 추가 |
| Fallback | ❌ | ✅ 결과 부족 시 기본 추천 |
| Re-ranking | ❌ | ✅ 다차원 점수 기반 재정렬 |
| 추가 정보 | ❌ | ✅ 건강 가이드 자동 제공 |

## 성능 고려사항

- 쿼리 분석 및 라우팅: ~50ms
- 검색 실행: 기존 API와 동일
- Re-ranking: ~10ms
- 전체 응답 시간: < 1초 (대부분의 경우)

## 주의사항

1. 기존 API는 그대로 유지되며 하위 호환성 보장
2. 지능형 검색은 더 많은 정보를 제공하지만 응답 크기가 큼
3. 간단한 검색은 기존 API 사용 권장
4. 복잡한 쿼리나 사용자 친화적 검색은 지능형 API 권장

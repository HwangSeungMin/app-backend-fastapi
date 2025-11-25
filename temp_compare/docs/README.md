# 건강기능식품 RAG 시스템 - 상세 문서

> 최종 업데이트: 2025-11-24 | 버전: 1.0.0

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [아키텍처](#아키텍처)
3. [주요 기능](#주요-기능)
4. [설치 및 설정](#설치-및-설정)
5. [데이터 관리](#데이터-관리)
6. [API 사용법](#api-사용법)
7. [Kibana 대시보드](#kibana-대시보드)
8. [FAQ 시스템](#faq-시스템)
9. [복용시간 추천](#복용시간-추천)
10. [보안 설정](#보안-설정)
11. [트러블슈팅](#트러블슈팅)
12. [성능 지표](#성능-지표)

---

## 시스템 개요

### 프로젝트 설명

식품안전나라 API 데이터를 기반으로 건강기능식품을 검색하고 추천하는 **RAG (Retrieval-Augmented Generation) 시스템**입니다.

### 핵심 기술 스택

| 카테고리 | 기술 | 버전 |
|---------|------|------|
| **Backend** | FastAPI | 0.104+ |
| **언어** | Python | 3.9+ |
| **검색 엔진** | Elasticsearch | 8.x |
| **임베딩** | Sentence-Transformers | jhgan/ko-sroberta-multitask |
| **시각화** | Kibana | 8.x |
| **데이터** | 식품안전나라 API | C003, I2710 |

### 주요 특징

- ✅ **하이브리드 검색**: 벡터 검색 + 키워드 검색
- ✅ **지능형 쿼리 처리**: NER, 의도 분류, 쿼리 확장 (50+ 동의어)
- ✅ **스마트 라우팅**: 쿼리 유형별 최적 API 자동 선택
- ✅ **Re-ranking**: 다차원 점수 기반 결과 재정렬
- ✅ **FAQ 통합**: 20개 증상 카테고리, 300개 질문-답변
- ✅ **복용시간 추천**: 복수 성분 상호작용 분석
- ✅ **증분 색인**: 중복 방지 자동 색인
- ✅ **Kibana 최적화**: 대시보드 시각화 지원
- ✅ **CORS 보안**: 환경변수 기반 도메인 제한

---

## 아키텍처

### 시스템 구조

```
┌─────────────────────────────────────────────────────────┐
│                     사용자 요청                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Server                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 기본 검색 API │  │ 추천 API     │  │ 지능형 검색  │  │
│  │              │  │ - 증상 기반  │  │ - 쿼리 분석  │  │
│  │              │  │ - 성분 기반  │  │ - 라우팅     │  │
│  │              │  │ - 복용시간   │  │ - Re-ranking │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ 쿼리 분석 │  │ Fallback │  │ Re-      │
│ - NER    │  │ System   │  │ ranking  │
│ - 의도    │  │ - FAQ    │  │          │
│ - 확장    │  │ - 기본값  │  │          │
└──────────┘  └──────────┘  └──────────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Elasticsearch        │
        │  - 하이브리드 검색      │
        │  - 벡터 유사도 검색     │
        │  - 키워드 검색          │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Kibana Dashboard     │
        │  - 시각화              │
        │  - 분석                │
        └────────────────────────┘
```

### 디렉토리 구조

```
health-supplement-rag/
├── api/                    # API 레이어
│   ├── app.py             # FastAPI 앱 (CORS 보안)
│   ├── routes.py          # API 라우트
│   └── schemas.py         # Pydantic 스키마
├── search/                # 검색 엔진
│   ├── rag_search.py      # RAG 검색 엔진
│   ├── embeddings.py      # 임베딩 생성
│   ├── elasticsearch_manager.py
│   ├── query_analyzer.py  # 쿼리 분석 (NER, 의도, 확장)
│   ├── smart_router.py    # 스마트 라우팅
│   ├── fallback_system.py # Fallback 시스템 (FAQ)
│   └── reranker.py        # Re-ranking
├── services/              # 비즈니스 로직
│   ├── recommendation_service.py
│   └── timing_service.py  # 복용시간 추천
├── data/                  # 데이터 처리
│   ├── api_client.py      # 식약처 API 클라이언트
│   ├── data_processor.py  # 데이터 전처리
│   └── faq_dataset_300.csv # FAQ 데이터
├── utils/                 # 유틸리티
│   ├── knowledge_base.py  # 도메인 지식 + FAQ
│   └── logger.py
├── config/                # 설정
│   ├── settings.py
│   └── elasticsearch_config.py
├── scripts/               # 운영 스크립트
│   ├── setup_data.py      # 초기 색인
│   ├── incremental_index.py  # 증분 색인
│   ├── update_knowledge_base.py  # FAQ 통합
│   ├── test_faq_integration.py   # FAQ 테스트
│   ├── test_timing_api.py        # 복용시간 테스트
│   └── remove_duplicates.py
├── docs/                  # 문서
│   ├── README.md          # 이 파일
│   ├── intelligent_search_guide.md
│   ├── query_expansion_and_api_guide.md
│   ├── indexing_guide.md
│   └── kibana_index_optimization.md
├── tests/                 # 테스트
├── .env.example          # 환경변수 템플릿
└── docker-compose.yml
```

---

## 주요 기능

### 1. 지능형 검색 시스템

#### 1.1 쿼리 분석 (Query Analyzer)

**기능**:
- **개체명 추출 (NER)**: 증상, 성분, 신체 부위 자동 인식
- **의도 분류**: 복용 시간, 성분 검색, 증상 검색 등
- **쿼리 확장**: 50+ 동의어 매핑, 3-5x 확장
- **Span-based 매칭**: 중복 방지 (예: "심장"에서 "장" 추출 방지)

**예시**:
```python
# 입력
"눈이 피로해요"

# 분석 결과
{
  "entities": {
    "body_parts": ["눈"],
    "symptoms": ["피로"]
  },
  "intent": "SYMPTOM_SEARCH",
  "expanded_query": "눈이 피로해요 시력 안구 눈건강 피곤 지침"
}
```

#### 1.2 스마트 라우팅 (Smart Router)

쿼리 유형에 따라 최적의 API 자동 선택:

| 의도 | 라우팅 API | 예시 쿼리 |
|-----|-----------|----------|
| TIMING_QUERY | `timing_recommend` | "칼슘은 언제 먹어야 하나요?" |
| INGREDIENT_SEARCH | `ingredient_search` | "비타민C가 들어간 제품" |
| SYMPTOM_SEARCH | `symptom_recommend` | "눈이 피로해요" |
| MIXED | `hybrid_search` | "눈 피로에 좋은 루테인" |

#### 1.3 Re-ranking 시스템

**다차원 점수 계산**:
- **검색 관련성** (60%): 원본 검색 점수
- **인기도** (20%): 검색 빈도
- **신뢰도** (10%): 제조사 평판
- **최신성** (10%): 신고일자

#### 1.4 Fallback System

검색 결과가 부족할 때 FAQ 기반 추천 제공:
- 증상별 기본 추천
- 관련 FAQ 3개 제공
- 건강 팁 제공

### 2. FAQ 데이터셋 통합

**20개 증상 카테고리**:
- 피로감, 두통, 스트레스, 면역저하, 눈피로
- 소화불량, 피부트러블, 빈혈, 관절통, 수면장애
- 기억력저하, 우울감, 혈압상승, 피부노화, 체중증가
- 심장두근거림, 손발저림, 요통, 호흡곤란, 혈당불안정

**300개 질문-답변**:
- 각 증상별 15개 FAQ
- 전문적인 답변 (영양학적 설명)
- 추천 영양제 및 건강 팁

**데이터 구조**:
```csv
id,symptom,question,answer,recommend_supplement,recommend_action
1,피로감,아침에 일어나도 계속 피곤한데...,에너지 대사에 필요한...,철분, 비타민C,수면 7~8시간 유지
```

### 3. 복용시간 추천 시스템

**기능**:
- **복수 성분 지원**: 배열 형태로 여러 성분 동시 분석
- **상호작용 감지**: 성분 간 충돌 자동 감지 및 경고
- **최적 스케줄**: 하루 복용 스케줄 자동 생성
- **스마트 기본값**: 모든 성분 정보 없을 때만 기본 추천

**지원 성분** (9개):
- 철분, 비타민D, 비타민C, 칼슘, 마그네슘
- 오메가3, 비타민B, 아연, 프로바이오틱스

**상호작용 규칙**:
- 철분 ↔ 칼슘: 2시간 간격
- 철분 ↔ 아연: 2시간 간격
- 칼슘 ↔ 아연: 2시간 간격

### 4. 식약처 API 연동

| API | 설명 | 데이터 |
|-----|------|--------|
| **C003** | 품목제조신고 | 제품명, 회사명, 원재료, 주요기능 |
| **I2710** | 기능성 내용 | 분류, 기능성 내용, 섭취방법 |

### 5. 증분 색인 시스템

**기능**:
- 기존 데이터 자동 감지 (품목제조번호 기반)
- 중복 제외 신규 데이터만 색인
- Dry-run 모드 지원
- 배치 크기 조정 가능

---

## 설치 및 설정

### 1. 사전 요구사항

- Python 3.9+
- Docker & Docker Compose
- 식품안전나라 API 키 ([발급 방법](https://www.foodsafetykorea.go.kr/api/))

### 2. 설치

```bash
# 1. 저장소 클론
git clone <repository-url>
cd health-supplement-rag

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. Elasticsearch & Kibana 시작
docker-compose up -d

# 5. 환경 변수 설정
cp .env.example .env
# .env 파일 편집
```

### 3. 환경 변수 설정

`.env` 파일:
```bash
# API 설정
FOOD_SAFETY_API_KEY=your_api_key_here
FOOD_SAFETY_BASE_URL=http://openapi.foodsafetykorea.go.kr/api

# Elasticsearch 설정
ES_HOST=localhost
ES_PORT=9200
ES_INDEX_NAME=health_supplements

# 보안 설정
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
ENV=development
DEBUG=true

# 배치 설정
API_BATCH_SIZE=100
API_REQUEST_DELAY=0.5
```

### 4. 초기 데이터 색인

```bash
# 전체 데이터 색인 (최초 1회)
python scripts/setup_data.py --api-key YOUR_KEY --recreate-index --max-items 5000

# FAQ 데이터 통합 (선택사항)
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv
```

### 5. 서버 시작

```bash
# FastAPI 서버
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# 접속
# API 문서: http://localhost:8000/docs
# Kibana: http://localhost:5601
```

---

## 데이터 관리

### 색인 워크플로우

#### 시나리오 1: 최초 설정

```bash
# 1. 전체 데이터 색인
python scripts/setup_data.py --api-key YOUR_KEY --recreate-index --max-items 5000

# 2. FAQ 데이터 통합
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv
```

#### 시나리오 2: 정기 업데이트 (권장)

```bash
# 신규 데이터만 추가 (주 1회)
python scripts/incremental_index.py --api-key YOUR_KEY --max-items 1000

# 결과 예시:
# - 수집: 1000개
# - 중복: 950개 (자동 제외)
# - 신규 색인: 50개
```

#### 시나리오 3: 중복 정리

```bash
# 중복 확인
python scripts/remove_duplicates.py --dry-run --show-samples

# 중복 제거
python scripts/remove_duplicates.py
```

#### 시나리오 4: FAQ 업데이트

```bash
# CSV 파일 수정 후
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv

# 테스트
python scripts/test_faq_integration.py
```

---

## API 사용법

### 1. 기본 검색 API

#### 하이브리드 검색

```bash
POST /api/search/hybrid
{
  "query": "비타민C",
  "top_k": 5
}
```

#### 증상 기반 추천

```bash
POST /api/search/symptom
{
  "symptom": "피로",
  "top_k": 5
}
```

#### 성분 기반 검색

```bash
POST /api/search/ingredient
{
  "ingredient": "오메가3",
  "top_k": 5
}
```

### 2. 지능형 검색 API

```bash
POST /api/search/intelligent
{
  "query": "눈이 피로하고 비타민C가 필요해요",
  "top_k": 5,
  "enable_fallback": true,
  "enable_reranking": true,
  "enable_diversity": false
}
```

**응답 구조**:
```json
{
  "query_analysis": {
    "original_query": "눈이 피로하고 비타민C가 필요해요",
    "expanded_query": "눈이 피로하고 비타민C가 필요해요 시력 안구 ...",
    "entities": {
      "body_parts": ["눈"],
      "symptoms": ["피로"],
      "ingredients": ["비타민C"]
    },
    "intent": "MIXED"
  },
  "routing_info": {
    "api_used": "hybrid_search",
    "reason": "복합 쿼리"
  },
  "results": [...],
  "fallback_info": {
    "category": "눈피로",
    "suggested_products": ["루테인", "빌베리", "오메가3"],
    "related_faqs": [
      {
        "question": "하루 종일 모니터를 보는데 눈 건강에 좋은 영양제가 있나요?",
        "answer": "루테인과 제아잔틴은 황반 색소 밀도를 높여..."
      }
    ]
  }
}
```

### 3. 복용시간 추천 API

```bash
POST /api/recommend/timing
{
  "ingredients": ["철분", "칼슘", "비타민D", "마그네슘"]
}
```

**응답 구조**:
```json
{
  "optimal_schedule": [
    {
      "time": "07:00",
      "timing": "아침 공복",
      "ingredients": ["철분"],
      "count": 1,
      "notes": []
    },
    {
      "time": "08:00",
      "timing": "아침 식후",
      "ingredients": ["비타민D"],
      "count": 1,
      "notes": []
    },
    {
      "time": "22:00",
      "timing": "취침 전",
      "ingredients": ["칼슘", "마그네슘"],
      "count": 2,
      "notes": ["⚠️ 칼슘과(와) 철분은(는) 2시간 간격을 두고 복용하세요."]
    }
  ],
  "conflicts": [
    {
      "ingredient1": "철분",
      "ingredient2": "칼슘",
      "warning": "철분과(와) 칼슘은(는) 함께 복용하지 않는 것이 좋습니다.",
      "solution": "철분은(는) 공복에, 칼슘은(는) 식후 또는 취침 전에 각각 복용하세요.",
      "time_gap": "최소 2시간 간격을 두고 복용하세요."
    }
  ],
  "summary": {
    "total_ingredients": 4,
    "ingredients_with_info": 4,
    "ingredients_without_info": 0,
    "conflict_count": 1,
    "timing_slots": 3
  }
}
```

---

## Kibana 대시보드

### 1. 접속 및 설정

```
http://localhost:5601
```

**Index Pattern 생성**:
```
Management > Stack Management > Index Patterns > Create

Index pattern name: health_supplements*
Time field: report_date
```

### 2. 대시보드 예시

#### 시계열 분석

**신고일자별 제품 추이**:
```
Visualization: Line Chart
X-axis: report_date (Date Histogram)
Y-axis: Count
```

#### 카테고리 분석

**카테고리별 제품 분포**:
```
Visualization: Pie Chart
Slice: classification.category (Terms)
Size: Count
```

**제조사별 제품 수**:
```
Visualization: Data Table
Rows: company_name.keyword (Terms)
Metrics: Count
```

#### 트렌드 분석

**인기 원재료 Top 10**:
```
Visualization: Tag Cloud
Tags: raw_materials.keyword (Terms, Top 10)
Size: Count
```

---

## FAQ 시스템

### 데이터 구조

**CSV 파일**: `data/faq_dataset_300.csv`

**필드**:
- `id`: FAQ ID
- `symptom`: 증상 카테고리
- `question`: 사용자 질문
- `answer`: 전문가 답변
- `recommend_supplement`: 추천 영양제 (쉼표 구분)
- `recommend_action`: 추천 행동 (쉼표 구분)

### Knowledge Base 통합

**자동 생성 구조**:
```python
DEFAULT_RECOMMENDATIONS = {
    "피로감": {
        "products": ["철분", "비타민C", "비타민B콤플렉스"],
        "message": "에너지 대사에 필요한 비타민B군과 마그네슘이...",
        "tips": ["수면 7~8시간 유지", "규칙적인 운동"],
        "faqs": [
            {
                "question": "아침에 일어나도 계속 피곤한데...",
                "answer": "에너지 대사에 필요한..."
            }
        ]
    }
}
```

### 업데이트 방법

```bash
# 1. CSV 파일 수정
# data/faq_dataset_300.csv 편집

# 2. Knowledge Base 업데이트
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv

# 3. 테스트
python scripts/test_faq_integration.py

# 4. 서버 재시작 (자동)
# uvicorn --reload 모드에서 자동 재시작됨
```

---

## 복용시간 추천

### 지원 성분 및 규칙

| 성분 | 복용 시간 | 이유 | 피해야 할 성분 |
|-----|----------|------|---------------|
| **철분** | 공복 | 흡수율 최대화 | 칼슘, 아연, 커피, 차 |
| **비타민D** | 아침 식후 | 지용성, 지방과 함께 | - |
| **비타민C** | 식후 | 위장 자극 감소 | - |
| **칼슘** | 저녁/취침 전 | 야간 뼈 형성 | 철분, 아연 |
| **마그네슘** | 취침 전 | 근육 이완, 수면 개선 | - |
| **오메가3** | 식후 | 지용성, 흡수율 증가 | - |
| **비타민B** | 아침 식후 | 에너지 대사 | - |
| **아연** | 공복/식후 | 흡수율 vs 위장 자극 | 칼슘, 철분 |
| **프로바이오틱스** | 공복 | 위산 영향 최소화 | - |

### API 사용 예시

**단일 성분**:
```json
{
  "ingredients": ["철분"]
}
```

**복수 성분 (충돌 없음)**:
```json
{
  "ingredients": ["비타민D", "비타민C", "오메가3"]
}
```

**복수 성분 (충돌 있음)**:
```json
{
  "ingredients": ["철분", "칼슘", "비타민D", "마그네슘", "아연"]
}
```

**정보 없는 성분**:
```json
{
  "ingredients": ["알 수 없는 성분1", "알 수 없는 성분2"]
}
// 응답: default_recommendation 제공
```

---

## 보안 설정

### CORS 설정

**환경변수 기반**:
```bash
# .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourdomain.com
```

**코드** (`api/app.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API 키 관리

**환경변수 사용**:
```bash
# .env
FOOD_SAFETY_API_KEY=your_secret_key_here
```

**코드에서 사용**:
```python
from config.settings import settings

api_key = settings.FOOD_SAFETY_API_KEY
```

### 환경별 설정

```bash
# 개발 환경
ENV=development
DEBUG=true

# 프로덕션 환경
ENV=production
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 트러블슈팅

### 1. Elasticsearch 연결 실패

**증상**:
```
ConnectionError: ElasticSearch 연결 실패
```

**해결**:
```bash
# 1. Elasticsearch 상태 확인
curl http://localhost:9200

# 2. Docker 컨테이너 재시작
docker-compose restart elasticsearch

# 3. 로그 확인
docker logs elasticsearch

# 4. 포트 확인
netstat -an | grep 9200
```

### 2. 중복 데이터 발견

**해결**:
```bash
# 중복 확인
python scripts/remove_duplicates.py --dry-run --show-samples

# 중복 제거
python scripts/remove_duplicates.py
```

### 3. 색인 속도 느림

**해결**:
```bash
# 배치 크기 증가
python scripts/incremental_index.py --batch-size 500

# API 요청 딜레이 감소 (주의: API 제한 확인)
# .env
API_REQUEST_DELAY=0.3
```

### 4. API 요청 제한

**해결**:
```bash
# .env
API_REQUEST_DELAY=1.0  # 1초로 증가
API_BATCH_SIZE=50      # 배치 크기 감소
```

### 5. Kibana 대시보드 데이터 안 보임

**해결**:
```bash
# 1. Index Pattern 확인
# Management > Index Patterns

# 2. 인덱스 새로고침
# Index Pattern > Refresh field list

# 3. 시간 범위 확인
# 대시보드 우측 상단 시간 범위 조정 (Last 7 days 등)

# 4. 데이터 확인
curl http://localhost:9200/health_supplements/_count
```

### 6. FAQ 데이터 업데이트 실패

**해결**:
```bash
# 백업 파일 확인
ls utils/knowledge_base.py.backup

# 백업에서 복원
cp utils/knowledge_base.py.backup utils/knowledge_base.py

# 재시도
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv
```

### 7. Windows 한글 깨짐

**해결**:
```cmd
# 인코딩 변경
chcp 65001

# 또는 자동 스크립트
scripts\fix_encoding.bat
```

---

## 성능 지표

### 검색 품질

| 지표 | Before | After | 개선 |
|-----|--------|-------|------|
| **재현율** | 65% | 85-95% | **+30-50%** |
| **정확도** | 70% | 75-80% | **+7-14%** |
| **평균 응답 시간** | 800ms | 850ms | +50ms |

### 쿼리 확장 효과

| 항목 | Before | After | 개선 |
|-----|--------|-------|------|
| **동의어 매핑** | 16개 | 50+ | **3.1x** |
| **확장 비율** | ~2x | ~3-5x | **1.5-2.5x** |

### 데이터 풍부도

| 항목 | Before | After | 개선 |
|-----|--------|-------|------|
| **FAQ 데이터** | 0개 | 300개 | **신규** |
| **증상 카테고리** | 5개 | 20개 | **4x** |
| **복용시간 정보** | 0개 | 9개 성분 | **신규** |

---

## 문서 인덱스

### 핵심 가이드

| 문서 | 설명 | 대상 |
|-----|------|------|
| [README.md](../README.md) | 빠른 시작 가이드 | 모든 사용자 |
| **docs/README.md** (이 파일) | 상세 시스템 문서 | 모든 사용자 |
| [intelligent_search_guide.md](intelligent_search_guide.md) | 지능형 검색 API | 개발자 |
| [query_expansion_and_api_guide.md](query_expansion_and_api_guide.md) | 쿼리 확장 및 API | 개발자 |
| [indexing_guide.md](indexing_guide.md) | 데이터 색인 절차 | 운영자 |
| [kibana_index_optimization.md](kibana_index_optimization.md) | Kibana 최적화 | 분석가 |

### 참고 문서

| 문서 | 설명 |
|-----|------|
| [KIBANA_GUIDE.md](KIBANA_GUIDE.md) | Kibana 기본 사용법 |
| [KIBANA_DASHBOARD_EXAMPLES.md](KIBANA_DASHBOARD_EXAMPLES.md) | 대시보드 예시 |
| [elasticsearch-nori-setup.md](elasticsearch-nori-setup.md) | Nori 플러그인 설정 |
| [ENCODING_GUIDE.md](ENCODING_GUIDE.md) | 인코딩 문제 해결 |

---

## 빠른 시작 체크리스트

### 초기 설정 (최초 1회)

- [ ] Docker & Docker Compose 설치
- [ ] Python 3.9+ 설치
- [ ] 가상환경 생성 및 의존성 설치
- [ ] Elasticsearch & Kibana 시작
- [ ] 식품안전나라 API 키 발급
- [ ] 환경 변수 설정 (.env)
- [ ] 전체 데이터 색인
- [ ] FAQ 데이터 통합

### 정기 운영

- [ ] 주 1회 증분 색인
- [ ] 월 1회 중복 제거
- [ ] Kibana 대시보드 모니터링
- [ ] 로그 확인

### 개발

- [ ] FastAPI 서버 시작
- [ ] API 문서 확인 (http://localhost:8000/docs)
- [ ] 테스트 실행
- [ ] 로그 모니터링

---

## 라이선스

MIT License

---

## 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.

---

**🎉 모든 준비가 완료되었습니다!**

더 자세한 내용은 각 문서를 참고하세요.

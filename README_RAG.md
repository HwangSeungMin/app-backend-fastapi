# 🏥 건강기능식품 RAG 시스템 (Yakkobak)

> **AI 기반 지능형 검색과 추천을 제공하는 건강기능식품 정보 시스템**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.11-yellow.svg)](https://www.elastic.co/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 🎯 핵심 기능

### 🔍 **지능형 검색 시스템**
- **쿼리 분석**: 자동 의도 파악 및 개체명 추출
- **스마트 라우팅**: 최적 API 자동 선택
- **쿼리 확장**: 동의어/유사어 자동 추가 (3배 확장)
- **Re-ranking**: 관련성, 인기도, 신뢰도 기반 결과 재정렬
- **Fallback 시스템**: 결과 부족 시 대안 제공

### 🤖 **AI 추천 엔진**
- **Gemini LLM 통합**: Google Gemini 2.0 Flash 기반 자연어 추천
- **다중 소스 융합**: RAG + SERP + Gemini 지식 통합
- **가중치 조절**: 데이터 vs AI 지식 비중 조정 (0.0-1.0)
- **증상 기반 추천**: 증상에 맞는 영양제 추천
- **성분 기반 검색**: 특정 성분 포함 제품 검색

### ⏰ **복용 시간 최적화**
- **복수 성분 분석**: 여러 영양제 동시 복용 스케줄링
- **상호작용 감지**: 성분 간 충돌 자동 감지
- **최적 시간 추천**: 식사 시간 기반 최적 복용 시간
- **알람 통합**: 기존 알람과 충돌 방지

### 📊 **데이터 시각화**
- **Kibana 대시보드**: 실시간 데이터 분석 및 시각화
- **통계 분석**: 제품 트렌드, 제조사 분석
- **FAQ 통합**: 300개 건강 관련 FAQ 데이터

---

## 🚀 빠른 시작

### 📋 **사전 요구사항**

- Python 3.12+
- Docker Desktop (실행 중)
- 8GB+ RAM
- 10GB+ 디스크 공간

### 🔧 **설치 및 실행**

```bash
# 1. 저장소 클론
git clone https://github.com/ShootingStar-5/app-backend-fastapi.git
cd app-backend-fastapi

# 2. 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. 의존성 설치
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일에서 API 키 설정 필요:
# - FOOD_SAFETY_API_KEY (식약처 API)
# - GEMINI_API_KEY (Google Gemini)
# - SERP_API_KEY (선택사항)

# 5. Docker 컨테이너 시작
docker-compose up -d

# 6. 데이터 색인 (최초 1회)
# 테스트용 (1000개)
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index --max-items 1000

# 전체 데이터
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index

# 7. 서버 시작
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 🌐 **접속 URL**

| 서비스 | URL | 설명 |
|--------|-----|------|
| **API 문서** | http://localhost:8000/docs | Swagger UI |
| **ReDoc** | http://localhost:8000/redoc | 대체 API 문서 |
| **Kibana** | http://localhost:5601 | 데이터 시각화 |
| **Elasticsearch** | http://localhost:9200 | 검색 엔진 |

---

## 📚 API 엔드포인트

### 🔍 **검색 API**

#### 1. 지능형 검색 (추천)
```bash
POST /api/v1/search/intelligent
{
  "query": "눈이 피로하고 비타민C가 필요해요",
  "top_k": 5,
  "enable_reranking": true,
  "enable_serp": true
}
```

#### 2. 하이브리드 검색
```bash
POST /api/v1/search/hybrid
{
  "query": "비타민",
  "top_k": 10
}
```

#### 3. 증상 기반 검색
```bash
POST /api/v1/search/symptom
{
  "symptom": "피로",
  "top_k": 5
}
```

#### 4. 성분 기반 검색
```bash
POST /api/v1/search/ingredient
{
  "ingredient": "비타민C",
  "top_k": 10
}
```

---

### 🤖 **AI 추천 API**

#### 1. Gemini 추천 (AI 융합)
```bash
POST /api/v1/recommend/gemini
{
  "query": "피로 회복에 좋은 영양제 추천해주세요",
  "top_k": 5,
  "enable_serp": true,
  "rag_weight": 0.5,
  "max_length": 200
}
```

#### 2. 증상 기반 추천
```bash
POST /api/v1/recommend/symptom
{
  "symptom": "관절통",
  "top_k": 3
}
```

#### 3. 복용 시간 추천
```bash
POST /api/v1/recommend/timing
{
  "ingredients": ["철분", "칼슘", "비타민D"],
  "user_meal_times": {
    "breakfast": "08:00",
    "lunch": "12:00",
    "dinner": "18:00"
  }
}
```

---

## 🛠️ 기술 스택

### **Backend**
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.12+
- **ASGI Server**: Uvicorn

### **검색 & AI**
- **검색 엔진**: Elasticsearch 8.11
- **임베딩 모델**: jhgan/ko-sroberta-multitask (768차원)
- **LLM**: Google Gemini 2.0 Flash
- **벡터 검색**: Dense Vector + BM25 하이브리드

### **데이터**
- **주요 데이터**: 식품안전나라 C003 API (건강기능식품)
- **FAQ 데이터**: 300개 건강 관련 질문/답변
- **외부 검색**: Google SERP API (선택)

### **인프라**
- **컨테이너**: Docker + Docker Compose
- **시각화**: Kibana 8.11
- **로깅**: Python logging + Elasticsearch

---

## 📖 상세 문서

### **API 문서**
- 📘 [지능형 검색 API](docs/API_INTELLIGENT_SEARCH.md) - 쿼리 분석, 스마트 라우팅, Fallback
- 🤖 [Gemini 추천 API](docs/API_GEMINI_RECOMMEND.md) - AI 기반 융합 추천

### **설정 가이드**
- 🐳 [Docker 가이드](docs/DOCKER_GUIDE.md) - Docker 설정 및 배포
- 📊 [Kibana 가이드](docs/KIBANA_GUIDE.md) - 대시보드 설정
- 🔍 [Elasticsearch 설정](docs/elasticsearch-nori-setup.md) - Nori 분석기 설정

### **데이터 관리**
- 📝 [색인 가이드](docs/indexing_guide.md) - 데이터 색인 절차
- 🔧 [인덱스 구조 개선](docs/INDEX_STRUCTURE_IMPROVEMENT.md) - 스키마 최적화

### **전체 문서**
- 📚 [전체 시스템 문서](docs/README.md) - 종합 가이드

---

## 🔧 주요 스크립트

### **데이터 관리**

```bash
# 전체 데이터 색인 (최초)
python scripts/setup_data.py --api-key YOUR_KEY --recreate-index

# 증분 색인 (정기 업데이트)
python scripts/incremental_index.py --api-key YOUR_KEY

# 인덱스 통계 확인
python scripts/update_index.py stats

# FAQ 데이터 업데이트
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv
```

### **테스트**

```bash
# 검색 테스트
python scripts/test_search.py

# 지능형 검색 테스트
python scripts/test_intelligent_search.py

# Gemini 추천 테스트
python scripts/test_gemini_recommendation.py

# 복용 시간 API 테스트
python scripts/test_timing_api.py

# FAQ 통합 테스트
python scripts/test_faq_integration.py
```

### **Kibana 대시보드**

```bash
# 대시보드 Import
python scripts/import_kibana_dashboard.py

# 대시보드 백업
python scripts/backup_kibana_dashboard.py
```

---

## 📊 성능 지표

### **검색 품질**

| 지표 | 기존 | 개선 후 | 향상률 |
|------|------|---------|--------|
| **재현율** | 65% | 85-95% | **+30-50%** |
| **정확도** | 70% | 75-80% | **+7-14%** |
| **동의어 커버리지** | 16개 | 50+ | **3.1x** |

### **응답 시간**

| API | 평균 응답 시간 |
|-----|---------------|
| 하이브리드 검색 | ~200ms |
| 지능형 검색 | ~500ms |
| Gemini 추천 | ~2-4초 |
| 복용 시간 추천 | ~100ms |

### **데이터 규모**

- **제품 데이터**: 1,000+ (테스트) / 전체 가능
- **FAQ 데이터**: 300개
- **인덱스 크기**: ~3.2GB (압축) / ~9.9GB (로컬)

---

## 🐛 트러블슈팅

### **Elasticsearch 연결 오류**

```bash
# 상태 확인
curl http://localhost:9200

# 컨테이너 재시작
docker-compose restart elasticsearch

# 로그 확인
docker-compose logs elasticsearch
```

### **Kibana 접속 안 됨**

```bash
# Kibana 재시작
docker-compose restart kibana

# 대시보드 Import
python scripts/import_kibana_dashboard.py
```

### **색인 실패**

```bash
# 인덱스 삭제 후 재생성
python scripts/update_index.py delete
python scripts/setup_data.py --api-key YOUR_KEY --recreate-index --max-items 1000
```

### **Docker 메모리 부족**

```yaml
# docker-compose.yml 수정
environment:
  - "ES_JAVA_OPTS=-Xms2g -Xmx2g"  # 메모리 증가
```

---

## 🔐 환경 변수

### **필수 설정**

```bash
# .env 파일
FOOD_SAFETY_API_KEY=your_api_key_here  # 식약처 API 키
GEMINI_API_KEY=your_gemini_key_here    # Google Gemini API 키

# Elasticsearch
ES_HOST=localhost
ES_PORT=9200
ES_INDEX_NAME=health_supplements

# Gemini 설정
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.7
```

### **선택 설정**

```bash
# SERP API (선택)
SERP_API_KEY=your_serp_key_here
SERP_API_ENABLED=True

# RAG 가중치
RAG_WEIGHT=0.5
GEMINI_WEIGHT=0.5
```

---

## 🐳 Docker 배포

### **로컬 실행**

```bash
# 전체 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d elasticsearch kibana
```

### **Docker Hub 배포**

```bash
# 이미지 빌드 및 푸시
python scripts/push_to_dockerhub.ps1 -Username "your_username"

# 다른 환경에서 실행
docker pull your_username/app-backend-fastapi:latest
docker run -d -p 8000:8000 your_username/app-backend-fastapi:latest
```

**상세 가이드**: [DOCKER_HUB_PUSH_GUIDE.md](DOCKER_HUB_PUSH_GUIDE.md)

---

## 📝 라이선스

MIT License

---

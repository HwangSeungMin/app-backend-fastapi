# 건강기능식품 RAG 시스템

> **지능형 검색과 추천을 제공하는 건강기능식품 정보 시스템**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.x-yellow.svg)](https://www.elastic.co/)

## 🎯 핵심 기능

- 🔍 **지능형 검색**: 쿼리 분석, 의도 분류, 자동 확장
- 🎯 **스마트 추천**: 증상/성분 기반 맞춤 추천 + FAQ (300개)
- ⏰ **복용시간 추천**: 복수 성분 상호작용 분석 및 최적 스케줄
- ⭐ **Re-ranking**: 관련성, 인기도, 신뢰도 기반 결과 재정렬
- 📊 **Kibana 대시보드**: 실시간 데이터 시각화

## 🚀 빠른 시작


```bash
# 1. 설치
cd d:/yakkobak_be

git clone <repository-url>

python --version # 3.9 이상 

python -m venv venv # 가상환경 생성

# 가상환경 접속 
venv\Scripts\activate #Windows 
source venv/bin/activate  #Linux/Mac 

python.exe -m pip install --upgrade pip

pip install -r requirements.txt

# 2. 환경 설정
cp .env.example .env
# .env 파일에서 API 키 설정

## 기본 요구 조건 : Docker Desktop 설치 및 실행 

# 3. Elasticsearch & Kibana 시작
docker-compose up -d

# 4. 데이터 색인
python scripts/setup_data.py --api-key YOUR_KEY --max-items 5000

python scripts/setup_data.py --api-key 56a49a1dd780482f8fd4 --skip-collect

# 5. 서버 시작
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**접속**: 
- API 문서: http://localhost:8000/docs
- Kibana: http://localhost:5601

## 📚 API 예시

### 지능형 검색
```bash
POST /api/search/intelligent
{
  "query": "눈이 피로하고 비타민C가 필요해요",
  "top_k": 5
}
```

### 복용시간 추천
```bash
POST /api/recommend/timing
{
  "ingredients": ["철분", "칼슘", "비타민D"]
}
```

## 🛠️ 기술 스택

| 카테고리 | 기술 |
|---------|------|
| Backend | FastAPI, Python 3.9+ |
| 검색 엔진 | Elasticsearch 8.x |
| 임베딩 | Sentence-Transformers |
| 시각화 | Kibana 8.x |
| 데이터 | 식품안전나라 API + FAQ |

## 📖 문서

- **[📘 전체 문서](docs/README.md)** - 상세한 시스템 가이드
- [지능형 검색 가이드](docs/intelligent_search_guide.md)
- [쿼리 확장 & API 가이드](docs/query_expansion_and_api_guide.md)
- [데이터 색인 가이드](docs/indexing_guide.md)
- [Kibana 최적화 가이드](docs/kibana_index_optimization.md)

## 🔧 주요 명령어

```bash
# 정기 업데이트
python scripts/incremental_index.py --api-key YOUR_KEY

# FAQ 데이터 업데이트
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv

# 중복 제거
python scripts/remove_duplicates.py

# 테스트
python scripts/test_timing_api.py
python scripts/test_faq_integration.py
```

## 📊 성능

| 지표 | 개선 |
|-----|------|
| 재현율 | **+30-50%** (65% → 85-95%) |
| 정확도 | **+7-14%** (70% → 75-80%) |
| 동의어 | **3.1x** (16개 → 50+) |
| FAQ 데이터 | **300개** (신규) |

## 🐛 트러블슈팅

```bash
# Elasticsearch 연결 확인
curl http://localhost:9200

# 컨테이너 재시작
docker-compose restart

# 로그 확인
docker logs elasticsearch
```

## 📝 라이선스

MIT License

---

**📖 자세한 내용은 [docs/README.md](docs/README.md)를 참고하세요.**
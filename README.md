# 약꼬박 (Yakkobak) - 의약품 관리 앱 백엔드

팀 프로젝트로 개발하는 의약품 관리 모바일 앱의 백엔드 API 서버입니다.

## 📋 프로젝트 개요

약봉투 사진(OCR) 또는 음성(STT)을 통해 약 정보를 추출하고, RAG 기반 건강기능식품 추천 서비스를 제공하는 FastAPI 백엔드 서버입니다.

### 주요 기능

- **OCR (광학 문자 인식)**: 약봉투 사진에서 텍스트 추출 및 약 정보 파싱
- **STT (음성-텍스트 변환)**: 음성으로 약 정보 입력 및 의약품 복용 정보 추출
- **RAG 검색**: Elasticsearch 기반 건강기능식품 검색 및 추천
- **Gemini LLM**: Google Gemini를 활용한 지능형 추천
- **Kibana 대시보드**: 검색 로그 및 분석 시각화

### 아키텍처

```
┌─────────────┐      HTTP Request     ┌──────────────────┐
│             │ ──────────────────────> │                  │
│  Flutter    │   (이미지/음성 파일)   │  FastAPI Server  │
│  App        │                         │  + Elasticsearch │
│  (로컬 DB)  │ <────────────────────── │  + Kibana        │
└─────────────┘   JSON Response        └──────────────────┘
                                                 │
                                                 │ API Call
                                                 ▼
                                         ┌───────────────┐
                                         │ External APIs │
                                         │ - Azure OCR   │
                                         │ - Azure STT   │
                                         │ - Azure OpenAI│
                                         │ - Google Gemini│
                                         └───────────────┘
```

## 🛠️ 기술 스택

- **웹 프레임워크**: FastAPI 0.104+
- **검색 엔진**: Elasticsearch 8.11.0 (Nori 플러그인)
- **시각화**: Kibana 8.11.0
- **ML/임베딩**: Sentence Transformers, PyTorch
- **LLM**: Google Gemini, Azure OpenAI
- **컨테이너**: Docker, Docker Compose
- **외부 서비스**: 
  - Azure Computer Vision (OCR)
  - Azure Speech Service (STT)
  - Azure OpenAI (GPT-4)
  - Google Gemini API

## 📂 프로젝트 구조

```
app-backend-fastapi/
├── app/
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── api/                    # API 라우터
│   │   └── v1/
│   │       ├── endpoints/      # API 엔드포인트
│   │       │   ├── ocr/        # OCR API
│   │       │   ├── stt/        # STT API
│   │       │   ├── rag/        # RAG 검색 API
│   │       │   └── chatbot/    # 챗봇 API
│   │       └── api.py          # 라우터 통합
│   ├── core/                   # 핵심 설정
│   │   ├── config.py           # 환경 변수 관리
│   │   └── elasticsearch_config.py
│   ├── services/               # 비즈니스 로직
│   │   ├── ocr/                # OCR 서비스
│   │   ├── stt/                # STT 서비스
│   │   └── rag/                # RAG 서비스
│   ├── search/                 # 검색 엔진
│   │   ├── embeddings.py       # 임베딩 생성
│   │   ├── rag_search.py       # RAG 검색
│   │   └── smart_router.py     # 지능형 라우팅
│   ├── schemas/                # Pydantic 스키마
│   └── utils/                  # 유틸리티
├── scripts/                    # 데이터 처리 스크립트
├── data/                       # 데이터 파일
├── logs/                       # 로그 파일
├── requirements.txt            # Python 의존성
├── .env                        # 환경 변수 (직접 생성 필요)
├── .env.example                # 환경 변수 예시
├── Dockerfile                  # API 서버 이미지
├── docker-compose.yml          # Docker Compose 설정
└── README.md
```

## 🚀 빠른 시작

### 사전 요구사항

- **Docker Desktop** 설치 및 실행
  - [Windows용 Docker Desktop 다운로드](https://www.docker.com/products/docker-desktop/)
- **Git**
- **Python 3.12** (로컬 개발 시)

### 1. 저장소 클론

```bash
git clone https://github.com/ShootingStar-5/app-backend-fastapi.git
cd app-backend-fastapi

# develop 브랜치로 전환
git checkout develop
```

### 2. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.

**Windows (PowerShell)**:
```powershell
Copy-Item .env.example .env
```

**Mac/Linux**:
```bash
cp .env.example .env
```

`.env` 파일을 열어서 필요한 API 키를 설정합니다:

```env
# Azure Speech Service (STT)
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=westus3

# Azure OpenAI (LLM)
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Google Gemini LLM
GEMINI_API_KEY=your_gemini_api_key

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200
ES_HOST=elasticsearch
ES_PORT=9200
```

### 3. Docker로 서비스 실행

```bash
# 모든 서비스 시작 (API, Elasticsearch, Kibana)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f api
```

**실행되는 서비스**:
- `yakkobak-api`: FastAPI 서버 (포트 8000)
- `yakkobak-es`: Elasticsearch (포트 9200, 9300)
- `yakkobak-kibana`: Kibana (포트 5601)

### 4. 서비스 확인

브라우저에서 다음 URL로 접속:

- **API 문서 (Swagger)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601

헬스체크:
```bash
# API 헬스체크
curl http://localhost:8000/api/v1/health

# Elasticsearch 상태
curl http://localhost:9200/_cluster/health
```

### 5. 서비스 중지

```bash
# 서비스 중지 (데이터 보존)
docker-compose stop

# 서비스 중지 및 컨테이너 제거 (데이터 보존)
docker-compose down

# 서비스 중지 및 볼륨까지 삭제 (데이터 삭제)
docker-compose down -v
```

## 🔧 로컬 개발 환경 (선택사항)

Docker 없이 로컬에서 개발하려면:

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. 패키지 설치

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt
```

### 3. Elasticsearch 실행

```bash
# Docker로 Elasticsearch만 실행
docker-compose up -d elasticsearch kibana
```

### 4. 서버 실행

```bash
# 개발 서버 실행 (자동 리로드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📝 API 엔드포인트

### 헬스체크
```bash
GET /
GET /api/v1/health
```

### STT API
```bash
# 음성 → 텍스트 변환
POST /api/v1/stt/transcribe

# 음성 → 의약품 정보 추출
POST /api/v1/stt/extract

# 텍스트 → 의약품 정보 추출
POST /api/v1/stt/extract-text
```

### RAG 검색 API
```bash
# 건강기능식품 검색
POST /api/v1/rag/search

# 지능형 추천
POST /api/v1/rag/recommend
```

### OCR API
```bash
# 이미지 → 텍스트 추출
POST /api/v1/ocr/extract
```

자세한 API 사용법은 http://localhost:8000/docs 에서 확인하세요.

## 🐳 Docker 이미지 정보

### Elasticsearch 이미지
- **이미지**: `albob1403/yakkobak-elasticsearch:latest`
- **포함 내용**:
  - Elasticsearch 8.11.0
  - Nori 한글 분석 플러그인
  - 사전 색인된 건강기능식품 데이터

Docker Hub에서 자동으로 다운로드됩니다. 수동으로 받으려면:
```bash
docker pull albob1403/yakkobak-elasticsearch:latest
```

## 🤝 팀 협업 가이드

### Git 브랜치 전략

1. **새로운 기능 개발**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/기능명
   ```

2. **코드 작성 후 커밋**:
   ```bash
   git add .
   git commit -m "feat: 기능 설명"
   ```

3. **원격 저장소에 푸시**:
   ```bash
   git push origin feature/기능명
   ```

4. **Pull Request 생성**
   - GitHub에서 `feature/기능명` → `develop`으로 PR 생성
   - 팀원의 코드 리뷰 받기
   - 승인 후 merge

### 커밋 메시지 컨벤션

- `feat:` 새로운 기능 추가
- `fix:` 버그 수정
- `docs:` 문서 수정
- `refactor:` 코드 리팩토링
- `chore:` 빌드, 설정 파일 수정
- `test:` 테스트 코드 추가/수정

## 🐛 트러블슈팅

### Docker가 실행되지 않을 때

1. Docker Desktop이 실행 중인지 확인
2. Windows의 경우 WSL2가 설치되어 있는지 확인
3. Docker Desktop 재시작

### 포트 충돌

다른 프로그램이 포트를 사용 중이면 `docker-compose.yml`에서 포트 변경:
```yaml
ports:
  - "8001:8000"  # 8000 대신 8001 사용
```

### Elasticsearch 메모리 부족

`docker-compose.yml`에서 메모리 설정 조정:
```yaml
environment:
  - "ES_JAVA_OPTS=-Xms256m -Xmx256m"  # 512m에서 256m으로 감소
```

### 코드 변경이 반영되지 않을 때

```bash
# API 컨테이너 재시작
docker-compose restart api

# 또는 전체 재빌드
docker-compose up -d --build
```

## 📚 추가 문서

- [Docker 설정 가이드](DOCKER_SETUP.md)
- [RAG 시스템 설명](README_RAG.md)
- [Azure 배포 가이드](AZURE_DEPLOYMENT.md)

## 📧 문의

팀 내부 문서나 이슈 트래커를 참고해주세요.

---

**Happy Coding! 🚀**

# Docker 환경 설정 및 사용 가이드

## 📦 프로젝트 구성

이 프로젝트는 Docker를 사용하여 다음 서비스들을 컨테이너화합니다:

- **FastAPI 애플리케이션**: Python 백엔드 API
- **Elasticsearch**: 검색 엔진 및 데이터 저장소
- **Kibana**: Elasticsearch 데이터 시각화

## 🚀 빠른 시작

### 1. 사전 요구사항

- Docker Desktop 설치 및 실행
- Git

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd yakkobak_be
```

### 3. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (API 키 등 설정)
```

### 4. 실행

#### 개발 환경 (Hot Reload)

```bash
# 빌드 및 실행
docker-compose -f docker-compose.dev.yml up --build

# 백그라운드 실행
docker-compose -f docker-compose.dev.yml up -d

# 로그 확인
docker-compose -f docker-compose.dev.yml logs -f api
```

#### 프로덕션 환경

```bash
# 빌드 및 실행
docker-compose up --build -d

# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f
```

### 5. 접속

- **API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601

## 🔧 주요 명령어

### 컨테이너 관리

```bash
# 시작
docker-compose up -d

# 중지
docker-compose stop

# 재시작
docker-compose restart

# 삭제 (데이터 유지)
docker-compose down

# 삭제 (데이터 포함)
docker-compose down -v

# 특정 서비스만 재시작
docker-compose restart api
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs api

# 실시간 로그
docker-compose logs -f api

# 최근 100줄
docker-compose logs --tail=100 api
```

### 컨테이너 접속

```bash
# API 컨테이너 접속
docker-compose exec api bash

# Elasticsearch 컨테이너 접속
docker-compose exec elasticsearch bash

# Python 쉘 실행
docker-compose exec api python
```

### 데이터베이스 작업

```bash
# 색인 작업 실행
docker-compose exec api python scripts/setup_data.py --api-key YOUR_KEY --skip-collect

# FAQ 데이터 업데이트
docker-compose exec api python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv
```

## 📁 프로젝트 구조

```
yakkobak_be/
├── Dockerfile              # 프로덕션 이미지
├── Dockerfile.dev          # 개발 이미지
├── Dockerfile.elasticsearch # Elasticsearch (Nori 플러그인 포함)
├── docker-compose.yml      # 프로덕션 구성
├── docker-compose.dev.yml  # 개발 구성
├── .dockerignore          # Docker 빌드 제외 파일
├── app/                   # FastAPI 애플리케이션
├── data/                  # 데이터 파일
├── scripts/               # 유틸리티 스크립트
└── logs/                  # 로그 파일
```

## 🔄 개발 워크플로우

### 1. 로컬 개발

```bash
# 개발 환경 시작 (hot reload)
docker-compose -f docker-compose.dev.yml up

# 코드 수정 → 자동 재시작
# 브라우저에서 http://localhost:8000/docs 확인
```

### 2. 의존성 추가

```bash
# requirements.txt 수정 후
docker-compose -f docker-compose.dev.yml build api
docker-compose -f docker-compose.dev.yml up -d api
```

### 3. 테스트

```bash
# 컨테이너 내부에서 테스트 실행
docker-compose exec api pytest

# 특정 테스트 파일
docker-compose exec api pytest tests/test_api.py
```

## 🌐 다른 환경에 배포

### 1. 이미지 빌드 및 푸시

```bash
# Docker Hub에 로그인
docker login

# 이미지 빌드
docker build -t your-username/yakkobak-api:latest .

# 이미지 푸시
docker push your-username/yakkobak-api:latest
```

### 2. 다른 서버에서 실행

```bash
# 프로젝트 클론
git clone <repository-url>
cd yakkobak_be

# 환경 변수 설정
cp .env.example .env
# .env 편집

# Elasticsearch 볼륨 복원 (선택사항)
docker volume create health-supplement-rag_es_data
# 백업 데이터 복원...

# 실행
docker-compose up -d
```

## 📊 모니터링

### 컨테이너 상태

```bash
# 실행 중인 컨테이너
docker-compose ps

# 리소스 사용량
docker stats

# 헬스 체크
docker-compose exec api curl http://localhost:8000/api/v1/health
```

### Elasticsearch 상태

```bash
# 클러스터 상태
curl http://localhost:9200/_cluster/health?pretty

# 인덱스 확인
curl http://localhost:9200/_cat/indices?v

# 문서 개수
curl http://localhost:9200/health_supplements/_count
```

## 🐛 문제 해결

### 포트 충돌

```bash
# 다른 포트 사용
# docker-compose.yml에서 포트 변경
ports:
  - "8001:8000"  # 8000 대신 8001 사용
```

### 컨테이너 재빌드

```bash
# 캐시 없이 재빌드
docker-compose build --no-cache api

# 전체 재빌드
docker-compose build --no-cache
```

### 볼륨 초기화

```bash
# 주의: 모든 데이터 삭제됨
docker-compose down -v
docker volume rm health-supplement-rag_es_data
docker-compose up -d
```

### 로그 레벨 조정

```bash
# .env 파일에서
LOG_LEVEL=DEBUG

# 또는 docker-compose.yml에서
environment:
  - LOG_LEVEL=DEBUG
```

## 🔐 보안 고려사항

### 프로덕션 배포 시

1. **환경 변수 보호**
   - `.env` 파일을 Git에 커밋하지 않기
   - 민감한 정보는 Docker secrets 사용

2. **네트워크 격리**
   - 필요한 포트만 외부에 노출
   - 내부 통신은 Docker 네트워크 사용

3. **이미지 최적화**
   - Multi-stage build 사용
   - 불필요한 파일 제외 (.dockerignore)

4. **정기 업데이트**
   - 베이스 이미지 정기 업데이트
   - 의존성 보안 패치 적용

## 📚 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Elasticsearch Docker 가이드](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)

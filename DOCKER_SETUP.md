# Docker 설정 가이드

## 🐳 Docker Hub 이미지 사용

이 프로젝트는 사전에 색인된 Elasticsearch 데이터를 포함한 Docker 이미지를 사용합니다.

### Elasticsearch 이미지 정보
- **이미지명**: `albob1403/yakkobak-elasticsearch:latest`
- **포함 내용**:
  - Elasticsearch 8.11.0
  - Nori 한글 분석 플러그인
  - 사전 색인된 건강기능식품 데이터

## 🚀 실행 방법

### 1. Docker 이미지 다운로드 (선택사항)
Docker Compose가 자동으로 이미지를 다운로드하지만, 수동으로 미리 받을 수도 있습니다:

```bash
docker pull albob1403/yakkobak-elasticsearch:latest
```

### 2. 서비스 시작
```bash
# 모든 서비스 시작 (api, elasticsearch, kibana)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f elasticsearch
```

### 3. 서비스 상태 확인
```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# Elasticsearch 상태 확인
curl http://localhost:9200/_cluster/health

# API 헬스체크
curl http://localhost:8000/api/v1/health
```

### 4. 서비스 중지
```bash
# 서비스 중지 (데이터 보존)
docker-compose stop

# 서비스 중지 및 컨테이너 제거 (데이터 보존)
docker-compose down

# 서비스 중지 및 볼륨까지 삭제 (데이터 삭제)
docker-compose down -v
```

## 📊 접속 정보

서비스가 정상적으로 시작되면 다음 URL로 접속할 수 있습니다:

- **FastAPI 서버**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601

## 🔧 트러블슈팅

### Elasticsearch 컨테이너가 시작되지 않을 때
```bash
# 로그 확인
docker-compose logs elasticsearch

# 메모리 부족 시 docker-compose.yml에서 메모리 조정
# ES_JAVA_OPTS=-Xms512m -Xmx512m → ES_JAVA_OPTS=-Xms256m -Xmx256m
```

### 포트 충돌 시
다른 프로그램이 포트를 사용 중이면 `docker-compose.yml`에서 포트를 변경:
```yaml
ports:
  - "8001:8000"  # 8000 대신 8001 사용
```

### 이미지 업데이트
최신 이미지로 업데이트하려면:
```bash
docker-compose pull
docker-compose up -d
```

## 📦 볼륨 관리

Elasticsearch 데이터는 Docker 볼륨에 저장됩니다:

```bash
# 볼륨 목록 확인
docker volume ls

# 볼륨 상세 정보
docker volume inspect dev_es_data

# 볼륨 삭제 (주의: 모든 데이터 삭제됨)
docker volume rm dev_es_data
```

## 🔄 개발 모드

코드 수정 시 자동으로 반영됩니다 (볼륨 마운트 설정됨):
- `./app` → `/workspace/app`
- `./logs` → `/workspace/logs`

변경사항이 반영되지 않으면:
```bash
docker-compose restart api
```

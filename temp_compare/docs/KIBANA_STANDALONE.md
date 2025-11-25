# Kibana 단독 실행 가이드

이미 실행 중인 Elasticsearch에 Kibana만 추가로 실행하는 방법입니다.

## 방법 1: 자동 스크립트 사용 (권장)

### Windows
```bash
# 스크립트 실행
scripts\start_kibana_standalone.bat
```

### Linux/Mac
```bash
# 실행 권한 부여
chmod +x scripts/start_kibana_standalone.sh

# 스크립트 실행
./scripts/start_kibana_standalone.sh
```

스크립트가 자동으로:
1. Elasticsearch 연결 확인
2. 기존 Kibana 컨테이너 제거 (있는 경우)
3. 새로운 Kibana 컨테이너 실행

---

## 방법 2: Docker Compose 사용

```bash
# Kibana만 실행
docker-compose -f docker-compose.kibana-only.yml up -d

# 로그 확인
docker-compose -f docker-compose.kibana-only.yml logs -f

# 중지
docker-compose -f docker-compose.kibana-only.yml down
```

---

## 방법 3: 직접 Docker 명령어 사용

### Windows
```bash
docker run -d ^
  --name health-supplement-kibana ^
  -p 5601:5601 ^
  --add-host host.docker.internal:host-gateway ^
  -e ELASTICSEARCH_HOSTS=http://host.docker.internal:9200 ^
  -e SERVER_NAME=kibana ^
  -e SERVER_HOST=0.0.0.0 ^
  -e XPACK_SECURITY_ENABLED=false ^
  -e I18N_LOCALE=ko-KR ^
  docker.elastic.co/kibana/kibana:8.11.0
```

### Linux/Mac
```bash
docker run -d \
  --name health-supplement-kibana \
  -p 5601:5601 \
  --add-host host.docker.internal:host-gateway \
  -e ELASTICSEARCH_HOSTS=http://host.docker.internal:9200 \
  -e SERVER_NAME=kibana \
  -e SERVER_HOST=0.0.0.0 \
  -e XPACK_SECURITY_ENABLED=false \
  -e I18N_LOCALE=ko-KR \
  docker.elastic.co/kibana/kibana:8.11.0
```

---

## 접속 확인

### 1. Kibana 로그 확인
```bash
docker logs -f health-supplement-kibana
```

다음과 같은 메시지가 나오면 준비 완료:
```
[Kibana][http] http server running at http://0.0.0.0:5601
```

### 2. 브라우저에서 접속
- URL: http://localhost:5601
- 초기 로딩 시간: 약 1-2분

### 3. Elasticsearch 연결 확인
Kibana 접속 후 좌측 하단에 "Connected to Elasticsearch" 메시지 확인

---

## 관리 명령어

### Kibana 중지
```bash
docker stop health-supplement-kibana
```

### Kibana 재시작
```bash
docker start health-supplement-kibana
```

### Kibana 삭제
```bash
docker rm -f health-supplement-kibana
```

### Kibana 상태 확인
```bash
docker ps | grep kibana
```

### Kibana 로그 확인
```bash
# 실시간 로그
docker logs -f health-supplement-kibana

# 최근 100줄
docker logs --tail 100 health-supplement-kibana
```

---

## 문제 해결

### Kibana가 시작되지 않을 때

#### 1. Elasticsearch 연결 확인
```bash
# Elasticsearch가 실행 중인지 확인
curl http://localhost:9200

# 정상 응답 예시:
# {
#   "name" : "...",
#   "cluster_name" : "...",
#   "version" : { "number" : "8.11.0" }
# }
```

#### 2. Docker 네트워크 확인
```bash
# host.docker.internal이 정상 작동하는지 확인
docker exec health-supplement-kibana ping host.docker.internal
```

**Windows/Mac**: `host.docker.internal`이 자동으로 지원됩니다.

**Linux**: 다음과 같이 실행:
```bash
docker run -d \
  --name health-supplement-kibana \
  -p 5601:5601 \
  --network host \
  -e ELASTICSEARCH_HOSTS=http://localhost:9200 \
  -e SERVER_NAME=kibana \
  -e SERVER_HOST=0.0.0.0 \
  -e XPACK_SECURITY_ENABLED=false \
  -e I18N_LOCALE=ko-KR \
  docker.elastic.co/kibana/kibana:8.11.0
```

#### 3. 포트 충돌 확인
```bash
# 5601 포트가 이미 사용 중인지 확인
netstat -ano | findstr :5601  # Windows
lsof -i :5601                 # Linux/Mac
```

다른 포트를 사용하려면:
```bash
docker run -d \
  --name health-supplement-kibana \
  -p 5602:5601 \  # 5602로 변경
  ...
```

#### 4. Kibana 로그 확인
```bash
docker logs health-supplement-kibana
```

오류 메시지 확인 후 적절한 조치 수행

---

## 네트워크 구성

### 시나리오 1: Elasticsearch가 Docker 컨테이너로 실행 중
```bash
# Elasticsearch 네트워크 확인
docker network ls
docker inspect <elasticsearch-container-name> | grep NetworkMode

# Kibana를 같은 네트워크에 추가
docker run -d \
  --name health-supplement-kibana \
  --network <elasticsearch-network-name> \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  ...
```

### 시나리오 2: Elasticsearch가 호스트에서 직접 실행 중
```bash
# host.docker.internal 사용 (Windows/Mac)
-e ELASTICSEARCH_HOSTS=http://host.docker.internal:9200

# 또는 Linux에서 --network host 사용
docker run -d \
  --name health-supplement-kibana \
  --network host \
  -e ELASTICSEARCH_HOSTS=http://localhost:9200 \
  ...
```

---

## 대시보드 자동 설정

Kibana가 실행된 후:

```bash
# 인덱스 패턴 및 시각화 자동 생성
python scripts/setup_kibana_dashboard.py
```

자세한 내용은 [Kibana 가이드](KIBANA_GUIDE.md)를 참고하세요.

---

## 참고 사항

- Kibana는 Elasticsearch와 **같은 버전**을 사용하는 것이 권장됩니다
- 초기 시작 시 1-2분 정도 소요될 수 있습니다
- Elasticsearch가 중지되면 Kibana도 자동으로 연결이 끊어집니다
- 재시작 정책이 `unless-stopped`로 설정되어 있어 Docker 재시작 시 자동 실행됩니다

---

## 추가 도움말

문제가 계속되면:
1. [Kibana 공식 문서](https://www.elastic.co/guide/en/kibana/8.11/index.html) 참고
2. [프로젝트 이슈](../README.md)에 문의

# Elasticsearch Nori 플러그인 설치 가이드

## Docker를 사용한 설치 (권장)

### 1. 기존 Elasticsearch 컨테이너 중지 및 제거

```bash
# 실행 중인 Elasticsearch 컨테이너 확인
docker ps -a | findstr elastic

# 기존 컨테이너 중지 및 제거
docker stop <container_id>
docker rm <container_id>
```

### 2. Nori 플러그인이 포함된 Elasticsearch 실행

프로젝트 루트 디렉토리에서:

```bash
# Docker Compose로 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f elasticsearch
```

### 3. Nori 플러그인 설치 확인

```bash
# 플러그인 목록 확인
curl http://localhost:9200/_cat/plugins

# 출력 예시:
# health-supplement-node analysis-nori 8.11.0
```

### 4. Elasticsearch 상태 확인

```bash
# 클러스터 상태 확인
curl http://localhost:9200/_cluster/health

# 노드 정보 확인
curl http://localhost:9200
```

### 5. 컨테이너 관리 명령어

```bash
# 중지
docker-compose down

# 중지 + 볼륨 삭제 (데이터 초기화)
docker-compose down -v

# 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f elasticsearch
```

---

## 기존 Docker 컨테이너에 직접 설치

이미 Elasticsearch 컨테이너가 실행 중인 경우:

```bash
# 1. 컨테이너 접속
docker exec -it <container_name> bash

# 2. Nori 플러그인 설치
bin/elasticsearch-plugin install analysis-nori

# 3. 컨테이너 재시작 (필수!)
docker restart <container_name>

# 4. 플러그인 확인
curl http://localhost:9200/_cat/plugins
```

---

## Windows에서 로컬 Elasticsearch 설치 시

### 1. Elasticsearch 다운로드 및 압축 해제
- https://www.elastic.co/downloads/elasticsearch

### 2. Nori 플러그인 설치

PowerShell에서:

```powershell
cd C:\path\to\elasticsearch-8.11.0

# Nori 플러그인 설치
.\bin\elasticsearch-plugin.bat install analysis-nori

# 설치 확인
.\bin\elasticsearch-plugin.bat list
```

### 3. Elasticsearch 실행

```powershell
.\bin\elasticsearch.bat
```

### 4. 플러그인 확인

```powershell
curl http://localhost:9200/_cat/plugins
```

---

## Nori 분석기 테스트

### 1. 분석기 테스트

```bash
curl -X POST "http://localhost:9200/_analyze" -H "Content-Type: application/json" -d '{
  "tokenizer": "nori_tokenizer",
  "text": "건강기능식품 비타민을 먹습니다"
}'
```

### 2. 예상 출력

```json
{
  "tokens": [
    {"token": "건강", "start_offset": 0, "end_offset": 2},
    {"token": "기능", "start_offset": 2, "end_offset": 4},
    {"token": "식품", "start_offset": 4, "end_offset": 6},
    {"token": "비타민", "start_offset": 7, "end_offset": 10},
    {"token": "먹습니다", "start_offset": 12, "end_offset": 16}
  ]
}
```

---

## 프로젝트에서 인덱스 재생성

Nori 플러그인 설치 후:

```bash
# 가상환경 활성화
venv\Scripts\activate

# 인덱스 생성 (자동으로 Nori 사용)
python scripts/setup_data.py --api-key YOUR_API_KEY --skip-collect

# Nori 사용 확인 로그 출력:
# ✓ Nori 플러그인이 설치되어 있습니다.
```

---

## 문제 해결

### 플러그인이 설치되지 않는 경우

```bash
# 플러그인 수동 설치
docker exec -it health-supplement-es bash
bin/elasticsearch-plugin install analysis-nori --batch
exit

# 컨테이너 재시작
docker restart health-supplement-es
```

### 메모리 부족 오류

`docker-compose.yml`에서 메모리 조정:

```yaml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"  # 512m → 1g로 증가
```

### 포트 충돌

다른 프로세스가 9200 포트를 사용하는 경우:

```bash
# 포트 사용 확인
netstat -ano | findstr :9200

# 프로세스 종료 (관리자 권한 필요)
taskkill /PID <PID> /F
```

---

## 참고 자료

- [Elasticsearch Nori 분석기 공식 문서](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-nori.html)
- [Docker Elasticsearch 공식 이미지](https://www.docker.elastic.co/r/elasticsearch)

# 빠른 시작 가이드

> 건강기능식품 RAG 시스템 - 상황별 시작 가이드

## 📋 목차

1. [🆕 초기 프로젝트 구축](#-초기-프로젝트-구축) - 처음 설치할 때
2. [🔄 서버 재구동](#-서버-재구동) - 이미 설치된 환경
3. [🧪 테스트 및 확인](#-테스트-및-확인)
4. [❓ 자주 묻는 질문](#-자주-묻는-질문)

---

## 🆕 초기 프로젝트 구축

> **처음 프로젝트를 설치하고 구축할 때 따라하세요**

### 1단계: 사전 요구사항 확인

```bash
# Python 버전 확인 (3.9 이상 필요)
python --version

# Docker 설치 확인
docker --version
docker-compose --version

# Git 설치 확인
git --version
```

**필요한 것**:
- ✅ Python 3.9 이상
- ✅ Docker & Docker Compose
- ✅ Git
- ✅ 식품안전나라 API 키 ([발급 방법](https://www.foodsafetykorea.go.kr/api/))

### 2단계: 프로젝트 클론 및 가상환경 설정

```bash
# 1. 저장소 클론
git clone <repository-url>
cd health-supplement-rag

# 2. 가상환경 생성
python -m venv venv

# 3. 가상환경 활성화
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt
```

**확인**:
```bash
# 가상환경이 활성화되면 프롬프트 앞에 (venv) 표시됨
(venv) PS D:\health-supplement-rag>
```

### 3단계: 환경 변수 설정

```bash
# 1. .env 파일 생성
cp .env.example .env

# 2. .env 파일 편집 (메모장 또는 VS Code)
notepad .env  # Windows
# 또는
code .env     # VS Code
```

**필수 설정** (`.env` 파일):
```bash
# API 키 (필수)
FOOD_SAFETY_API_KEY=your_api_key_here

# Elasticsearch 설정
ES_HOST=localhost
ES_PORT=9200
ES_INDEX_NAME=health_supplements

# 보안 설정
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# 환경 설정
ENV=development
DEBUG=true
```

### 4단계: Elasticsearch & Kibana 시작

```bash
# Docker Compose로 시작
docker-compose up -d

# 상태 확인 (약 30초 대기 후)
docker-compose ps

# Elasticsearch 연결 확인
curl http://localhost:9200
```

**예상 출력**:
```json
{
  "name" : "elasticsearch",
  "cluster_name" : "docker-cluster",
  "version" : { ... }
}
```

### 4-1단계: Nori Analyzer 설치 (한국어 형태소 분석기)

> **중요**: Elasticsearch 컨테이너에 Nori 플러그인이 기본적으로 설치되어 있지 않습니다. 반드시 설치해야 합니다.

```bash
# 1. Elasticsearch 컨테이너에 접속
docker exec -it elasticsearch bash

# 2. Nori 플러그인 설치
bin/elasticsearch-plugin install analysis-nori

# 3. 설치 확인 (y 입력)
# -> Continue with installation? [y/N] y

# 4. 컨테이너 종료
exit

# 5. Elasticsearch 재시작 (플러그인 적용)
docker-compose restart elasticsearch

# 6. 재시작 대기 (약 30초)
timeout /t 30  # Windows
# sleep 30  # macOS/Linux

# 7. 플러그인 설치 확인
curl http://localhost:9200/_cat/plugins?v
```

**예상 출력**:
```
name          component      version
elasticsearch analysis-nori  8.x.x
```

**Windows PowerShell 한 줄 명령어**:
```powershell
docker exec -it elasticsearch bin/elasticsearch-plugin install analysis-nori; docker-compose restart elasticsearch; timeout /t 30
```

**macOS/Linux 한 줄 명령어**:
```bash
docker exec -it elasticsearch bin/elasticsearch-plugin install analysis-nori && docker-compose restart elasticsearch && sleep 30
```

> **참고**: Nori analyzer는 한국어 텍스트를 형태소 단위로 분석하여 검색 품질을 향상시킵니다. 이 단계를 건너뛰면 한국어 검색이 제대로 작동하지 않을 수 있습니다.


### 5단계: 초기 데이터 색인

```bash
# 전체 데이터 색인 (최초 1회, 약 10-20분 소요)
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index --max-items 5000

# 진행 상황 확인
# - 데이터 수집 중...
# - 임베딩 생성 중...
# - Elasticsearch 색인 중...
# - 완료!
```

**옵션 설명**:
- `--api-key`: 식품안전나라 API 키
- `--recreate-index`: 기존 인덱스 삭제 후 재생성
- `--max-items`: 색인할 최대 항목 수 (5000 권장)

### 6단계: FAQ 데이터 통합 (선택사항)

```bash
# FAQ 데이터를 Knowledge Base에 통합
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv

# 테스트
python scripts/test_faq_integration.py
```

### 7단계: 서버 시작

```bash
# FastAPI 서버 시작
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# 서버가 시작되면 다음 메시지 표시:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

### 8단계: 접속 확인

**브라우저에서 접속**:
- 🌐 **API 문서**: http://localhost:8000/docs
- 📊 **Kibana**: http://localhost:5601

**API 테스트**:
```bash
# 간단한 검색 테스트
curl -X POST "http://localhost:8000/api/search/hybrid" \
  -H "Content-Type: application/json" \
  -d '{"query": "비타민C", "top_k": 5}'
```

### ✅ 초기 구축 완료!

이제 시스템이 정상적으로 작동합니다. 다음부터는 [서버 재구동](#-서버-재구동) 섹션을 참고하세요.

---

## 🔄 서버 재구동

> **이미 설치된 환경에서 서버를 다시 시작할 때**

### 시나리오 1: 컴퓨터 재부팅 후

```bash
# 1. 프로젝트 디렉토리로 이동
cd d:\health-supplement-rag

# 2. 가상환경 활성화
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Docker 컨테이너 시작
docker-compose up -d

# 4. Elasticsearch 준비 대기 (약 30초)
timeout /t 30  # Windows
# sleep 30  # macOS/Linux

# 5. FastAPI 서버 시작
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

**한 번에 실행** (Windows):
```batch
cd d:\health-supplement-rag && venv\Scripts\activate && docker-compose up -d && timeout /t 30 && uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### 시나리오 2: 코드 수정 후 재시작

```bash
# 1. 서버 중지 (Ctrl+C)

# 2. 코드 수정 (VS Code 등)

# 3. 서버 재시작
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# 참고: --reload 옵션이 있으면 코드 변경 시 자동 재시작됨
```

### 시나리오 3: Docker 컨테이너만 재시작

```bash
# Elasticsearch & Kibana 재시작
docker-compose restart

# 또는 중지 후 재시작
docker-compose down
docker-compose up -d
```

### 시나리오 4: 전체 재시작 (문제 발생 시)

```bash
# 1. 모든 서비스 중지
# FastAPI 서버: Ctrl+C
docker-compose down

# 2. 가상환경 비활성화
deactivate

# 3. 다시 시작
cd d:\health-supplement-rag
venv\Scripts\activate
docker-compose up -d
timeout /t 30
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### 시나리오 5: 의존성 업데이트 후

```bash
# 1. 가상환경 활성화
venv\Scripts\activate

# 2. 의존성 재설치
pip install -r requirements.txt --upgrade

# 3. 서버 재시작
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### 빠른 재구동 체크리스트

- [ ] 프로젝트 디렉토리로 이동
- [ ] 가상환경 활성화 (`venv\Scripts\activate`)
- [ ] Docker 컨테이너 실행 (`docker-compose up -d`)
- [ ] Elasticsearch 준비 대기 (30초)
- [ ] FastAPI 서버 시작 (`uvicorn api.app:app --reload`)

---

## 🧪 테스트 및 확인

### 시스템 상태 확인

```bash
# 1. Elasticsearch 상태
curl http://localhost:9200

# 2. 인덱스 확인
curl http://localhost:9200/_cat/indices?v

# 3. 문서 개수 확인
curl http://localhost:9200/health_supplements/_count

# 4. Docker 컨테이너 상태
docker-compose ps
```

### API 테스트

```bash
# 1. 기본 검색
curl -X POST "http://localhost:8000/api/search/hybrid" \
  -H "Content-Type: application/json" \
  -d '{"query": "비타민C", "top_k": 5}'

# 2. 지능형 검색
curl -X POST "http://localhost:8000/api/search/intelligent" \
  -H "Content-Type: application/json" \
  -d '{"query": "눈이 피로해요", "top_k": 5}'

# 3. 복용시간 추천
curl -X POST "http://localhost:8000/api/recommend/timing" \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["철분", "칼슘"]}'
```

### 테스트 스크립트 실행

```bash
# FAQ 통합 테스트
python scripts/test_faq_integration.py

# 복용시간 API 테스트
python scripts/test_timing_api.py
```

---

## ❓ 자주 묻는 질문

### Q1: 가상환경이 활성화되지 않아요

**증상**: `venv\Scripts\activate` 실행 시 오류

**해결**:
```powershell
# PowerShell 실행 정책 변경 (관리자 권한)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 다시 시도
venv\Scripts\activate
```

### Q2: Docker 컨테이너가 시작되지 않아요

**확인**:
```bash
# Docker Desktop이 실행 중인지 확인
docker ps

# 포트 충돌 확인
netstat -ano | findstr :9200
netstat -ano | findstr :5601
```

**해결**:
```bash
# 기존 컨테이너 제거 후 재시작
docker-compose down -v
docker-compose up -d
```

### Q3: Elasticsearch 연결 실패

**증상**: `ConnectionError: ElasticSearch 연결 실패`

**해결**:
```bash
# 1. Elasticsearch 준비 대기 (30초)
timeout /t 30

# 2. 상태 확인
curl http://localhost:9200

# 3. 로그 확인
docker logs elasticsearch

# 4. 재시작
docker-compose restart elasticsearch
```

### Q4: API 키 오류

**증상**: `API 요청 실패: 401 Unauthorized`

**해결**:
```bash
# 1. .env 파일 확인
cat .env | grep FOOD_SAFETY_API_KEY

# 2. API 키 재설정
notepad .env

# 3. 서버 재시작 (환경변수 다시 로드)
# Ctrl+C로 중지 후
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### Q5: 포트가 이미 사용 중이에요

**증상**: `Address already in use: 8000`

**해결**:
```bash
# Windows: 포트 사용 프로세스 확인
netstat -ano | findstr :8000

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F

# 또는 다른 포트 사용
uvicorn api.app:app --reload --host 0.0.0.0 --port 8001
```

### Q6: 한글이 깨져요 (Windows)

**해결**:
```cmd
# 인코딩 변경
chcp 65001

# 또는 자동 스크립트
scripts\fix_encoding.bat
```

### Q7: 데이터가 색인되지 않아요

**확인**:
```bash
# 1. 인덱스 존재 확인
curl http://localhost:9200/_cat/indices?v

# 2. 문서 개수 확인
curl http://localhost:9200/health_supplements/_count

# 3. 로그 확인
# 서버 실행 중 로그 메시지 확인
```

**해결**:
```bash
# 재색인
python scripts/setup_data.py --api-key YOUR_KEY --recreate-index --max-items 1000
```

### Q8: Kibana에 데이터가 안 보여요

**해결**:
```bash
# 1. Kibana 접속
http://localhost:5601

# 2. Index Pattern 생성
# Management > Stack Management > Index Patterns > Create
# Index pattern name: health_supplements*
# Time field: report_date

# 3. 시간 범위 조정
# 대시보드 우측 상단 > Last 7 days 또는 Last 30 days
```

### Q9: Nori analyzer가 설치되지 않았어요

**증상**: 
- 한국어 검색이 제대로 작동하지 않음
- 플러그인 목록에 `analysis-nori`가 없음

**확인**:
```bash
# 플러그인 목록 확인
curl http://localhost:9200/_cat/plugins?v

# 또는
docker exec -it elasticsearch bin/elasticsearch-plugin list
```

**해결**:
```bash
# 1. Elasticsearch 컨테이너에 접속
docker exec -it elasticsearch bash

# 2. Nori 플러그인 설치
bin/elasticsearch-plugin install analysis-nori

# 3. y 입력하여 설치 진행
# -> Continue with installation? [y/N] y

# 4. 컨테이너 종료
exit

# 5. Elasticsearch 재시작
docker-compose restart elasticsearch

# 6. 대기 (30초)
timeout /t 30  # Windows
# sleep 30  # macOS/Linux

# 7. 설치 확인
curl http://localhost:9200/_cat/plugins?v
```

**자동 설치 (한 줄)**:
```bash
# Windows PowerShell
docker exec -it elasticsearch bin/elasticsearch-plugin install analysis-nori; docker-compose restart elasticsearch; timeout /t 30

# macOS/Linux
docker exec -it elasticsearch bin/elasticsearch-plugin install analysis-nori && docker-compose restart elasticsearch && sleep 30
```

> **참고**: Nori analyzer 설치 후에는 반드시 Elasticsearch를 재시작해야 플러그인이 적용됩니다.

---

## � 추가 리소스

### 문서

- **[README.md](README.md)** - 프로젝트 개요
- **[docs/README.md](docs/README.md)** - 상세 문서
- **[.env.example](.env.example)** - 환경변수 템플릿

### 스크립트

```bash
# 정기 업데이트
python scripts/incremental_index.py --api-key YOUR_KEY

# FAQ 업데이트
python scripts/update_knowledge_base.py --csv-path data/faq_dataset_300.csv

# 중복 제거
python scripts/remove_duplicates.py
```

### 유용한 명령어

```bash
# 로그 실시간 확인
docker logs -f elasticsearch
docker logs -f kibana

# 컨테이너 리소스 사용량
docker stats

# 디스크 정리
docker system prune -a
```

---

## 🎯 다음 단계

### 초기 구축 완료 후

1. ✅ [API 문서](http://localhost:8000/docs)에서 API 테스트
2. ✅ [Kibana](http://localhost:5601)에서 대시보드 생성
3. ✅ 정기 업데이트 스케줄 설정 (주 1회)
4. ✅ 백업 계획 수립

### 개발 시작

1. ✅ [docs/README.md](docs/README.md) 읽기
2. ✅ API 엔드포인트 테스트
3. ✅ 코드 수정 및 테스트
4. ✅ 로그 모니터링

---

**🎉 준비 완료! 이제 시스템을 사용할 수 있습니다.**

문제가 발생하면 [트러블슈팅](#-자주-묻는-질문) 섹션을 참고하세요.

# 데이터 색인 절차 가이드

> 최종 업데이트: 2025-11-26 | 데이터 소스: 식약처 C003 API

## 📋 색인 절차 개요

### 현재 색인 프로세스

```
1단계: C003 API 데이터 수집 (건강기능식품 품목제조신고)
   ↓
2단계: 데이터 전처리 및 문서 생성
   ↓
3단계: ElasticSearch 인덱스 생성/확인
   ↓
4단계: 벡터 임베딩 생성 (ko-sroberta-multitask)
   ↓
5단계: Bulk 색인 실행
   ↓
6단계: 인덱스 통계 확인
```

---

## 🔄 증분 색인 (Incremental Indexing)

### 문제점
- 기존 방식: 전체 데이터를 매번 재색인 → 중복 발생
- 시간 소요: 대량 데이터 처리 시 오래 걸림

### 해결책
- **증분 색인**: 이미 색인된 데이터 제외
- **중복 체크**: 제품 ID 기반 중복 확인
- **업데이트 모드**: 신규 데이터만 추가

---

## 📝 색인 절차 상세

### 1단계: 데이터 수집

#### 기본 수집
```bash
# 전체 데이터 수집
python scripts/setup_data.py --api-key YOUR_API_KEY

# 제한된 개수 수집 (테스트용)
python scripts/setup_data.py --api-key YOUR_API_KEY --max-items 1000
```


### 2단계: 데이터 전처리

자동으로 수행됩니다:
- C003 API 데이터 파싱
- 제품 고유 ID 생성 (`{PRDLST_REPORT_NO}_{BSSH_NM}`)
- 임베딩 텍스트 생성 (제품명, 회사명, 형태, 기능, 원재료 등)
- Kibana 최적화 필드 추가 (indexed_at, stats, ingredient_count)
- 필드 정규화 및 검증

### 3단계: 인덱스 생성

#### 신규 생성
```bash
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index
```

#### 기존 인덱스 사용
```bash
python scripts/setup_data.py --api-key YOUR_API_KEY
```

### 4단계: 문서 색인

#### 전체 색인 (기존 방식)
```bash
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index
```

#### 증분 색인 (신규 - 중복 제외)
```bash
python scripts/incremental_index.py --api-key YOUR_API_KEY
```

### 5단계: 통계 확인

자동으로 출력됩니다:
- 인덱스명
- 문서 개수
- 인덱스 크기

---

## 🆕 증분 색인 사용법

### 기본 사용

```bash
# 신규 데이터만 색인
python scripts/incremental_index.py --api-key YOUR_API_KEY

# 저장된 파일에서 증분 색인
python scripts/incremental_index.py --skip-collect --data-file data/raw/new_data.json

# 최대 개수 제한
python scripts/incremental_index.py --api-key YOUR_API_KEY --max-items 500
```

### 옵션

| 옵션 | 설명 | 예시 |
|-----|------|------|
| `--api-key` | 식약처 API 키 | `--api-key YOUR_KEY` |
| `--skip-collect` | 데이터 수집 건너뛰기 | `--skip-collect` |
| `--data-file` | 데이터 파일 경로 | `--data-file data/new.json` |
| `--max-items` | 최대 수집 개수 | `--max-items 1000` |
| `--batch-size` | 색인 배치 크기 | `--batch-size 100` |
| `--dry-run` | 실제 색인 없이 테스트 | `--dry-run` |

---

## 🔍 중복 체크 로직

### 제품 ID 생성

```python
# 제품 고유 ID
product_id = f"{PRDLST_REPORT_NO}_{BSSH_NM}"

# 예시
"201900001_종근당건강"
```

### 중복 확인 프로세스

```
1. ElasticSearch에서 기존 제품 ID 목록 조회
   ↓
2. 신규 데이터와 비교
   ↓
3. 중복되지 않은 데이터만 필터링
   ↓
4. 필터링된 데이터만 색인
```

---

## 📊 색인 시나리오

### 시나리오 1: 초기 색인 (최초 설정)

```bash
# 전체 데이터 수집 및 색인 (인덱스 재생성)
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index

# 테스트용 (5000개 제한)
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index --max-items 5000

# 특정 범위만 색인
python scripts/setup_data.py --api-key YOUR_API_KEY --start-index 1 --end-index 10000

# 결과
# ✓ 인덱스 생성: health_supplements
# ✓ C003 데이터 수집 완료
# ✓ 벡터 임베딩 생성 완료
# ✓ 색인 완료: 5000개 문서
```

### 시나리오 2: 증분 색인 (정기 업데이트)

```bash
# 신규 데이터만 자동으로 색인 (중복 제외)
python scripts/incremental_index.py --api-key YOUR_API_KEY

# 1000개 제한
python scripts/incremental_index.py --api-key YOUR_API_KEY --max-items 1000

# 테스트 모드 (실제 색인 안 함)
python scripts/incremental_index.py --api-key YOUR_API_KEY --max-items 100 --dry-run

# 결과
# [3단계] 기존 제품 ID 조회
# ✓ 기존 제품 ID 4950개 조회 완료
#
# [4단계] 신규 문서 필터링
# ✓ 필터링 완료
#   - 전체 문서: 1000개
#   - 중복 문서: 950개
#   - 신규 문서: 50개
#
# [5단계] 신규 문서 벡터화 및 색인
# ✓ 색인 완료
#
# 인덱스 통계:
#   - 문서 개수: 5,000개
#   - 신규 추가: 50개
```

### 시나리오 3: 저장된 파일로 증분 색인

```bash
# 이미 수집한 데이터가 있는 경우
python scripts/incremental_index.py --skip-collect --data-file data/raw/new_products.json

# 결과
# [1-2단계] 저장된 데이터 로드
# ✓ 데이터 로드 완료 - 1000개 문서
# [3단계] 기존 ID 조회 및 중복 제외
# [5단계] 신규 데이터만 색인
```

### 시나리오 4: 인덱스 관리

```bash
# 인덱스 통계 확인
python scripts/update_index.py stats

# 인덱스 재생성 (데이터 유지)
python scripts/update_index.py recreate

# 기존 파일로 재색인
python scripts/update_index.py reindex --data-file data/raw/health_supplements_data.json

# 인덱스 삭제
python scripts/update_index.py delete
```

### 시나리오 5: 전체 재색인 (스키마 변경 시)

```bash
# 스키마 변경 등으로 전체 재색인 필요 시
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index

# 결과
# ✓ 기존 인덱스 삭제
# ✓ 새 인덱스 생성 (새 스키마 적용)
# ✓ 전체 데이터 재색인
```

---

## ⚠️ 주의사항 및 권장사항

### 1. API 키 관리
```bash
# 방법 1: 환경 변수 사용 (권장)
export FOOD_SAFETY_API_KEY="your_api_key"
python scripts/incremental_index.py

# 방법 2: .env 파일 사용
# .env 파일에 추가
FOOD_SAFETY_API_KEY=your_api_key

# 방법 3: 직접 전달
python scripts/incremental_index.py --api-key YOUR_API_KEY
```

### 2. 데이터 백업
```bash
# Windows
xcopy /E /I data\raw data\backup_%date:~0,4%%date:~5,2%%date:~8,2%

# Linux/Mac
cp -r data/raw data/backup_$(date +%Y%m%d)

# 중요: 재색인 전 반드시 백업!
```

### 3. 인덱스 스냅샷 (ElasticSearch)
```bash
# 스냅샷 저장소 등록 (최초 1회)
curl -X PUT "localhost:9200/_snapshot/my_backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/backup"
  }
}
'

# 스냅샷 생성
curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_$(date +%Y%m%d)?wait_for_completion=true"

# 스냅샷 복원
curl -X POST "localhost:9200/_snapshot/my_backup/snapshot_20251126/_restore"
```

### 4. 색인 성능 최적화
- **배치 크기**: 100-500 (기본 100)
  - 소량 데이터: `--batch-size 100`
  - 대량 데이터: `--batch-size 500`
  - 메모리 부족 시: `--batch-size 50`

- **API 요청 제한**
  ```python
  # app/core/config.py
  API_BATCH_SIZE = 1000      # API 한 번에 가져올 개수
  API_REQUEST_DELAY = 0.5    # API 요청 간 대기 시간(초)
  ```

- **임베딩 배치 크기**: 32 (고정, elasticsearch_manager.py)

- **ElasticSearch 힙 메모리**
  ```yaml
  # docker-compose.yml
  environment:
    - "ES_JAVA_OPTS=-Xms2g -Xmx2g"  # 최소 2GB 권장
  ```

---

## 🔧 트러블슈팅

### 문제 1: 색인 속도 느림
```bash
# 해결: 배치 크기 증가
python scripts/incremental_index.py --batch-size 500
```

### 문제 2: 메모리 부족
```bash
# 해결: 작은 배치로 나눠서 색인
python scripts/incremental_index.py --max-items 1000 --batch-size 50
```

### 문제 3: API 요청 제한 (429 Too Many Requests)
```python
# app/core/config.py 수정
API_REQUEST_DELAY = 1.0    # 0.5 → 1.0초로 증가
API_BATCH_SIZE = 500       # 1000 → 500으로 감소
```

---

## 📈 모니터링

### 색인 진행 상황 확인

```bash
# 실시간 로그 확인
tail -f logs/app.log

# 인덱스 통계
curl -X GET "localhost:9200/health_supplements/_stats?pretty"

# 문서 개수
curl -X GET "localhost:9200/health_supplements/_count?pretty"
```

### 색인 품질 확인

```bash
# 샘플 문서 조회
curl -X GET "localhost:9200/health_supplements/_search?size=5&pretty"

# 특정 필드 존재 여부
curl -X GET "localhost:9200/health_supplements/_search?q=_exists_:embedding_vector&pretty"
```

---

## 💡 Best Practices

1. **정기적인 증분 색인**: 주 1회 신규 데이터 추가
2. **백업**: 색인 전 항상 백업
3. **모니터링**: 색인 후 통계 확인
4. **테스트**: `--dry-run`으로 먼저 테스트
5. **로그 확인**: 오류 발생 시 로그 분석

---

## 🚀 빠른 시작

### 초기 설정 (최초 1회)

```bash
# 1. 환경 변수 설정 (.env 파일)
FOOD_SAFETY_API_KEY=your_api_key
ES_HOST=localhost
ES_PORT=9200
ES_INDEX_NAME=health_supplements

# 2. ElasticSearch 및 Kibana 시작
docker-compose up -d elasticsearch kibana

# 3. 연결 확인 (30초 대기 후)
curl http://localhost:9200

# 4. 전체 데이터 색인 (테스트: 5000개)
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index --max-items 5000

# 5. 인덱스 통계 확인
python scripts/update_index.py stats
```

### 정기 업데이트 (주 1회 권장)

```bash
# 신규 데이터만 자동 추가 (중복 자동 제외)
python scripts/incremental_index.py --api-key YOUR_API_KEY

# 제한된 개수로 테스트
python scripts/incremental_index.py --api-key YOUR_API_KEY --max-items 1000 --dry-run
```

### 재색인 작업 체크리스트

#### ✅ 재색인 전 체크리스트

- [ ] **백업 완료**: 데이터 파일 백업 확인
- [ ] **인덱스 통계 확인**: 현재 문서 개수 기록
- [ ] **API 키 확인**: 환경 변수 또는 .env 파일 설정
- [ ] **ElasticSearch 상태**: `curl http://localhost:9200` 응답 확인
- [ ] **디스크 공간**: 충분한 저장 공간 확보 (최소 5GB)
- [ ] **작업 시간**: 사용자 접근이 적은 시간대 선택

#### 🔄 재색인 실행

```bash
# 1. 백업 (중요!)
xcopy /E /I data\raw data\backup_%date:~0,4%%date:~5,2%%date:~8,2%

# 2. 현재 인덱스 통계 확인 및 기록
python scripts/update_index.py stats

# 3. 전체 재색인 실행
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index

# 4. 재색인 후 확인
python scripts/update_index.py stats
curl http://localhost:9200/health_supplements/_count

# 5. 샘플 데이터 확인
curl http://localhost:9200/health_supplements/_search?size=3&pretty
```

#### ✅ 재색인 후 검증

- [ ] **문서 개수**: 이전과 비슷한 개수인지 확인
- [ ] **벡터 필드**: `embedding_vector` 필드 존재 확인
- [ ] **검색 테스트**: API 검색 기능 정상 작동 확인
- [ ] **Kibana 확인**: 대시보드에서 데이터 표시 확인
- [ ] **로그 확인**: `logs/app.log`에서 에러 없는지 확인

```bash
# 검색 테스트
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "비타민", "top_k": 5}'

# 벡터 필드 확인
curl "http://localhost:9200/health_supplements/_search?q=_exists_:embedding_vector&size=0"
```

---

## 📝 재색인이 필요한 경우

다음 상황에서 전체 재색인이 필요합니다:

1. **스키마 변경**
   - 인덱스 매핑 수정
   - 새로운 필드 추가
   - 분석기(Analyzer) 변경

2. **임베딩 모델 변경**
   - 벡터 차원 변경
   - 다른 임베딩 모델 사용

3. **데이터 품질 개선**
   - 전처리 로직 개선
   - 데이터 정규화 규칙 변경

4. **대량 중복 데이터 발견**
   - 증분 색인으로 해결 안 되는 경우

5. **ElasticSearch 업그레이드**
   - 메이저 버전 업그레이드 시

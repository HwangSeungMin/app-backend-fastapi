# 데이터 색인 절차 가이드

## 📋 색인 절차 개요

### 현재 색인 프로세스

```
1단계: 데이터 수집
   ↓
2단계: 데이터 전처리
   ↓
3단계: ElasticSearch 인덱스 생성
   ↓
4단계: 문서 벡터화 및 색인
   ↓
5단계: 인덱스 통계 확인
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

#### 추가 API 데이터 수집
```bash
# 기능성 원료, 영업신고, 부작용 정보
python scripts/collect_additional_data.py --max-items 100
```

### 2단계: 데이터 전처리

자동으로 수행됩니다:
- 제품 정보 + 분류 정보 병합
- 임베딩 텍스트 생성
- 필드 정규화

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

### 시나리오 1: 초기 색인

```bash
# 1. 인덱스 생성 및 전체 데이터 색인
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index --max-items 5000

# 결과
# - 인덱스 생성: health_supplements
# - 색인된 문서: 5000개
```

### 시나리오 2: 신규 데이터 추가

```bash
# 2. 1개월 후 신규 데이터 추가
python scripts/incremental_index.py --api-key YOUR_API_KEY --max-items 1000

# 결과
# - 수집된 데이터: 1000개
# - 기존 데이터와 중복: 950개
# - 신규 데이터 색인: 50개
# - 총 문서 수: 5050개
```

### 시나리오 3: 추가 API 데이터 통합

```bash
# 3. 추가 API 데이터 수집
python scripts/collect_additional_data.py --max-items 100

# 4. 추가 데이터를 기존 인덱스에 병합
python scripts/merge_additional_data.py

# 결과
# - 기능성 원료 정보 추가
# - 영업신고 정보 추가
# - 부작용 정보 추가
```

### 시나리오 4: 전체 재색인

```bash
# 4. 스키마 변경 등으로 전체 재색인 필요 시
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index

# 결과
# - 기존 인덱스 삭제
# - 새 인덱스 생성
# - 전체 데이터 재색인
```

---

## ⚠️ 주의사항

### 1. API 키 관리
```bash
# 환경 변수 사용 권장
export FOOD_SAFETY_API_KEY="your_api_key"
python scripts/incremental_index.py
```

### 2. 데이터 백업
```bash
# 색인 전 데이터 백업
cp -r data/raw data/backup_$(date +%Y%m%d)
```

### 3. 인덱스 스냅샷
```bash
# ElasticSearch 스냅샷 생성
curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_1?wait_for_completion=true"
```

### 4. 색인 성능
- 배치 크기: 100-500 (기본 100)
- 대량 데이터: 배치 크기 증가 권장
- 메모리: 충분한 힙 메모리 확보

---

## 🔧 트러블슈팅

### 문제 1: 중복 데이터 발견
```bash
# 해결: 중복 제거 스크립트 실행
python scripts/remove_duplicates.py
```

### 문제 2: 색인 속도 느림
```bash
# 해결: 배치 크기 증가
python scripts/incremental_index.py --batch-size 500
```

### 문제 3: 메모리 부족
```bash
# 해결: 작은 배치로 나눠서 색인
python scripts/incremental_index.py --max-items 1000 --batch-size 50
```

### 문제 4: API 요청 제한
```bash
# 해결: 요청 간격 증가 (settings.py)
API_REQUEST_DELAY = 1.0  # 1초
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
# 1. 전체 데이터 색인
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index --max-items 5000
```

### 정기 업데이트 (주기적)
```bash
# 2. 신규 데이터만 추가
python scripts/incremental_index.py --api-key YOUR_API_KEY --max-items 1000
```

### 추가 데이터 통합 (선택)
```bash
# 3. 추가 API 데이터 수집 및 병합
python scripts/collect_additional_data.py --max-items 100
python scripts/merge_additional_data.py
```

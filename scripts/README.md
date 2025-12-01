# 데이터 색인 스크립트 사용 가이드

## 📚 스크립트 목록

### 1. 초기 색인 (setup_data.py)
전체 데이터를 처음부터 색인합니다.

```bash
# 기본 사용
python scripts/setup_data.py --api-key YOUR_API_KEY

# 인덱스 재생성
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index

# 제한된 개수 (테스트용)
python scripts/setup_data.py --api-key YOUR_API_KEY --max-items 1000
```

### 2. 증분 색인 (incremental_index.py) ⭐ 신규
**이미 색인된 데이터를 제외하고 신규 데이터만 색인합니다.**

```bash
# 기본 사용 (중복 자동 제외)
python scripts/incremental_index.py --api-key YOUR_API_KEY

# Dry-run (테스트만, 실제 색인 안 함)
python scripts/incremental_index.py --api-key YOUR_API_KEY --dry-run

# 추가 API 데이터 포함
python scripts/incremental_index.py --api-key YOUR_API_KEY --include-additional

# 배치 크기 조정
python scripts/incremental_index.py --api-key YOUR_API_KEY --batch-size 500
```

### 3. 중복 제거 (remove_duplicates.py) ⭐ 신규
인덱스에서 중복된 문서를 찾아 제거합니다.

```bash
# 중복 확인 (삭제 안 함)
python scripts/remove_duplicates.py --dry-run

# 중복 샘플 표시
python scripts/remove_duplicates.py --dry-run --show-samples

# 실제 중복 제거
python scripts/remove_duplicates.py
```

### 4. 추가 데이터 수집 (collect_additional_data.py)
식약처 추가 API 데이터를 수집합니다.

```bash
# 기본 사용
python scripts/collect_additional_data.py --max-items 100
```

---

## 🔄 색인 워크플로우

### 시나리오 1: 최초 설정

```bash
# 1. 전체 데이터 색인 (처음 1회)
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index --max-items 5000

# 결과: 5000개 문서 색인
```

### 시나리오 2: 정기 업데이트 (권장)

```bash
# 2. 신규 데이터만 추가 (주기적)
python scripts/incremental_index.py --api-key YOUR_API_KEY --max-items 1000

# 결과:
# - 수집: 1000개
# - 중복: 950개 (자동 제외)
# - 신규 색인: 50개
```

### 시나리오 3: 중복 발견 시

```bash
# 3. 중복 확인
python scripts/remove_duplicates.py --dry-run --show-samples

# 4. 중복 제거
python scripts/remove_duplicates.py

# 결과: 중복 문서 삭제
```

### 시나리오 4: 추가 데이터 통합

```bash
# 5. 추가 API 데이터 수집
python scripts/collect_additional_data.py --max-items 100

# 6. 증분 색인 (추가 데이터 포함)
python scripts/incremental_index.py --api-key YOUR_API_KEY --include-additional
```

---

## 📋 옵션 설명

### 공통 옵션

| 옵션 | 설명 | 예시 |
|-----|------|------|
| `--api-key` | 식약처 API 키 | `--api-key YOUR_KEY` |
| `--max-items` | 최대 수집 개수 | `--max-items 1000` |
| `--dry-run` | 테스트만 (실제 실행 안 함) | `--dry-run` |

### setup_data.py

| 옵션 | 설명 |
|-----|------|
| `--recreate-index` | 기존 인덱스 삭제 후 재생성 |
| `--skip-collect` | 데이터 수집 건너뛰기 |
| `--data-file` | 데이터 파일 경로 |

### incremental_index.py

| 옵션 | 설명 |
|-----|------|
| `--batch-size` | 색인 배치 크기 (기본: 100) |
| `--include-additional` | 추가 API 데이터 포함 |
| `--skip-collect` | 데이터 수집 건너뛰기 |

### remove_duplicates.py

| 옵션 | 설명 |
|-----|------|
| `--show-samples` | 중복 샘플 표시 |

---

## ⚠️ 주의사항

### 1. API 키 관리

```bash
# 환경 변수 사용 권장
export FOOD_SAFETY_API_KEY="your_api_key"
python scripts/incremental_index.py
```

### 2. 백업

```bash
# 색인 전 데이터 백업
cp -r data/raw data/backup_$(date +%Y%m%d)
```

### 3. Dry-run 먼저 실행

```bash
# 항상 dry-run으로 먼저 테스트
python scripts/incremental_index.py --api-key YOUR_API_KEY --dry-run
```

---

## 💡 Best Practices

1. **정기적인 증분 색인**: 주 1회 신규 데이터 추가
2. **Dry-run 활용**: 실제 색인 전 항상 테스트
3. **중복 체크**: 월 1회 중복 확인 및 제거
4. **로그 확인**: 색인 후 로그 분석
5. **통계 모니터링**: 문서 개수 추이 확인

---

## 🔍 트러블슈팅

### 문제: 중복 데이터 발견
```bash
python scripts/remove_duplicates.py
```

### 문제: 색인 속도 느림
```bash
python scripts/incremental_index.py --batch-size 500
```

### 문제: API 요청 제한
```python
# config/settings.py
API_REQUEST_DELAY = 1.0  # 1초로 증가
```

---

## 📊 모니터링

### 인덱스 통계 확인

```bash
# 문서 개수
curl -X GET "localhost:9200/health_supplements/_count?pretty"

# 인덱스 상태
curl -X GET "localhost:9200/health_supplements/_stats?pretty"
```

### 로그 확인

```bash
# 실시간 로그
tail -f logs/app.log

# 오류 로그만
grep ERROR logs/app.log
```

---

## 🚀 빠른 시작

### 초기 설정 (최초 1회)
```bash
python scripts/setup_data.py --api-key YOUR_API_KEY --recreate-index --max-items 5000
```

### 정기 업데이트 (주기적)
```bash
python scripts/incremental_index.py --api-key YOUR_API_KEY --max-items 1000
```

### 중복 정리 (필요시)
```bash
python scripts/remove_duplicates.py
```

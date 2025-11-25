# Kibana 대시보드를 위한 Elasticsearch 인덱스 최적화 가이드

## 📊 개요

Kibana 대시보드에서 효과적인 시각화와 분석을 위해서는 Elasticsearch 인덱스 설정을 최적화해야 합니다.

---

## 🎯 주요 최적화 포인트

### 1. 필드 타입 최적화

#### Keyword vs Text
- **Keyword**: 집계(aggregation), 필터링, 정렬에 사용
- **Text**: 전문 검색(full-text search)에 사용

#### 권장 설정
```json
{
  "company_name": {
    "type": "text",
    "fields": {
      "keyword": {"type": "keyword"}  // 집계용
    }
  }
}
```

### 2. 날짜 필드 추가

Kibana 시계열 분석을 위해 필수:

```json
{
  "report_date": {
    "type": "date",
    "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis"
  },
  "indexed_at": {
    "type": "date"  // 색인 시간
  },
  "updated_at": {
    "type": "date"  // 업데이트 시간
  }
}
```

### 3. 집계 최적화 필드

통계 및 집계를 위한 필드:

```json
{
  "classification.category": {
    "type": "keyword"  // 카테고리별 집계
  },
  "company_name.keyword": {
    "type": "keyword"  // 제조사별 집계
  },
  "price_range": {
    "type": "keyword"  // 가격대별 집계
  },
  "popularity_score": {
    "type": "integer"  // 인기도 점수
  }
}
```

### 4. 지리 정보 (선택)

제조사 위치 분석:

```json
{
  "location": {
    "type": "geo_point"  // 지도 시각화
  }
}
```

---

## 🔧 최적화된 인덱스 설정

### 개선된 Mapping

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "refresh_interval": "1s",  // Kibana 실시간 업데이트
    "analysis": {
      // ... (기존 분석기 설정)
    }
  },
  "mappings": {
    "properties": {
      // === 기본 정보 ===
      "product_id": {
        "type": "keyword"
      },
      "product_name": {
        "type": "text",
        "fields": {
          "keyword": {"type": "keyword"},  // 집계용
          "ngram": {"type": "text"}
        }
      },
      "company_name": {
        "type": "text",
        "fields": {
          "keyword": {"type": "keyword"}  // 제조사별 집계
        }
      },
      
      // === 날짜 필드 (Kibana 시계열) ===
      "report_date": {
        "type": "date",
        "format": "yyyyMMdd||yyyy-MM-dd"
      },
      "indexed_at": {
        "type": "date"  // 색인 시간 (자동 추가)
      },
      "updated_at": {
        "type": "date"  // 업데이트 시간
      },
      
      // === 분류 정보 (집계용) ===
      "classification": {
        "properties": {
          "category": {
            "type": "keyword"  // 카테고리별 집계
          },
          "detail_category": {
            "type": "keyword"  // 상세 카테고리별 집계
          },
          "function_content": {
            "type": "text",
            "fields": {
              "keyword": {"type": "keyword"}
            }
          }
        }
      },
      
      // === 통계 필드 ===
      "stats": {
        "properties": {
          "view_count": {
            "type": "integer"  // 조회수
          },
          "search_count": {
            "type": "integer"  // 검색 횟수
          },
          "popularity_score": {
            "type": "float"  // 인기도 점수
          }
        }
      },
      
      // === 가격 정보 (선택) ===
      "price_range": {
        "type": "keyword"  // "저가", "중가", "고가"
      },
      
      // === 원재료 분석 ===
      "raw_materials": {
        "type": "text",
        "fields": {
          "keyword": {"type": "keyword"}
        }
      },
      "ingredient_count": {
        "type": "integer"  // 성분 개수
      },
      
      // === 검색 최적화 ===
      "embedding_vector": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      },
      "embedding_text": {
        "type": "text"
      },
      
      // === 메타데이터 ===
      "metadata": {
        "properties": {
          "source": {
            "type": "keyword"  // 데이터 출처
          },
          "version": {
            "type": "keyword"  // 데이터 버전
          }
        }
      }
    }
  }
}
```

---

## 📈 Kibana 대시보드 활용 예시

### 1. 시계열 분석

**신고일자별 제품 추이**
```
Visualization: Line Chart
X-axis: report_date (Date Histogram)
Y-axis: Count
```

**월별 신규 제품 수**
```
Visualization: Bar Chart
X-axis: report_date (Monthly)
Y-axis: Count
```

### 2. 카테고리 분석

**카테고리별 제품 분포**
```
Visualization: Pie Chart
Slice: classification.category (Terms)
Size: Count
```

**제조사별 제품 수**
```
Visualization: Data Table
Rows: company_name.keyword (Terms)
Metrics: Count
```

### 3. 트렌드 분석

**인기 원재료 Top 10**
```
Visualization: Tag Cloud
Tags: raw_materials.keyword (Terms, Top 10)
Size: Count
```

**검색 빈도 높은 제품**
```
Visualization: Metric
Metric: stats.search_count (Sum)
Filter: Last 30 days
```

### 4. 지리 분석 (선택)

**제조사 위치 분포**
```
Visualization: Maps
Geo Field: location
Metrics: Count
```

---

## 🔄 인덱스 설정 변경 방법

### 방법 1: 새 인덱스 생성 (권장)

```bash
# 1. 최적화된 설정으로 새 인덱스 생성
python scripts/setup_data_optimized.py --api-key YOUR_KEY --recreate-index

# 2. 데이터 색인
python scripts/setup_data_optimized.py --api-key YOUR_KEY
```

### 방법 2: 기존 인덱스 재색인

```bash
# 1. 새 인덱스 생성
curl -X PUT "localhost:9200/health_supplements_v2" \
  -H 'Content-Type: application/json' \
  -d @config/index_settings_kibana.json

# 2. 데이터 재색인
POST _reindex
{
  "source": {
    "index": "health_supplements"
  },
  "dest": {
    "index": "health_supplements_v2"
  }
}

# 3. 별칭 변경
POST _aliases
{
  "actions": [
    {"remove": {"index": "health_supplements", "alias": "health_supplements_current"}},
    {"add": {"index": "health_supplements_v2", "alias": "health_supplements_current"}}
  ]
}
```

### 방법 3: 인덱스 템플릿 사용

```bash
# 템플릿 생성
curl -X PUT "localhost:9200/_index_template/health_supplements_template" \
  -H 'Content-Type: application/json' \
  -d @config/index_template.json
```

---

## 📊 추가 필드 제안

### 1. 통계 추적

```python
# 색인 시 자동 추가
doc['indexed_at'] = datetime.now().isoformat()
doc['stats'] = {
    'view_count': 0,
    'search_count': 0,
    'popularity_score': 0.0
}
```

### 2. 가격 범위 분류

```python
# 가격 정보가 있다면
if price:
    if price < 10000:
        doc['price_range'] = '저가'
    elif price < 30000:
        doc['price_range'] = '중가'
    else:
        doc['price_range'] = '고가'
```

### 3. 성분 개수

```python
# 원재료 개수 계산
doc['ingredient_count'] = len(doc['raw_materials'].split(','))
```

---

## 🎨 Kibana Index Pattern 설정

### 1. Index Pattern 생성

```
Management > Stack Management > Index Patterns > Create

Index pattern name: health_supplements*
Time field: report_date (또는 indexed_at)
```

### 2. Field Formatting

```
company_name.keyword: String
classification.category: String
report_date: Date (Format: YYYY-MM-DD)
stats.popularity_score: Number (Format: 0.00)
```

### 3. Scripted Fields (선택)

```javascript
// 제품 연령 (일 단위)
doc['indexed_at'].value.millis - doc['report_date'].value.millis
```

---

## 🚀 실행 순서

### 1단계: 설정 파일 업데이트

```bash
# 최적화된 설정 파일 생성
python scripts/generate_kibana_config.py
```

### 2단계: 인덱스 재생성

```bash
# 기존 데이터 백업
python scripts/backup_index.py

# 새 인덱스 생성 및 색인
python scripts/setup_data_optimized.py --api-key YOUR_KEY --recreate-index
```

### 3단계: Kibana 설정

```bash
# Kibana 대시보드 자동 생성
python scripts/setup_kibana_dashboard.py
```

### 4단계: 검증

```bash
# 인덱스 확인
curl -X GET "localhost:9200/health_supplements/_mapping?pretty"

# 샘플 데이터 확인
curl -X GET "localhost:9200/health_supplements/_search?size=1&pretty"
```

---

## ⚠️ 주의사항

### 1. Mapping 변경 불가

- 기존 인덱스의 mapping은 변경 불가
- 새 인덱스 생성 후 재색인 필요

### 2. 성능 고려

- 집계 필드는 `keyword` 타입 사용
- 불필요한 필드는 `enabled: false`
- 대용량 데이터는 샤드 수 증가 고려

### 3. 디스크 공간

- 재색인 시 2배 공간 필요
- 완료 후 기존 인덱스 삭제

---

## 💡 Best Practices

1. **Time-based Index**: 월별 인덱스 생성 고려
   ```
   health_supplements-2024-01
   health_supplements-2024-02
   ```

2. **Index Lifecycle Management (ILM)**: 오래된 데이터 자동 관리

3. **Rollover**: 인덱스 크기 제한
   ```
   max_size: 50GB
   max_age: 30d
   ```

4. **Snapshot**: 정기 백업
   ```bash
   # 매일 자동 스냅샷
   PUT _snapshot/my_backup/snapshot_$(date +%Y%m%d)
   ```

---

## 📝 체크리스트

색인 전 확인사항:

- [ ] 날짜 필드 추가 (`indexed_at`, `updated_at`)
- [ ] Keyword 필드 추가 (집계용)
- [ ] 통계 필드 추가 (`stats.*`)
- [ ] 가격 범위 분류 (선택)
- [ ] 성분 개수 계산 (선택)
- [ ] 인덱스 템플릿 설정
- [ ] Kibana Index Pattern 생성
- [ ] 대시보드 시각화 테스트

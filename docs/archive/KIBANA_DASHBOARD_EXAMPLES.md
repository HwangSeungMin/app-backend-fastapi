# Kibana 대시보드 구축 예시

현재 `health_supplements` 인덱스 데이터 기준으로 실용적인 대시보드를 만드는 방법입니다.

## 📊 인덱스 데이터 구조

```json
{
  "product_id": "제품ID",
  "product_name": "제품명",
  "company_name": "제조사명",
  "report_date": "신고일자",
  "raw_materials": "원료성분",
  "primary_function": "주요기능",
  "classification": {
    "category": "카테고리",
    "detail_category": "세부카테고리",
    "function_content": "기능성내용",
    "intake_method": "섭취방법",
    "intake_caution": "섭취주의사항"
  },
  "metadata": {
    "manufacturer": "제조사",
    "distribution_company": "유통사",
    "update_date": "갱신일자"
  },
  "embedding_vector": [벡터값...],
  "embedding_text": "임베딩용 텍스트"
}
```

---

## 🎯 추천 대시보드 1: 제품 현황 대시보드

### 목적
전체 건강기능식품 제품 현황을 한눈에 파악

### 포함할 시각화

#### 1️⃣ 전체 제품 수 (Metric)
```
Visualization Type: Metric
Metrics: Count
Label: "전체 제품 수"
```

**Dev Tools에서 생성:**
```json
POST /health_supplements/_search
{
  "size": 0,
  "aggs": {
    "total_products": {
      "value_count": {
        "field": "_id"
      }
    }
  }
}
```

#### 2️⃣ 카테고리별 제품 분포 (Donut Chart)
```
Visualization Type: Pie
Metrics: Count
Buckets:
  - Aggregation: Terms
  - Field: classification.category.keyword
  - Size: 10
  - Order: Descending
Display: Donut
```

**Dev Tools 쿼리:**
```json
POST /health_supplements/_search
{
  "size": 0,
  "aggs": {
    "category_distribution": {
      "terms": {
        "field": "classification.category.keyword",
        "size": 10
      }
    }
  }
}
```

#### 3️⃣ 제조사별 제품 수 TOP 20 (Horizontal Bar)
```
Visualization Type: Horizontal Bar
Metrics: Count
Buckets:
  - Aggregation: Terms
  - Field: company_name.keyword
  - Size: 20
  - Order: Descending by Count
```

**Dev Tools 쿼리:**
```json
POST /health_supplements/_search
{
  "size": 0,
  "aggs": {
    "top_companies": {
      "terms": {
        "field": "company_name.keyword",
        "size": 20,
        "order": { "_count": "desc" }
      }
    }
  }
}
```

#### 4️⃣ 월별 신규 제품 등록 추이 (Line Chart)
```
Visualization Type: Line
Metrics: Count
Buckets:
  - Aggregation: Date Histogram
  - Field: report_date
  - Interval: Monthly
```

**Dev Tools 쿼리:**
```json
POST /health_supplements/_search
{
  "size": 0,
  "aggs": {
    "products_over_time": {
      "date_histogram": {
        "field": "report_date",
        "calendar_interval": "month",
        "format": "yyyy-MM"
      }
    }
  }
}
```

#### 5️⃣ 최근 등록 제품 (Data Table)
```
Visualization Type: Data Table
Metrics: Top Hits (Size: 10)
Sort: report_date descending
Columns: product_name, company_name, report_date, classification.category
```

**Dev Tools 쿼리:**
```json
POST /health_supplements/_search
{
  "size": 10,
  "sort": [
    { "report_date": "desc" }
  ],
  "_source": ["product_name", "company_name", "report_date", "classification.category"]
}
```

---

## 🔬 추천 대시보드 2: 성분 분석 대시보드

### 목적
주요 성분별 제품 분석 및 트렌드 파악

#### 1️⃣ 주요 성분 워드 클라우드 (Tag Cloud)
```
Visualization Type: Tag Cloud
Metrics: Count
Buckets:
  - Aggregation: Terms
  - Field: raw_materials.keyword
  - Size: 100
```

**실제 구현 (성분 추출 필요):**

먼저 주요 성분을 추출하는 스크립트 필요:

```python
# scripts/extract_ingredients.py
from elasticsearch import Elasticsearch
from collections import Counter
import re

es = Elasticsearch(["http://localhost:9200"])

# 모든 제품의 원료성분 가져오기
results = es.search(
    index="health_supplements",
    body={
        "size": 10000,
        "_source": ["raw_materials"]
    }
)

# 성분 추출 및 카운팅
all_ingredients = []
for hit in results['hits']['hits']:
    raw_materials = hit['_source']['raw_materials']
    # 괄호 제거 및 쉼표로 분리
    ingredients = re.split(r'[,，]', raw_materials)
    for ing in ingredients:
        # 괄호 안 내용 제거
        ing = re.sub(r'\([^)]*\)', '', ing).strip()
        if ing:
            all_ingredients.append(ing)

# 상위 100개 성분
top_ingredients = Counter(all_ingredients).most_common(100)
for ing, count in top_ingredients[:20]:
    print(f"{ing}: {count}")
```

#### 2️⃣ 기능성 내용별 제품 분포 (Pie Chart)
```
Visualization Type: Pie
Metrics: Count
Buckets:
  - Aggregation: Terms
  - Field: classification.function_content.keyword
  - Size: 15
```

#### 3️⃣ 주요 기능별 제품 수 (Vertical Bar)
```
Visualization Type: Vertical Bar
Metrics: Count
Buckets:
  - Aggregation: Significant Terms
  - Field: primary_function
  - Size: 20
```

**Dev Tools 쿼리:**
```json
POST /health_supplements/_search
{
  "size": 0,
  "aggs": {
    "primary_functions": {
      "terms": {
        "field": "primary_function.keyword",
        "size": 20
      }
    }
  }
}
```

#### 4️⃣ 세부 카테고리 트리맵 (Tree Map)
```
Visualization Type: Tree Map
Metrics: Count
Buckets:
  - Group by: classification.category.keyword
  - Then by: classification.detail_category.keyword
```

---

## 📈 추천 대시보드 3: 검색 및 추천 분석 대시보드

### 목적
사용자 검색 패턴 및 추천 결과 분석 (로그 수집 필요)

이 대시보드는 API 로그를 Elasticsearch에 저장해야 합니다.

#### 로그 인덱스 생성

```python
# utils/search_logger.py
from elasticsearch import Elasticsearch
from datetime import datetime

class SearchLogger:
    def __init__(self):
        self.es = Elasticsearch(["http://localhost:9200"])
        self.index_name = "search_logs"

    def log_search(self, query_type, query, results_count, response_time):
        doc = {
            "timestamp": datetime.now(),
            "query_type": query_type,  # hybrid, symptom, ingredient
            "query": query,
            "results_count": results_count,
            "response_time_ms": response_time,
            "user_agent": "FastAPI",
        }
        self.es.index(index=self.index_name, document=doc)
```

#### 시각화 예시

**1. 시간대별 검색 수 (Area Chart)**
```
Field: timestamp
Interval: Hourly
Metrics: Count
```

**2. 인기 검색어 TOP 30 (Tag Cloud)**
```
Field: query.keyword
Size: 30
```

**3. 검색 유형별 분포 (Pie Chart)**
```
Field: query_type.keyword
```

---

## 🛠️ 실습: 대시보드 만들기

### Step 1: Kibana 접속
```
http://localhost:5601
```

### Step 2: Index Pattern 생성

1. **Management** → **Stack Management** 클릭
2. **Index Patterns** 선택
3. **Create index pattern** 클릭
4. Index pattern name: `health_supplements*`
5. Time field: `metadata.update_date` 또는 `@timestamp` (없으면 선택 안함)
6. **Create index pattern** 클릭

### Step 3: 데이터 탐색 (Discover)

1. 좌측 메뉴에서 **Discover** 클릭
2. Index pattern: `health_supplements*` 선택
3. 다양한 필드 확인:
   - `product_name`
   - `company_name`
   - `classification.category`
   - `primary_function`

### Step 4: 첫 번째 시각화 만들기 - 전체 제품 수

1. **Visualize Library** → **Create visualization** 클릭
2. **Metric** 선택
3. Index: `health_supplements*`
4. Metrics: `Count` (기본값)
5. **Save** 클릭
   - Title: "전체 제품 수"
   - Description: "건강기능식품 전체 제품 수"

### Step 5: 두 번째 시각화 - 카테고리별 분포

1. **Create visualization** → **Pie** 선택
2. Index: `health_supplements*`
3. **Buckets** → **Add** → **Split slices**
   - Aggregation: `Terms`
   - Field: `classification.category.keyword`
   - Size: `10`
   - Order by: `Metric: Count`
   - Descending
4. Options:
   - Donut 체크
   - Show labels 체크
5. **Update** → **Save**
   - Title: "카테고리별 제품 분포"

### Step 6: 세 번째 시각화 - 제조사 랭킹

1. **Create visualization** → **Horizontal Bar** 선택
2. Index: `health_supplements*`
3. Metrics: `Count`
4. **Buckets** → **Add** → **X-axis**
   - Aggregation: `Terms`
   - Field: `company_name.keyword`
   - Size: `20`
   - Order: `Metric: Count`
   - Order: `Descending`
5. **Update** → **Save**
   - Title: "제조사별 제품 수 TOP 20"

### Step 7: 대시보드 생성

1. 좌측 메뉴에서 **Dashboard** 클릭
2. **Create dashboard** 클릭
3. **Add** 버튼 클릭
4. 위에서 만든 시각화 3개 모두 추가
5. 크기와 위치 조정 (드래그 앤 드롭)
6. **Save** 클릭
   - Title: "건강기능식품 현황 대시보드"
   - Description: "전체 제품 현황 및 통계"

---

## 📊 고급 시각화 예시

### 1. TSVB (Time Series Visual Builder) - 트렌드 분석

```
Visualization Type: TSVB
Panel Options:
  - Data timerange mode: Entire time range

Series:
  - Metrics: Count
  - Group by: Terms (classification.category.keyword)
  - Chart type: Area

Annotations:
  - 특정 날짜에 중요 이벤트 표시
```

### 2. Vega - 커스텀 차트

제품 네트워크 그래프 (제조사-카테고리 관계):

```json
{
  "$schema": "https://vega.github.io/schema/vega/v5.json",
  "data": [
    {
      "name": "products",
      "url": {
        "index": "health_supplements",
        "body": {
          "size": 1000,
          "_source": ["company_name", "classification.category"]
        }
      },
      "format": {"property": "hits.hits"}
    }
  ],
  "marks": [
    {
      "type": "symbol",
      "from": {"data": "products"},
      "encode": {
        "enter": {
          "x": {"signal": "random() * width"},
          "y": {"signal": "random() * height"}
        }
      }
    }
  ]
}
```

### 3. Lens - 빠른 시각화

Lens는 드래그 앤 드롭으로 쉽게 시각화 생성:

1. **Visualize Library** → **Create visualization** → **Lens**
2. 필드를 원하는 위치로 드래그:
   - `classification.category.keyword` → Vertical axis
   - `Count` → Horizontal axis
3. 차트 타입 변경 (Bar, Line, Area 등)
4. 저장

---

## 🎨 대시보드 레이아웃 추천

### 레이아웃 1: 상단 KPI + 차트

```
┌─────────────────────────────────────────────────┐
│  전체 제품 수    카테고리 수    제조사 수      │
│    12,345         25            450           │
├─────────────────────────────────────────────────┤
│                                                 │
│  카테고리별 분포 (Donut)  │  월별 등록 추이    │
│                           │   (Line Chart)     │
│                           │                    │
├───────────────────────────┴────────────────────┤
│                                                 │
│         제조사별 제품 수 TOP 20                 │
│         (Horizontal Bar Chart)                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 레이아웃 2: 그리드 레이아웃

```
┌──────────────┬──────────────┬──────────────┐
│  전체 제품   │ 카테고리 분포│  최근 등록   │
│   (Metric)   │    (Pie)     │   (Table)    │
├──────────────┴──────────────┴──────────────┤
│                                             │
│        제조사별 제품 수 (Bar Chart)         │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│        주요 성분 워드 클라우드              │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🔗 필터와 인터랙션

### Dashboard Controls 추가

1. Dashboard 편집 모드에서 **Add** → **Controls**
2. Control 유형 선택:
   - **Options list**: 카테고리 선택
   - **Range slider**: 날짜 범위
3. 설정:
   - Field: `classification.category.keyword`
   - Label: "카테고리 필터"
   - Multi-select: 활성화

### Drilldown 설정

시각화 클릭 → 상세 데이터 표시:
1. 시각화 설정에서 **Interactions** 활성화
2. 클릭 시 필터 적용 또는 다른 대시보드로 이동

---

## 📝 실전 예시 스크립트

전체 대시보드를 자동으로 생성하는 Python 스크립트:

```python
# scripts/create_complete_dashboard.py
import requests
import json

KIBANA_URL = "http://localhost:5601"
INDEX_PATTERN = "health_supplements"

def create_visualizations():
    """모든 시각화 생성"""

    visualizations = [
        {
            "id": "product-count",
            "title": "전체 제품 수",
            "type": "metric",
            "params": {
                "metric": {
                    "colorSchema": "Green to Red",
                    "metricColorMode": "None",
                    "style": {"fontSize": 60}
                }
            }
        },
        {
            "id": "category-pie",
            "title": "카테고리별 분포",
            "type": "pie",
            "params": {
                "addLegend": True,
                "addTooltip": True,
                "isDonut": True,
                "legendPosition": "right"
            }
        },
        # ... 더 많은 시각화
    ]

    for viz in visualizations:
        create_visualization(viz)

def create_dashboard():
    """대시보드 생성"""

    dashboard_config = {
        "title": "건강기능식품 종합 대시보드",
        "panels": [
            {"id": "product-count", "gridData": {"x": 0, "y": 0, "w": 12, "h": 4}},
            {"id": "category-pie", "gridData": {"x": 12, "y": 0, "w": 12, "h": 8}},
            # ... 패널 배치
        ]
    }

    # API 호출하여 대시보드 생성
    # ...

if __name__ == '__main__':
    create_visualizations()
    create_dashboard()
    print("대시보드 생성 완료!")
```

---

## 📚 참고 자료

- [Kibana Visualizations](https://www.elastic.co/guide/en/kibana/current/dashboard.html)
- [Elasticsearch Aggregations](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html)
- [Kibana Lens](https://www.elastic.co/guide/en/kibana/current/lens.html)

---

**다음 단계:**
1. 위 예시대로 시각화 생성
2. 대시보드로 조합
3. 필터 및 Controls 추가
4. 팀원들과 공유

대시보드 구축 중 궁금한 점이 있으면 언제든 문의하세요! 🎯

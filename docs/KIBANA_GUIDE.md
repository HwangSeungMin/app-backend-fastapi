# Kibana 사용 가이드

건강기능식품 RAG 시스템의 데이터를 Kibana로 시각화하고 모니터링하는 방법을 안내합니다.

## 목차

1. [Kibana 시작하기](#kibana-시작하기)
2. [인덱스 패턴 설정](#인덱스-패턴-설정)
3. [대시보드 구성](#대시보드-구성)
4. [유용한 쿼리](#유용한-쿼리)
5. [시각화 예제](#시각화-예제)

---

## Kibana 시작하기

### 1. Docker Compose로 Kibana 실행

```bash
# Elasticsearch와 Kibana 함께 시작
docker-compose up -d

# Kibana 로그 확인
docker-compose logs -f kibana
```

### 2. Kibana 접속

- URL: http://localhost:5601
- 초기 로딩 시간: 약 1-2분 소요

### 3. 자동 설정 스크립트 실행

```bash
# 인덱스 패턴 및 기본 시각화 자동 생성
python scripts/setup_kibana_dashboard.py
```

---

## 인덱스 패턴 설정

### 수동으로 인덱스 패턴 생성하기

1. Kibana 메인 페이지에서 **Management** → **Stack Management** 클릭
2. 왼쪽 메뉴에서 **Index Patterns** 선택
3. **Create index pattern** 클릭
4. 인덱스 패턴 입력: `health_supplements*`
5. Time field 선택: `metadata.update_date` (옵션)
6. **Create index pattern** 클릭

---

## 대시보드 구성

### 추천 대시보드 레이아웃

#### 1. 개요 대시보드 (Overview Dashboard)

**포함 시각화:**
- 전체 제품 수 (Metric)
- 카테고리별 분포 (Pie Chart)
- 제조사별 제품 수 TOP 10 (Horizontal Bar)
- 최근 등록 제품 (Data Table)

#### 2. 검색 분석 대시보드 (Search Analytics Dashboard)

**포함 시각화:**
- 시간대별 검색 쿼리 수 (Line Chart)
- 인기 검색어 TOP 20 (Tag Cloud)
- 검색 결과 없는 쿼리 (Data Table)

#### 3. 성분 분석 대시보드 (Ingredient Analysis Dashboard)

**포함 시각화:**
- 주요 성분별 제품 수 (Tree Map)
- 성분 조합 패턴 (Network Graph)
- 성분별 평균 가격 (Bar Chart)

---

## 유용한 쿼리

### Discover 탭에서 사용할 수 있는 쿼리

#### 1. 특정 성분을 포함한 제품 검색

```
raw_materials: "비타민D"
```

#### 2. 특정 카테고리 제품 검색

```
classification.category: "건강기능식품"
```

#### 3. 특정 회사의 제품 검색

```
company_name: "한국건강식품"
```

#### 4. 여러 조건 조합

```
classification.category: "건강기능식품" AND raw_materials: "오메가3"
```

#### 5. 특정 기간 내 등록된 제품

```
metadata.update_date: [2024-01-01 TO 2024-12-31]
```

---

## 시각화 예제

### 1. 카테고리별 제품 수 (Pie Chart)

**설정:**
- Visualization Type: Pie
- Metrics: Count
- Buckets:
  - Aggregation: Terms
  - Field: `classification.category.keyword`
  - Size: 10

### 2. 제조사별 제품 수 (Horizontal Bar)

**설정:**
- Visualization Type: Horizontal Bar
- Metrics: Count
- Buckets:
  - Aggregation: Terms
  - Field: `company_name.keyword`
  - Size: 10
  - Order: Descending

### 3. 주요 성분 워드 클라우드 (Tag Cloud)

**설정:**
- Visualization Type: Tag Cloud
- Metrics: Count
- Buckets:
  - Aggregation: Terms
  - Field: `raw_materials.keyword`
  - Size: 50

### 4. 월별 제품 등록 추이 (Line Chart)

**설정:**
- Visualization Type: Line
- Metrics: Count
- Buckets:
  - Aggregation: Date Histogram
  - Field: `metadata.update_date`
  - Interval: Monthly

### 5. 제품 상세 테이블 (Data Table)

**설정:**
- Visualization Type: Data Table
- Metrics: Count
- Buckets:
  - Split Rows: Terms
  - Field: `product_name.keyword`
  - Size: 100

**Columns to display:**
- product_name
- company_name
- classification.category
- primary_function

---

## 고급 기능

### 1. Saved Searches (저장된 검색)

자주 사용하는 검색 쿼리를 저장하여 빠르게 재사용:

```
1. Discover 탭에서 검색 쿼리 작성
2. 상단의 "Save" 버튼 클릭
3. 검색 이름 입력 및 저장
```

### 2. Dashboard Filters

대시보드에 필터를 추가하여 동적으로 데이터 탐색:

```
1. Dashboard에서 "Add filter" 클릭
2. Field 선택 (예: classification.category)
3. Operator 선택 (is, is not, is one of 등)
4. Value 입력
5. "Save" 클릭
```

### 3. Dashboard Time Range

시간 범위를 설정하여 특정 기간의 데이터만 표시:

```
1. 우측 상단의 시계 아이콘 클릭
2. Quick select 또는 Absolute/Relative 범위 선택
3. "Update" 클릭
```

---

## 성능 최적화 팁

### 1. 인덱스 패턴 최적화

- 불필요한 필드는 인덱스 패턴에서 제외
- Time-based 인덱스 사용 시 날짜 범위 제한

### 2. 시각화 최적화

- Aggregation size 최소화 (필요한 만큼만)
- 복잡한 스크립트 사용 자제
- 캐시 활용

### 3. 대시보드 최적화

- 너무 많은 시각화를 한 대시보드에 넣지 않기 (권장: 6-8개)
- Auto-refresh 간격 적절히 설정 (권장: 30초 이상)

---

## 문제 해결

### Kibana가 시작되지 않을 때

```bash
# Kibana 로그 확인
docker-compose logs kibana

# Elasticsearch 연결 확인
curl http://localhost:9200

# 컨테이너 재시작
docker-compose restart kibana
```

### 인덱스 패턴이 보이지 않을 때

1. Elasticsearch에 데이터가 있는지 확인:
   ```bash
   curl http://localhost:9200/health_supplements/_count
   ```

2. 인덱스 패턴 새로고침:
   - Management → Index Patterns → 새로고침 아이콘 클릭

### 시각화가 표시되지 않을 때

1. Time range 확인 (데이터가 있는 범위로 설정)
2. 필터 조건 확인
3. Aggregation 설정 확인

---

## 참고 자료

- [Kibana 공식 문서](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Elasticsearch Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
- [Kibana 시각화 가이드](https://www.elastic.co/guide/en/kibana/current/visualize.html)

---

## 추가 시각화 아이디어

### 1. 제품 검색 히트맵
- 시간대별 검색 활동 패턴 분석
- X축: 시간, Y축: 요일

### 2. 성분 네트워크 그래프
- 자주 함께 사용되는 성분 조합 시각화
- Node: 성분, Edge: 공통 제품 수

### 3. 가격 분포 히스토그램
- 제품 가격대별 분포 분석
- 카테고리별 가격 비교

### 4. 지역별 제조사 분포 지도
- 제조사 소재지 기준 지도 시각화
- Coordinate Map 활용

---

**문의사항이나 추가 요청사항이 있으시면 이슈를 등록해주세요!**

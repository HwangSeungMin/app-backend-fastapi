# 📚 프로젝트 문서 정리

## 📂 문서 분류 및 정리

### 1️⃣ 핵심 가이드 (필수 문서)

#### [`README.md`](file:///d:/yakkobak_be/README.md)
- **목적**: 프로젝트 전체 개요
- **대상**: 모든 사용자
- **상태**: ✅ 유지

#### [`README_RAG.md`](file:///d:/yakkobak_be/README_RAG.md)
- **목적**: RAG 시스템 개요
- **대상**: RAG 개발자
- **상태**: ✅ 유지

---

### 2️⃣ API 문서

#### [`docs/API_INTELLIGENT_SEARCH.md`](file:///d:/yakkobak_be/docs/API_INTELLIGENT_SEARCH.md)
- **목적**: 지능형 검색 API 상세 분석
- **내용**: 7단계 파이프라인, 컴포넌트 분석
- **상태**: ✅ 유지 (최신)

#### [`docs/query_expansion_and_api_guide.md`](file:///d:/yakkobak_be/docs/query_expansion_and_api_guide.md)
- **목적**: 쿼리 확장 및 API 가이드
- **내용**: 쿼리 확장 기법, API 사용법
- **상태**: ⚠️ 검토 필요 (중복 가능성)

---

### 3️⃣ Elasticsearch & 색인 문서

#### [`docs/indexing_guide.md`](file:///d:/yakkobak_be/docs/indexing_guide.md)
- **목적**: 색인 작업 가이드
- **내용**: 데이터 수집, 전처리, 색인 방법
- **상태**: ⚠️ 업데이트 필요 (C003 전용으로 변경됨)

#### [`docs/INDEX_STRUCTURE_IMPROVEMENT.md`](file:///d:/yakkobak_be/docs/INDEX_STRUCTURE_IMPROVEMENT.md)
- **목적**: 색인 구조 개선 분석
- **내용**: C003 API 분석, 유실 필드, 개선 방안
- **상태**: ✅ 유지 (최신)

#### [`docs/C003_RAG_INDEXING_COMPLETE.md`](file:///d:/yakkobak_be/docs/C003_RAG_INDEXING_COMPLETE.md)
- **목적**: C003 전용 색인 시스템 완료 보고
- **내용**: 변경 사항, 사용 방법, 개선 효과
- **상태**: ✅ 유지 (최신)

#### [`docs/elasticsearch-nori-setup.md`](file:///d:/yakkobak_be/docs/elasticsearch-nori-setup.md)
- **목적**: Nori 플러그인 설정 가이드
- **내용**: 한국어 형태소 분석기 설치
- **상태**: ✅ 유지

#### [`docs/kibana_index_optimization.md`](file:///d:/yakkobak_be/docs/kibana_index_optimization.md)
- **목적**: Kibana용 인덱스 최적화
- **내용**: 집계 필드, 시계열 분석
- **상태**: ✅ 유지

---

### 4️⃣ Kibana 문서 (중복 많음!)

#### ✅ 유지할 문서

##### [`docs/KIBANA_GUIDE.md`](file:///d:/yakkobak_be/docs/KIBANA_GUIDE.md)
- **목적**: Kibana 종합 가이드
- **내용**: 설치, 설정, 대시보드 생성
- **상태**: ✅ 유지 (메인 가이드)

##### [`docs/KIBANA_STANDALONE.md`](file:///d:/yakkobak_be/docs/KIBANA_STANDALONE.md)
- **목적**: Kibana 독립 실행 가이드
- **내용**: Docker 없이 Kibana 실행
- **상태**: ✅ 유지 (특수 용도)

#### ⚠️ 통합 검토 대상

##### [`docs/KIBANA_DASHBOARD_EXAMPLES.md`](file:///d:/yakkobak_be/docs/KIBANA_DASHBOARD_EXAMPLES.md)
- **목적**: Kibana 대시보드 예시
- **내용**: 시각화 예제
- **상태**: ⚠️ KIBANA_GUIDE.md와 통합 가능

##### [`docs/KIBANA_QUICK_GUIDE.md`](file:///d:/yakkobak_be/docs/KIBANA_QUICK_GUIDE.md)
- **목적**: Kibana 빠른 시작 가이드
- **내용**: 간단한 설정 방법
- **상태**: ⚠️ KIBANA_GUIDE.md와 통합 가능

---

### 5️⃣ Docker 문서

#### [`docs/DOCKER_GUIDE.md`](file:///d:/yakkobak_be/docs/DOCKER_GUIDE.md)
- **목적**: Docker 사용 가이드
- **내용**: Docker Compose 설정, 실행 방법
- **상태**: ✅ 유지

---

### 6️⃣ 기타 문서

#### [`docs/ENCODING_GUIDE.md`](file:///d:/yakkobak_be/docs/ENCODING_GUIDE.md)
- **목적**: 인코딩 문제 해결 가이드
- **내용**: UTF-8 인코딩 설정
- **상태**: ✅ 유지

#### [`docs/intelligent_search_guide.md`](file:///d:/yakkobak_be/docs/intelligent_search_guide.md)
- **목적**: 지능형 검색 가이드
- **내용**: 검색 기능 사용법
- **상태**: ⚠️ API_INTELLIGENT_SEARCH.md와 중복 가능성

---

## 🗂️ 정리 제안

### ✅ 유지할 문서 (11개)

**핵심 문서**:
1. `README.md` - 프로젝트 개요
2. `README_RAG.md` - RAG 시스템 개요

**API 문서**:
3. `docs/API_INTELLIGENT_SEARCH.md` - 지능형 검색 API

**색인 문서**:
4. `docs/INDEX_STRUCTURE_IMPROVEMENT.md` - 색인 구조 분석
5. `docs/C003_RAG_INDEXING_COMPLETE.md` - C003 색인 완료
6. `docs/elasticsearch-nori-setup.md` - Nori 설정
7. `docs/kibana_index_optimization.md` - 인덱스 최적화

**Kibana 문서**:
8. `docs/KIBANA_GUIDE.md` - Kibana 메인 가이드
9. `docs/KIBANA_STANDALONE.md` - 독립 실행 가이드

**기타**:
10. `docs/DOCKER_GUIDE.md` - Docker 가이드
11. `docs/ENCODING_GUIDE.md` - 인코딩 가이드

### 🔄 통합/업데이트 필요 (4개)

#### 통합 대상
1. **`docs/KIBANA_DASHBOARD_EXAMPLES.md`** → `KIBANA_GUIDE.md`에 통합
2. **`docs/KIBANA_QUICK_GUIDE.md`** → `KIBANA_GUIDE.md`에 통합
3. **`docs/intelligent_search_guide.md`** → `API_INTELLIGENT_SEARCH.md`와 통합 또는 제거

#### 업데이트 필요
4. **`docs/indexing_guide.md`** → C003 전용으로 업데이트 또는 제거

### ❌ 제거 검토 대상 (1개)

1. **`docs/query_expansion_and_api_guide.md`** - 내용 확인 후 통합 또는 제거

---

## 📋 정리 작업 계획

### Phase 1: 중복 문서 통합

```bash
# 1. Kibana 문서 통합
# KIBANA_DASHBOARD_EXAMPLES.md + KIBANA_QUICK_GUIDE.md → KIBANA_GUIDE.md

# 2. 검색 문서 통합
# intelligent_search_guide.md → API_INTELLIGENT_SEARCH.md
```

### Phase 2: 업데이트

```bash
# indexing_guide.md를 C003 전용으로 업데이트
# 또는 C003_RAG_INDEXING_COMPLETE.md로 대체
```

### Phase 3: 정리 후 디렉토리 구조

```
docs/
├── 📘 핵심 가이드
│   ├── README.md (루트)
│   └── README_RAG.md (루트)
│
├── 🔍 API 문서
│   └── API_INTELLIGENT_SEARCH.md
│
├── 💾 데이터 & 색인
│   ├── INDEX_STRUCTURE_IMPROVEMENT.md
│   ├── C003_RAG_INDEXING_COMPLETE.md
│   ├── elasticsearch-nori-setup.md
│   └── kibana_index_optimization.md
│
├── 📊 Kibana
│   ├── KIBANA_GUIDE.md (통합됨)
│   └── KIBANA_STANDALONE.md
│
└── 🛠️ 기타
    ├── DOCKER_GUIDE.md
    └── ENCODING_GUIDE.md
```

---

## 🎯 정리 후 예상 효과

| 항목 | Before | After | 개선 |
|------|--------|-------|------|
| **총 문서 수** | 17개 | 11개 | **-35%** |
| **중복 문서** | 4개 | 0개 | **✅** |
| **유지보수성** | 낮음 | 높음 | **✅** |

---

## ⚡ 즉시 실행 가능한 정리

원하시면 다음 작업을 진행할 수 있습니다:

1. **중복 Kibana 문서 통합**
2. **오래된 문서 아카이브** (`docs/archive/` 폴더로 이동)
3. **문서 인덱스 생성** (`docs/INDEX.md`)

어떤 작업을 진행할까요?

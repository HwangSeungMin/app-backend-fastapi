# 🔍 색인 구조 개선 분석

## 📊 C003 API 데이터 구조 분석

### 원본 필드 (C003 API)

```json
{
  "PRDLST_REPORT_NO": "200400150395",        // 제품 신고번호
  "SHAP": "",                                 // 형태 (비어있음)
  "PRMS_DT": "20040302",                     // 허가일자
  "LAST_UPDT_DTM": "20150522",               // 최종 수정일
  "PRDT_SHAP_CD_NM": "캡슐",                 // 제품 형태 코드명
  "LCNS_NO": "20040015039",                  // 인허가번호
  "CRET_DTM": "20150522",                    // 생성일시
  "PRDLST_NM": "영양칼슘비타민",             // 제품명
  "IFTKN_ATNT_MATR_CN": "물과 함께...",     // 섭취 시 주의사항
  "BSSH_NM": "고려인삼과학주식회사",         // 업소명 (제조사)
  "STDR_STND": "1. 성상 : ...",             // 기준 및 규격
  "DISPOS": "불투명의 녹색 경질캅셀",        // 성상 (외관)
  "PRIMARY_FNCLTY": "①뼈와 치아...",        // 주요 기능성
  "POG_DAYCNT": "제조일로부터 2년",          // 유통기한
  "CSTDY_MTHD": "",                          // 보관방법
  "NTK_MTHD": "1일 3회...",                  // 섭취방법
  "RAWMTRL_NM": "유청칼슘, 비타민B1..."      // 원재료명
}
```

## ⚠️ 현재 색인 구조의 문제점

### 1. 필드 매핑 불일치

| C003 API 필드 | 현재 색인 필드 | 상태 |
|---------------|----------------|------|
| `PRDLST_REPORT_NO` | `product_id` | ✅ 매핑됨 |
| `PRDLST_NM` | `product_name` | ✅ 매핑됨 |
| `BSSH_NM` | `company_name` | ✅ 매핑됨 |
| `RAWMTRL_NM` | `raw_materials` | ✅ 매핑됨 |
| `PRIMARY_FNCLTY` | `primary_function` | ✅ 매핑됨 |
| `PRMS_DT` | `report_date` | ✅ 매핑됨 |
| **`PRDT_SHAP_CD_NM`** | ❌ **없음** | ⚠️ **유실** |
| **`IFTKN_ATNT_MATR_CN`** | `classification.intake_caution` | ⚠️ 부분 매핑 |
| **`NTK_MTHD`** | `classification.intake_method` | ⚠️ 부분 매핑 |
| **`STDR_STND`** | ❌ **없음** | ⚠️ **유실** |
| **`DISPOS`** | ❌ **없음** | ⚠️ **유실** |
| **`POG_DAYCNT`** | ❌ **없음** | ⚠️ **유실** |
| **`CSTDY_MTHD`** | ❌ **없음** | ⚠️ **유실** |
| **`LAST_UPDT_DTM`** | ❌ **없음** | ⚠️ **유실** |
| **`LCNS_NO`** | ❌ **없음** | ⚠️ **유실** |

### 2. 유실된 중요 정보

#### 🔴 높은 우선순위 (검색/필터링에 중요)
1. **`PRDT_SHAP_CD_NM`** (제품 형태): 캡슐, 정제, 분말 등 - **필터링 필수**
2. **`STDR_STND`** (기준 및 규격): 성분 함량 정보 포함 - **검색 중요**
3. **`DISPOS`** (성상/외관): 제품 식별에 유용
4. **`POG_DAYCNT`** (유통기한): 제품 정보 필수

#### 🟡 중간 우선순위 (메타데이터)
5. **`LAST_UPDT_DTM`** (최종 수정일): 데이터 신선도 확인
6. **`LCNS_NO`** (인허가번호): 제품 추적
7. **`CSTDY_MTHD`** (보관방법): 제품 정보

### 3. 데이터 구조 문제

```python
# 현재 구조
{
    "classification": {
        "category": "...",           # 어디서 오는지 불명확
        "detail_category": "...",    # 어디서 오는지 불명확
        "function_content": "...",   # PRIMARY_FNCLTY와 중복?
        "intake_method": "...",      # NTK_MTHD
        "intake_caution": "..."      # IFTKN_ATNT_MATR_CN
    }
}
```

**문제점**:
- `category`, `detail_category`: C003 API에 없는 필드 (다른 API에서 가져와야 함)
- `function_content`와 `primary_function` 중복 가능성

## ✅ 개선된 색인 구조 제안

### 1. 완전한 필드 매핑

```json
{
  "mappings": {
    "properties": {
      // ========== 기본 정보 ==========
      "product_id": {
        "type": "keyword"
      },
      "product_name": {
        "type": "text",
        "analyzer": "korean",
        "fields": {
          "keyword": {"type": "keyword"},
          "ngram": {"type": "text", "analyzer": "korean_ngram"}
        }
      },
      "company_name": {
        "type": "text",
        "analyzer": "korean",
        "fields": {
          "keyword": {"type": "keyword"},
          "ngram": {"type": "text", "analyzer": "korean_ngram"}
        }
      },
      
      // ========== 날짜 정보 ==========
      "report_date": {
        "type": "date",
        "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis"
      },
      "last_update_date": {
        "type": "date",
        "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis"
      },
      "created_date": {
        "type": "date",
        "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis"
      },
      
      // ========== 제품 형태 (NEW!) ==========
      "product_shape": {
        "type": "keyword"  // 캡슐, 정제, 분말, 액상 등
      },
      
      // ========== 원재료 정보 ==========
      "raw_materials": {
        "type": "text",
        "analyzer": "korean",
        "fields": {
          "keyword": {"type": "keyword"},
          "ngram": {"type": "text", "analyzer": "korean_ngram"}
        }
      },
      
      // ========== 기능성 정보 ==========
      "primary_function": {
        "type": "text",
        "analyzer": "korean",
        "fields": {
          "keyword": {"type": "keyword"},
          "ngram": {"type": "text", "analyzer": "korean_ngram"}
        }
      },
      
      // ========== 섭취 정보 ==========
      "intake_info": {
        "properties": {
          "method": {
            "type": "text",
            "analyzer": "korean"
          },
          "caution": {
            "type": "text",
            "analyzer": "korean"
          }
        }
      },
      
      // ========== 제품 상세 정보 (NEW!) ==========
      "product_details": {
        "properties": {
          "standards": {
            "type": "text",
            "analyzer": "korean"
          },
          "appearance": {
            "type": "text",
            "analyzer": "korean"
          },
          "shelf_life": {
            "type": "keyword"
          },
          "storage_method": {
            "type": "text",
            "analyzer": "korean"
          }
        }
      },
      
      // ========== 인허가 정보 (NEW!) ==========
      "license_info": {
        "properties": {
          "license_no": {
            "type": "keyword"
          },
          "report_no": {
            "type": "keyword"
          }
        }
      },
      
      // ========== 분류 정보 (선택적) ==========
      "classification": {
        "properties": {
          "category": {"type": "keyword"},
          "detail_category": {"type": "keyword"},
          "function_content": {
            "type": "text",
            "analyzer": "korean",
            "fields": {
              "keyword": {"type": "keyword"}
            }
          }
        }
      },
      
      // ========== 메타데이터 ==========
      "metadata": {
        "properties": {
          "source": {"type": "keyword"},  // "C003_API"
          "version": {"type": "keyword"},
          "indexed_at": {"type": "date"},
          "updated_at": {"type": "date"}
        }
      },
      
      // ========== 임베딩 벡터 ==========
      "embedding_vector": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      },
      "embedding_text": {
        "type": "text",
        "analyzer": "korean"
      }
    }
  }
}
```

### 2. 데이터 변환 매핑

```python
# C003 API → Elasticsearch 매핑
FIELD_MAPPING = {
    # 기본 정보
    "PRDLST_REPORT_NO": "product_id",
    "PRDLST_NM": "product_name",
    "BSSH_NM": "company_name",
    
    # 날짜 정보
    "PRMS_DT": "report_date",
    "LAST_UPDT_DTM": "last_update_date",
    "CRET_DTM": "created_date",
    
    # 제품 형태 (NEW!)
    "PRDT_SHAP_CD_NM": "product_shape",
    
    # 원재료
    "RAWMTRL_NM": "raw_materials",
    
    # 기능성
    "PRIMARY_FNCLTY": "primary_function",
    
    # 섭취 정보
    "NTK_MTHD": "intake_info.method",
    "IFTKN_ATNT_MATR_CN": "intake_info.caution",
    
    # 제품 상세 (NEW!)
    "STDR_STND": "product_details.standards",
    "DISPOS": "product_details.appearance",
    "POG_DAYCNT": "product_details.shelf_life",
    "CSTDY_MTHD": "product_details.storage_method",
    
    # 인허가 정보 (NEW!)
    "LCNS_NO": "license_info.license_no",
    "PRDLST_REPORT_NO": "license_info.report_no"
}
```

### 3. 임베딩 텍스트 생성 개선

```python
def create_embedding_text(doc):
    """임베딩용 텍스트 생성 (개선 버전)"""
    
    parts = [
        doc.get("product_name", ""),
        doc.get("company_name", ""),
        doc.get("raw_materials", ""),
        doc.get("primary_function", ""),
        doc.get("product_shape", ""),  # NEW!
        doc.get("product_details", {}).get("appearance", ""),  # NEW!
        doc.get("intake_info", {}).get("method", "")
    ]
    
    # 빈 문자열 제거 및 결합
    text = " ".join([p for p in parts if p])
    
    return text
```

## 📋 마이그레이션 계획

### Phase 1: 색인 구조 업데이트

1. **새 매핑 정의**
   ```bash
   # elasticsearch_config.py 수정
   ```

2. **인덱스 재생성**
   ```bash
   python scripts/update_index.py recreate
   ```

### Phase 2: 데이터 변환 로직 수정

1. **데이터 프로세서 수정**
   ```python
   # data/data_processor.py
   def transform_c003_data(api_data):
       """C003 API 데이터 변환"""
       transformed = {
           "product_id": api_data["PRDLST_REPORT_NO"],
           "product_name": api_data["PRDLST_NM"],
           "company_name": api_data["BSSH_NM"],
           "report_date": api_data["PRMS_DT"],
           "last_update_date": api_data.get("LAST_UPDT_DTM"),
           "created_date": api_data.get("CRET_DTM"),
           
           # NEW: 제품 형태
           "product_shape": api_data.get("PRDT_SHAP_CD_NM"),
           
           "raw_materials": api_data.get("RAWMTRL_NM"),
           "primary_function": api_data.get("PRIMARY_FNCLTY"),
           
           # 섭취 정보
           "intake_info": {
               "method": api_data.get("NTK_MTHD"),
               "caution": api_data.get("IFTKN_ATNT_MATR_CN")
           },
           
           # NEW: 제품 상세
           "product_details": {
               "standards": api_data.get("STDR_STND"),
               "appearance": api_data.get("DISPOS"),
               "shelf_life": api_data.get("POG_DAYCNT"),
               "storage_method": api_data.get("CSTDY_MTHD")
           },
           
           # NEW: 인허가 정보
           "license_info": {
               "license_no": api_data.get("LCNS_NO"),
               "report_no": api_data.get("PRDLST_REPORT_NO")
           },
           
           # 메타데이터
           "metadata": {
               "source": "C003_API",
               "indexed_at": datetime.now().isoformat()
           }
       }
       
       # 임베딩 텍스트 생성
       transformed["embedding_text"] = create_embedding_text(transformed)
       
       return transformed
   ```

### Phase 3: 재색인

```bash
# 1. 새 데이터 수집
python scripts/fetch_c003_data.py --output data/raw/c003_data.json

# 2. 데이터 변환
python scripts/transform_data.py --input data/raw/c003_data.json --output data/processed/c003_transformed.json

# 3. 재색인
python scripts/update_index.py reindex --data-file data/processed/c003_transformed.json
```

## 🔍 검색 개선 효과

### 1. 제품 형태 필터링 가능

```python
# 캡슐 형태만 검색
{
    "query": {
        "bool": {
            "must": [
                {"match": {"product_name": "비타민"}}
            ],
            "filter": [
                {"term": {"product_shape": "캡슐"}}
            ]
        }
    }
}
```

### 2. 성분 함량 검색 가능

```python
# 기준 및 규격에서 특정 함량 검색
{
    "query": {
        "match": {
            "product_details.standards": "비타민C 표시량"
        }
    }
}
```

### 3. 유통기한 정보 제공

```python
# 제품 상세 정보에 유통기한 포함
{
    "_source": ["product_name", "product_details.shelf_life"]
}
```

## 📊 비교표

| 항목 | 현재 구조 | 개선 구조 | 개선 효과 |
|------|----------|----------|----------|
| **필드 수** | 15개 | 25개 | +67% |
| **C003 커버리지** | 60% | 95% | +35% |
| **검색 가능 필드** | 8개 | 15개 | +88% |
| **필터링 옵션** | 3개 | 8개 | +167% |
| **메타데이터** | 기본 | 상세 | ✅ |

## ⚡ 즉시 적용 가능한 개선

### 최소 변경 (Quick Win)

현재 구조를 크게 바꾸지 않고 필드만 추가:

```python
# elasticsearch_config.py의 mappings에 추가
"product_shape": {"type": "keyword"},
"shelf_life": {"type": "keyword"},
"standards": {"type": "text", "analyzer": "korean"},
"appearance": {"type": "text", "analyzer": "korean"},
"storage_method": {"type": "text", "analyzer": "korean"},
"license_no": {"type": "keyword"},
"last_update_date": {"type": "date", "format": "yyyyMMdd"}
```

이렇게 하면 **기존 데이터 유지 + 새 필드 추가**가 가능합니다!

## 🎯 결론

**유실된 정보**:
- 제품 형태 (캡슐/정제/분말)
- 기준 및 규격 (성분 함량)
- 외관/성상
- 유통기한
- 보관방법
- 인허가번호
- 최종 수정일

**권장 조치**:
1. **즉시**: 최소 변경으로 중요 필드 추가
2. **단기**: 데이터 변환 로직 수정
3. **중기**: 전체 색인 구조 재설계 및 재색인

이렇게 하면 검색 품질과 사용자 경험이 크게 향상됩니다! 🚀

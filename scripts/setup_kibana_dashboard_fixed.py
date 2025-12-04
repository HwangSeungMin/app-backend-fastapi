"""
Kibana 대시보드 설정 스크립트 (수정 버전)
실제 색인된 데이터 구조에 맞게 조정된 대시보드 생성
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)

KIBANA_URL = "http://localhost:5601"
ES_INDEX = "health_supplements"

def wait_for_kibana(max_retries=30, delay=5):
    """Kibana가 준비될 때까지 대기"""
    logger.info("Kibana 서버 연결 대기 중...")

    for i in range(max_retries):
        try:
            response = requests.get(f"{KIBANA_URL}/api/status", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Kibana 서버 연결 성공!")
                return True
        except Exception as e:
            logger.warning(f"대기 중... ({i+1}/{max_retries})")
            time.sleep(delay)

    logger.error("Kibana 서버에 연결할 수 없습니다.")
    return False

def create_index_pattern():
    """인덱스 패턴 생성 (시간 필드: indexed_at)"""
    logger.info("인덱스 패턴 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/index-pattern/{ES_INDEX}"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": f"{ES_INDEX}*",
            "timeFieldName": "indexed_at"  # 실제 date 타입 필드 사용
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code in [200, 409]:  # 200: 생성 성공, 409: 이미 존재
            logger.info("✓ 인덱스 패턴 생성 완료")
            return True
        else:
            logger.error(f"인덱스 패턴 생성 실패: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"인덱스 패턴 생성 오류: {e}")
        return False

def create_visualization_product_count():
    """전체 제품 수 시각화"""
    logger.info("제품 수 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/product-count"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "전체 제품 수",
            "visState": json.dumps({
                "title": "전체 제품 수",
                "type": "metric",
                "params": {
                    "metric": {
                        "colorSchema": "Green to Red",
                        "style": {
                            "fontSize": 60
                        }
                    }
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "건강기능식품 전체 제품 수",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": ES_INDEX,
                    "query": {"query": "", "language": "lucene"}
                })
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:
            logger.info("✓ 제품 수 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_category_pie():
    """카테고리별 분포 파이차트"""
    logger.info("카테고리 분포 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/category-distribution"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "카테고리별 제품 분포",
            "visState": json.dumps({
                "title": "카테고리별 제품 분포",
                "type": "pie",
                "params": {
                    "type": "pie",
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "isDonut": True
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "classification.category",  # keyword 타입
                            "size": 15,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "제품 카테고리별 분포",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": ES_INDEX,
                    "query": {"query": "", "language": "lucene"}
                })
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:
            logger.info("✓ 카테고리 분포 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_company_ranking():
    """회사별 제품 수 랭킹 TOP 20"""
    logger.info("회사별 제품 수 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/company-ranking"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "제조사별 제품 수 TOP 20",
            "visState": json.dumps({
                "title": "제조사별 제품 수 TOP 20",
                "type": "horizontal_bar",
                "params": {
                    "type": "histogram",
                    "grid": {"categoryLines": False},
                    "categoryAxes": [{
                        "id": "CategoryAxis-1",
                        "type": "category",
                        "position": "left",
                        "show": True,
                        "style": {},
                        "scale": {"type": "linear"},
                        "labels": {"show": True, "rotate": 0}
                    }],
                    "valueAxes": [{
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "bottom",
                        "show": True,
                        "style": {},
                        "scale": {"type": "linear", "mode": "normal"}
                    }]
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "company_name.keyword",  # keyword 서브필드 사용
                            "size": 20,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "제조사별 제품 수 상위 20개",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": ES_INDEX,
                    "query": {"query": "", "language": "lucene"}
                })
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:
            logger.info("✓ 회사별 제품 수 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_function_content():
    """기능성 내용별 분포"""
    logger.info("기능성 내용 분포 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/function-content-distribution"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "기능성 내용별 제품 분포",
            "visState": json.dumps({
                "title": "기능성 내용별 제품 분포",
                "type": "pie",
                "params": {
                    "type": "pie",
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "isDonut": True,
                    "labels": {
                        "show": True,
                        "values": True,
                        "last_level": True,
                        "truncate": 100
                    }
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "classification.function_content.keyword",  # keyword 서브필드
                            "size": 20,
                            "order": "desc",
                            "orderBy": "1",
                            "customLabel": "기능성 내용"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "제품의 기능성 내용별 분포 (도넛 차트)",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": ES_INDEX,
                    "query": {"query": "", "language": "lucene"}
                })
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:
            logger.info("✓ 기능성 내용 분포 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_product_shape():
    """제품 형태별 분포"""
    logger.info("제품 형태 분포 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/product-shape-distribution"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "제품 형태별 분포",
            "visState": json.dumps({
                "title": "제품 형태별 분포",
                "type": "pie",
                "params": {
                    "type": "pie",
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "isDonut": False
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "product_shape.keyword",  # keyword 서브필드
                            "size": 15,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "제품 형태(정제, 캡슐, 분말 등)별 분포",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": ES_INDEX,
                    "query": {"query": "", "language": "lucene"}
                })
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:
            logger.info("✓ 제품 형태 분포 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_ingredient_count():
    """원재료 수 분포"""
    logger.info("원재료 수 분포 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/ingredient-count-histogram"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "원재료 수 분포",
            "visState": json.dumps({
                "title": "원재료 수 분포",
                "type": "histogram",
                "params": {
                    "type": "histogram",
                    "grid": {"categoryLines": False},
                    "categoryAxes": [{
                        "id": "CategoryAxis-1",
                        "type": "category",
                        "position": "bottom",
                        "show": True,
                        "labels": {"show": True, "rotate": 0}
                    }],
                    "valueAxes": [{
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "left",
                        "show": True
                    }],
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right"
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "histogram",
                        "schema": "segment",
                        "params": {
                            "field": "ingredient_count",  # integer 타입
                            "interval": 1,
                            "min_doc_count": 1
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "제품별 원재료 개수 분포",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": ES_INDEX,
                    "query": {"query": "", "language": "lucene"}
                })
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:
            logger.info("✓ 원재료 수 분포 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_detail_category():
    """세부 카테고리 분포"""
    logger.info("세부 카테고리 분포 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/detail-category-bar"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "세부 카테고리 TOP 15",
            "visState": json.dumps({
                "title": "세부 카테고리 TOP 15",
                "type": "horizontal_bar",
                "params": {
                    "type": "histogram",
                    "grid": {"categoryLines": False},
                    "categoryAxes": [{
                        "id": "CategoryAxis-1",
                        "type": "category",
                        "position": "left",
                        "show": True,
                        "labels": {"show": True, "rotate": 0}
                    }],
                    "valueAxes": [{
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "bottom",
                        "show": True
                    }],
                    "addTooltip": True,
                    "addLegend": False
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "classification.detail_category",  # keyword 타입
                            "size": 15,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "세부 카테고리별 제품 수 상위 15개",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": ES_INDEX,
                    "query": {"query": "", "language": "lucene"}
                })
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:
            logger.info("✓ 세부 카테고리 분포 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def main():
    """메인 함수"""
    logger.info("=" * 80)
    logger.info("Kibana 대시보드 설정 시작 (수정 버전)")
    logger.info("=" * 80)

    # Kibana 연결 대기
    if not wait_for_kibana():
        logger.error("Kibana 서버에 연결할 수 없어 설정을 중단합니다.")
        return

    # 인덱스 패턴 생성
    create_index_pattern()

    # 시각화 생성
    logger.info("\n📊 시각화 생성 중...")
    create_visualization_product_count()
    create_visualization_category_pie()
    create_visualization_company_ranking()
    create_visualization_function_content()
    create_visualization_product_shape()
    create_visualization_ingredient_count()
    create_visualization_detail_category()

    logger.info("\n" + "=" * 80)
    logger.info("✓ Kibana 대시보드 설정 완료!")
    logger.info("=" * 80)
    logger.info("\n📍 다음 단계:")
    logger.info("  1. Kibana 접속: http://localhost:5601")
    logger.info("  2. Visualize Library에서 생성된 시각화 확인")
    logger.info("  3. Dashboard 메뉴에서 새 대시보드 생성")
    logger.info("  4. 시각화들을 드래그하여 대시보드에 추가")
    logger.info("\n📊 생성된 시각화:")
    logger.info("  - 전체 제품 수 (Metric)")
    logger.info("  - 카테고리별 제품 분포 (Donut Chart)")
    logger.info("  - 제조사별 제품 수 TOP 20 (Horizontal Bar)")
    logger.info("  - 기능성 내용별 분포 (Donut Chart)")
    logger.info("  - 제품 형태별 분포 (Pie Chart)")
    logger.info("  - 원재료 수 분포 (Histogram)")
    logger.info("  - 세부 카테고리 TOP 15 (Horizontal Bar)")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()

"""
Kibana 대시보드 설정 스크립트
건강기능식품 데이터 시각화를 위한 인덱스 패턴 및 대시보드 생성
현재 구성된 대시보드 기준으로 재생성
"""
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
    """인덱스 패턴 생성"""
    logger.info("인덱스 패턴 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/index-pattern/{ES_INDEX}"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": f"{ES_INDEX}*",
            "timeFieldName": "report_date"
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
    """전체 제품 수 시각화 생성"""
    logger.info("전체 제품 수 시각화 생성 중...")

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
            logger.info("✓ 전체 제품 수 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_company_ranking():
    """제조사별 제품 수 TOP 20 시각화 생성"""
    logger.info("제조사별 제품 수 TOP 20 시각화 생성 중...")

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
                        "labels": {"show": True, "rotate": 0}
                    }],
                    "valueAxes": [{
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "bottom",
                        "show": True
                    }],
                    "seriesParams": [{
                        "show": True,
                        "type": "histogram",
                        "mode": "normal",
                        "data": {"label": "제품 수", "id": "1"}
                    }],
                    "addTooltip": True,
                    "addLegend": False,
                    "legendPosition": "right"
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {"customLabel": "제품 수"}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "company_name.keyword",
                            "size": 20,
                            "order": "desc",
                            "orderBy": "1",
                            "customLabel": "제조사"
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
            logger.info("✓ 제조사별 제품 수 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_product_shape():
    """제품 형태별 분포 시각화 생성"""
    logger.info("제품 형태별 분포 시각화 생성 중...")

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
                            "field": "product_shape.keyword",
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
            logger.info("✓ 제품 형태별 분포 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_visualization_ingredient_count():
    """원재료 수 분포 시각화 생성"""
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
                            "field": "ingredient_count",
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

def create_visualization_monthly_trend():
    """월별 제품 등록 추이 시각화 생성"""
    logger.info("월별 제품 등록 추이 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/monthly-product-trend"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "월별 제품 등록 추이",
            "visState": json.dumps({
                "title": "월별 제품 등록 추이",
                "type": "line",
                "params": {
                    "type": "line",
                    "grid": {"categoryLines": False},
                    "categoryAxes": [{
                        "id": "CategoryAxis-1",
                        "type": "category",
                        "position": "bottom",
                        "show": True,
                        "labels": {"show": True, "rotate": 45}
                    }],
                    "valueAxes": [{
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "left",
                        "show": True
                    }],
                    "seriesParams": [{
                        "show": True,
                        "type": "line",
                        "mode": "normal",
                        "data": {"label": "등록 제품 수", "id": "1"},
                        "drawLinesBetweenPoints": True,
                        "showCircles": True,
                        "interpolate": "linear"
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
                        "params": {"customLabel": "등록 제품 수"}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "date_histogram",
                        "schema": "segment",
                        "params": {
                            "field": "report_date",
                            "interval": "monthly",
                            "customLabel": "등록 월",
                            "min_doc_count": 1
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "월별 신규 제품 등록 추이",
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
            logger.info("✓ 월별 제품 등록 추이 시각화 생성 완료")
            return True
        else:
            logger.warning(f"시각화 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"시각화 생성 오류: {e}")
        return False

def create_saved_search():
    """최근 등록 제품 검색 생성"""
    logger.info("최근 등록 제품 검색 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/search/recent-products"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "최근 등록 제품",
            "description": "최근 30일 내 등록된 제품",
            "columns": [
                "product_name",
                "company_name",
                "report_date",
                "raw_materials",
                "ingredient_count",
                "intake_info.caution",
                "intake_info.method",
                "product_details.shelf_life"
            ],
            "sort": [["report_date", "desc"]],
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": ES_INDEX,
                    "query": {"query": "", "language": "lucene"},
                    "filter": []
                })
            }
        },
        "references": [
            {
                "id": ES_INDEX,
                "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
                "type": "index-pattern"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:
            logger.info("✓ 최근 등록 제품 검색 생성 완료")
            return True
        else:
            logger.warning(f"검색 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"검색 생성 오류: {e}")
        return False

def main():
    """메인 함수"""
    logger.info("=" * 80)
    logger.info("Kibana 대시보드 설정 시작")
    logger.info("=" * 80)

    # Kibana 연결 대기
    if not wait_for_kibana():
        logger.error("Kibana 서버에 연결할 수 없어 설정을 중단합니다.")
        return

    # 인덱스 패턴 생성
    create_index_pattern()

    # 시각화 생성
    create_visualization_product_count()
    create_visualization_company_ranking()
    create_visualization_product_shape()
    create_visualization_ingredient_count()
    create_visualization_monthly_trend()

    # 저장된 검색 생성
    create_saved_search()

    logger.info("=" * 80)
    logger.info("✓ Kibana 대시보드 설정 완료!")
    logger.info("Kibana 대시보드: http://localhost:5601")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📌 생성된 시각화:")
    logger.info("  - 전체 제품 수 (Metric)")
    logger.info("  - 제조사별 제품 수 TOP 20 (Horizontal Bar)")
    logger.info("  - 제품 형태별 분포 (Pie Chart)")
    logger.info("  - 원재료 수 분포 (Histogram)")
    logger.info("  - 월별 제품 등록 추이 (Line Chart)")
    logger.info("  - 최근 등록 제품 (Saved Search)")
    logger.info("")
    logger.info("💡 Kibana UI에서 이 시각화들을 조합하여 대시보드를 구성할 수 있습니다.")

if __name__ == "__main__":
    main()

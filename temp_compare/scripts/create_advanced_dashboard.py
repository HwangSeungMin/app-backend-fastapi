# -*- coding: utf-8 -*-
"""
고급 Kibana 대시보드 자동 생성 스크립트
health_supplements 인덱스 기반으로 상세한 대시보드 구축
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.encoding_fix import ensure_utf8
ensure_utf8()

import requests
import json
import time
from utils.logger import get_logger

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
        except Exception:
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
        if response.status_code in [200, 409]:
            logger.info("✓ 인덱스 패턴 생성 완료")
            return True
        else:
            logger.error(f"인덱스 패턴 생성 실패: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"인덱스 패턴 생성 오류: {e}")
        return False

def create_saved_search():
    """저장된 검색 쿼리 생성"""
    logger.info("저장된 검색 생성 중...")

    searches = [
        {
            "id": "recent-products",
            "title": "최근 등록 제품",
            "description": "최근 30일 내 등록된 제품",
            "columns": ["product_name", "company_name", "classification.category", "report_date"],
            "sort": [["report_date", "desc"]]
        }
    ]

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    for search in searches:
        url = f"{KIBANA_URL}/api/saved_objects/search/{search['id']}"

        data = {
            "attributes": {
                "title": search["title"],
                "description": search.get("description", ""),
                "columns": search["columns"],
                "sort": search["sort"],
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "index": ES_INDEX,
                        "query": {"query": "", "language": "lucene"},
                        "filter": []
                    })
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 409]:
                logger.info(f"✓ 저장된 검색 '{search['title']}' 생성 완료")
        except Exception as e:
            logger.warning(f"저장된 검색 생성 실패: {e}")

def create_visualization_company_ranking():
    """제조사별 제품 수 TOP 20 시각화"""
    logger.info("제조사 랭킹 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/company-ranking-top20"
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
            logger.info("✓ 제조사 랭킹 시각화 생성 완료")
            return True
    except Exception as e:
        logger.warning(f"시각화 생성 실패: {e}")
    return False

def create_visualization_monthly_trend():
    """월별 제품 등록 추이 시각화"""
    logger.info("월별 추이 시각화 생성 중...")

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
            logger.info("✓ 월별 추이 시각화 생성 완료")
            return True
    except Exception as e:
        logger.warning(f"시각화 생성 실패: {e}")
    return False

def create_visualization_function_content():
    """기능성 내용별 분포 시각화"""
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
                            "field": "classification.function_content.keyword",
                            "size": 15,
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
    except Exception as e:
        logger.warning(f"시각화 생성 실패: {e}")
    return False

def create_visualization_detail_category_tree():
    """세부 카테고리 트리맵 시각화"""
    logger.info("세부 카테고리 트리맵 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/detail-category-treemap"
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "세부 카테고리 트리맵",
            "visState": json.dumps({
                "title": "세부 카테고리 트리맵",
                "type": "heatmap",
                "params": {
                    "addTooltip": True,
                    "addLegend": True,
                    "enableHover": True,
                    "legendPosition": "right",
                    "times": [],
                    "colorsNumber": 4,
                    "colorSchema": "Blues",
                    "setColorRange": False,
                    "percentageMode": False,
                    "invertColors": False,
                    "colorsRange": []
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
                            "field": "classification.category.keyword",
                            "size": 10,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    },
                    {
                        "id": "3",
                        "enabled": True,
                        "type": "terms",
                        "schema": "group",
                        "params": {
                            "field": "classification.detail_category.keyword",
                            "size": 10,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "카테고리 > 세부 카테고리 계층 구조",
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
            logger.info("✓ 세부 카테고리 트리맵 생성 완료")
            return True
    except Exception as e:
        logger.warning(f"시각화 생성 실패: {e}")
    return False

def print_summary():
    """완료 요약 출력"""
    print("\n" + "=" * 80)
    print("Kibana 대시보드 생성 완료!")
    print("=" * 80)
    print("\n📊 생성된 시각화:")
    print("  1. ✓ 전체 제품 수 (Metric)")
    print("  2. ✓ 카테고리별 분포 (Pie Chart)")
    print("  3. ✓ 제조사 랭킹 TOP 20 (Horizontal Bar)")
    print("  4. ✓ 월별 제품 등록 추이 (Line Chart)")
    print("  5. ✓ 기능성 내용 분포 (Donut Chart)")
    print("  6. ✓ 세부 카테고리 히트맵 (Heatmap)")
    print("\n📍 다음 단계:")
    print("  1. Kibana 접속: http://localhost:5601")
    print("  2. Visualize Library에서 생성된 시각화 확인")
    print("  3. Dashboard 메뉴에서 새 대시보드 생성")
    print("  4. 시각화들을 드래그하여 대시보드에 추가")
    print("\n💡 팁:")
    print("  - Lens를 사용하면 더 쉽게 시각화 생성 가능")
    print("  - Controls를 추가하여 대화형 필터 구현")
    print("  - Markdown 위젯으로 설명 추가")
    print("\n📖 자세한 가이드: docs/KIBANA_DASHBOARD_EXAMPLES.md")
    print("=" * 80 + "\n")

def main():
    """메인 함수"""
    logger.info("=" * 80)
    logger.info("고급 Kibana 대시보드 자동 생성 시작")
    logger.info("=" * 80)

    # Kibana 연결 대기
    if not wait_for_kibana():
        logger.error("Kibana 서버에 연결할 수 없어 설정을 중단합니다.")
        return

    # 인덱스 패턴 생성
    create_index_pattern()

    # 저장된 검색 생성
    create_saved_search()

    # 시각화 생성
    from scripts.setup_kibana_dashboard import (
        create_visualization_product_count,
        create_visualization_category_pie
    )

    create_visualization_product_count()
    create_visualization_category_pie()
    create_visualization_company_ranking()
    create_visualization_monthly_trend()
    create_visualization_function_content()
    create_visualization_detail_category_tree()

    # 완료 메시지
    print_summary()

if __name__ == "__main__":
    main()

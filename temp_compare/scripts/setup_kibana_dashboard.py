"""
Kibana 대시보드 설정 스크립트
건강기능식품 데이터 시각화를 위한 인덱스 패턴 및 대시보드 생성
"""
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
            "timeFieldName": "metadata.update_date"
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
    """제품 수 시각화 생성"""
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
    """카테고리별 분포 파이차트 생성"""
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
                            "field": "classification.category.keyword",
                            "size": 10,
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
    """회사별 제품 수 랭킹 생성"""
    logger.info("회사별 제품 수 시각화 생성 중...")

    url = f"{KIBANA_URL}/api/saved_objects/visualization/company-ranking"

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    data = {
        "attributes": {
            "title": "제조사별 제품 수 TOP 10",
            "visState": json.dumps({
                "title": "제조사별 제품 수 TOP 10",
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
                            "field": "company_name.keyword",
                            "size": 10,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "description": "제조사별 제품 수 상위 10개",
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
    create_visualization_category_pie()
    create_visualization_company_ranking()

    logger.info("=" * 80)
    logger.info("✓ Kibana 대시보드 설정 완료!")
    logger.info("Kibana 대시보드: http://localhost:5601")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()

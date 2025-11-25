"""
식약처 추가 API 데이터 수집 스크립트

I0030: 기능성 원료
I2790: 영업신고
I0040: 부작용 정보
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.api_client import FoodSafetyAPIClient
from utils.logger import get_logger
import json

logger = get_logger(__name__)


def collect_additional_data(max_items: int = 100):
    """추가 API 데이터 수집"""
    
    logger.info("=== 추가 API 데이터 수집 시작 ===")
    
    client = FoodSafetyAPIClient()
    
    # 추가 데이터 수집
    result = client.collect_all_data(
        max_items=max_items,
        include_additional=True
    )
    
    # 결과 저장
    output_dir = "data/raw"
    os.makedirs(output_dir, exist_ok=True)
    
    # 기능성 원료 저장
    if result['ingredients']:
        with open(f"{output_dir}/functional_ingredients.json", 'w', encoding='utf-8') as f:
            json.dump(result['ingredients'], f, ensure_ascii=False, indent=2)
        logger.info(f"기능성 원료 데이터 저장: {len(result['ingredients'])}개")
    
    # 영업신고 저장
    if result['businesses']:
        with open(f"{output_dir}/business_registration.json", 'w', encoding='utf-8') as f:
            json.dump(result['businesses'], f, ensure_ascii=False, indent=2)
        logger.info(f"영업신고 데이터 저장: {len(result['businesses'])}개")
    
    # 부작용 정보 저장
    if result['side_effects']:
        with open(f"{output_dir}/side_effects.json", 'w', encoding='utf-8') as f:
            json.dump(result['side_effects'], f, ensure_ascii=False, indent=2)
        logger.info(f"부작용 정보 데이터 저장: {len(result['side_effects'])}개")
    
    logger.info("=== 추가 API 데이터 수집 완료 ===")
    
    return result


def analyze_ingredient_data(ingredients: list):
    """기능성 원료 데이터 분석"""
    
    logger.info("\n=== 기능성 원료 데이터 분석 ===")
    
    if not ingredients:
        logger.warning("데이터가 없습니다.")
        return
    
    # 샘플 데이터 출력
    logger.info(f"총 {len(ingredients)}개 원료")
    logger.info("\n샘플 데이터:")
    
    for i, item in enumerate(ingredients[:3], 1):
        logger.info(f"\n[{i}] {item.get('PRDLST_NM', 'N/A')}")
        logger.info(f"  - 기능성 내용: {item.get('FNCLTY_CN', 'N/A')[:50]}...")
        logger.info(f"  - 일일섭취량: {item.get('DAILY_INTK_CN', 'N/A')}")


def analyze_business_data(businesses: list):
    """영업신고 데이터 분석"""
    
    logger.info("\n=== 영업신고 데이터 분석 ===")
    
    if not businesses:
        logger.warning("데이터가 없습니다.")
        return
    
    logger.info(f"총 {len(businesses)}개 업체")
    logger.info("\n샘플 데이터:")
    
    for i, item in enumerate(businesses[:3], 1):
        logger.info(f"\n[{i}] {item.get('BSSH_NM', 'N/A')}")
        logger.info(f"  - 소재지: {item.get('SITE_ADDR', 'N/A')}")
        logger.info(f"  - 영업 종류: {item.get('BIZ_STTS_NM', 'N/A')}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="식약처 추가 API 데이터 수집")
    parser.add_argument(
        "--max-items",
        type=int,
        default=100,
        help="수집할 최대 아이템 수 (기본: 100)"
    )
    
    args = parser.parse_args()
    
    try:
        result = collect_additional_data(max_items=args.max_items)
        
        # 데이터 분석
        analyze_ingredient_data(result['ingredients'])
        analyze_business_data(result['businesses'])
        
        logger.info("\n✓ 데이터 수집 및 분석 완료")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        sys.exit(1)

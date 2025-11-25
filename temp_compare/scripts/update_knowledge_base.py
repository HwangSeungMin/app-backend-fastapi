"""
Knowledge Base 업데이트 스크립트

FAQ 데이터셋을 로드하여 utils/knowledge_base.py의 DEFAULT_RECOMMENDATIONS를 업데이트합니다.
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.load_faq_data import load_faq_dataset, generate_knowledge_base_dict
from utils.logger import get_logger
import argparse

logger = get_logger(__name__)


def update_knowledge_base(csv_path: str, output_path: str = None):
    """
    FAQ 데이터를 로드하여 knowledge_base.py 업데이트
    
    Args:
        csv_path: FAQ CSV 파일 경로
        output_path: 출력 파일 경로 (기본값: utils/knowledge_base.py)
    """
    
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'utils', 
            'knowledge_base.py'
        )
    
    logger.info("=" * 60)
    logger.info("Knowledge Base 업데이트 시작")
    logger.info("=" * 60)
    
    # 1. FAQ 데이터 로드
    logger.info(f"\n[1단계] FAQ 데이터 로드: {csv_path}")
    faq_data = load_faq_dataset(csv_path)
    
    # 2. Knowledge Base 형식으로 변환
    logger.info("\n[2단계] Knowledge Base 형식으로 변환")
    kb_dict = generate_knowledge_base_dict(faq_data)
    
    # 3. 기존 파일 백업
    logger.info(f"\n[3단계] 기존 파일 백업: {output_path}.backup")
    if os.path.exists(output_path):
        import shutil
        shutil.copy2(output_path, f"{output_path}.backup")
    
    # 4. 새로운 knowledge_base.py 생성
    logger.info(f"\n[4단계] 새로운 knowledge_base.py 생성")
    
    # Python 코드 생성
    code_lines = []
    code_lines.append('"""')
    code_lines.append('건강기능식품 도메인 지식 베이스')
    code_lines.append('')
    code_lines.append('증상-영양소 매핑, 성분 상호작용, 복용 시간 가이드 등')
    code_lines.append('도메인 전문 지식을 제공합니다.')
    code_lines.append('')
    code_lines.append('※ 이 파일은 scripts/update_knowledge_base.py에 의해 자동 생성되었습니다.')
    code_lines.append('"""')
    code_lines.append('from typing import Dict, List, Optional')
    code_lines.append('from utils.logger import get_logger')
    code_lines.append('')
    code_lines.append('logger = get_logger(__name__)')
    code_lines.append('')
    code_lines.append('')
    code_lines.append('class HealthKnowledgeBase:')
    code_lines.append('    """건강기능식품 지식 베이스"""')
    code_lines.append('    ')
    
    # DEFAULT_RECOMMENDATIONS 생성
    code_lines.append('    # FAQ 데이터셋 기반 기본 추천')
    code_lines.append('    DEFAULT_RECOMMENDATIONS = {')
    
    for symptom, data in sorted(kb_dict.items()):
        code_lines.append(f'        "{symptom}": {{')
        code_lines.append(f'            "products": {data["products"]},')
        code_lines.append(f'            "message": """{data["message"]}""",')
        code_lines.append(f'            "tips": {data["tips"]},')
        code_lines.append(f'            "faqs": [')
        for faq in data["faqs"]:
            code_lines.append(f'                {{')
            code_lines.append(f'                    "question": """{faq["question"]}""",')
            code_lines.append(f'                    "answer": """{faq["answer"]}"""')
            code_lines.append(f'                }},')
        code_lines.append(f'            ]')
        code_lines.append(f'        }},')
    
    code_lines.append('    }')
    code_lines.append('    ')
    
    # 나머지 메서드들 추가 (기존 코드 유지)
    code_lines.extend([
        '    def __init__(self):',
        '        logger.info("건강기능식품 지식 베이스 초기화")',
        '    ',
        '    def get_default_recommendation(self, query: str) -> Optional[Dict]:',
        '        """기본 추천 조회"""',
        '        for category, info in self.DEFAULT_RECOMMENDATIONS.items():',
        '            if any(keyword in query for keyword in category.split("/")):'
        '                return {',
        '                    "category": category,',
        '                    **info',
        '                }',
        '        return None',
        '    ',
        '    def get_all_symptom_keywords(self) -> List[str]:',
        '        """모든 증상 키워드 목록"""',
        '        keywords = []',
        '        for category in self.DEFAULT_RECOMMENDATIONS.keys():',
        '            keywords.extend(category.split("/"))',
        '        return list(set(keywords))',
        '    ',
        '    def get_all_ingredients(self) -> List[str]:',
        '        """모든 성분 목록"""',
        '        ingredients = set()',
        '        for info in self.DEFAULT_RECOMMENDATIONS.values():',
        '            ingredients.update(info["products"])',
        '        return list(ingredients)',
        ''
    ])
    
    # 파일 쓰기
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(code_lines))
    
    logger.info(f"✓ 파일 생성 완료: {output_path}")
    logger.info(f"✓ 총 {len(kb_dict)}개 증상 카테고리 추가")
    
    logger.info("\n" + "=" * 60)
    logger.info("Knowledge Base 업데이트 완료!")
    logger.info("=" * 60)
    logger.info("\n서버를 재시작하면 새로운 데이터가 적용됩니다.")


def main():
    parser = argparse.ArgumentParser(description='FAQ 데이터셋으로 Knowledge Base 업데이트')
    parser.add_argument('--csv-path', type=str, default='data/faq_dataset_300.csv',
                       help='FAQ CSV 파일 경로')
    parser.add_argument('--output', type=str, default=None,
                       help='출력 파일 경로 (기본값: utils/knowledge_base.py)')
    
    args = parser.parse_args()
    
    try:
        update_knowledge_base(args.csv_path, args.output)
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

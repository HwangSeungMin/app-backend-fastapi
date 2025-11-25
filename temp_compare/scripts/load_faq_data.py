"""
FAQ 데이터셋 로더

CSV 파일에서 FAQ 데이터를 로드하고 증상별로 그룹화합니다.
"""
import csv
from collections import defaultdict
from typing import Dict, List, Set
from utils.logger import get_logger

logger = get_logger(__name__)


def load_faq_dataset(csv_path: str) -> Dict:
    """
    CSV 파일에서 FAQ 데이터 로드 및 증상별 그룹화
    
    Args:
        csv_path: CSV 파일 경로
        
    Returns:
        증상별로 그룹화된 FAQ 데이터
    """
    
    logger.info(f"FAQ 데이터 로드 시작: {csv_path}")
    
    faq_data = defaultdict(lambda: {
        'questions': [],
        'answers': [],
        'supplements': set(),
        'actions': set()
    })
    
    total_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                symptom = row['symptom'].strip()
                question = row['question'].strip()
                answer = row['answer'].strip()
                
                # 질문과 답변 추가
                faq_data[symptom]['questions'].append(question)
                faq_data[symptom]['answers'].append(answer)
                
                # 영양제 파싱 (쉼표로 구분)
                if row['recommend_supplement']:
                    supplements = [s.strip() for s in row['recommend_supplement'].split(',')]
                    faq_data[symptom]['supplements'].update(supplements)
                
                # 행동 파싱 (쉼표로 구분)
                if row['recommend_action']:
                    actions = [a.strip() for a in row['recommend_action'].split(',')]
                    faq_data[symptom]['actions'].update(actions)
                
                total_count += 1
        
        # set을 list로 변환
        for symptom in faq_data:
            faq_data[symptom]['supplements'] = sorted(list(faq_data[symptom]['supplements']))
            faq_data[symptom]['actions'] = sorted(list(faq_data[symptom]['actions']))
        
        logger.info(f"FAQ 데이터 로드 완료: {total_count}개 항목, {len(faq_data)}개 증상 카테고리")
        
        # 통계 출력
        for symptom, data in faq_data.items():
            logger.info(f"  - {symptom}: {len(data['questions'])}개 질문, "
                       f"{len(data['supplements'])}개 영양제, {len(data['actions'])}개 행동")
        
        return dict(faq_data)
        
    except FileNotFoundError:
        logger.error(f"파일을 찾을 수 없습니다: {csv_path}")
        raise
    except Exception as e:
        logger.error(f"FAQ 데이터 로드 오류: {e}")
        raise


def generate_knowledge_base_dict(faq_data: Dict) -> Dict:
    """
    FAQ 데이터를 Knowledge Base 형식으로 변환
    
    Args:
        faq_data: load_faq_dataset에서 반환된 데이터
        
    Returns:
        DEFAULT_RECOMMENDATIONS 형식의 딕셔너리
    """
    
    knowledge_base = {}
    
    for symptom, data in faq_data.items():
        # 대표 답변 선택 (첫 번째 답변)
        representative_answer = data['answers'][0] if data['answers'] else ""
        
        # FAQ 리스트 생성 (최대 5개)
        faqs = []
        for i, (q, a) in enumerate(zip(data['questions'], data['answers'])):
            if i >= 5:  # 최대 5개만
                break
            faqs.append({
                "question": q,
                "answer": a
            })
        
        knowledge_base[symptom] = {
            "products": data['supplements'],
            "message": representative_answer,
            "tips": data['actions'],
            "faqs": faqs
        }
    
    return knowledge_base


if __name__ == "__main__":
    # 테스트
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    csv_path = "data/faq_dataset_300.csv"
    
    # 데이터 로드
    faq_data = load_faq_dataset(csv_path)
    
    # Knowledge Base 형식으로 변환
    kb_dict = generate_knowledge_base_dict(faq_data)
    
    # 샘플 출력
    print("\n=== 샘플 데이터 (피로감) ===")
    if "피로감" in kb_dict:
        import json
        print(json.dumps(kb_dict["피로감"], ensure_ascii=False, indent=2))

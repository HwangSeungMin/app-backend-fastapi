"""
쿼리 분석기 (Query Analyzer)

사용자 쿼리를 분석하여 개체명, 의도, 확장 키워드를 추출합니다.
규칙 기반 방식으로 구현되어 있으며, 필요시 NER 모델로 확장 가능합니다.
"""
from typing import Dict, List, Set, Optional
from app.utils.knowledge_base import HealthKnowledgeBase
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EntityExtractor:
    """개체명 추출기 (규칙 기반)"""
    
    def __init__(self, knowledge_base: HealthKnowledgeBase):
        self.kb = knowledge_base
        
        # 증상 키워드
        self.symptom_keywords = self.kb.get_all_symptom_keywords()
        
        # 성분 키워드
        self.ingredient_keywords = self.kb.get_all_ingredients()
        
        # 신체 부위 키워드
        self.body_parts = [
            "눈", "귀", "코", "입", "목", "어깨", "팔", "손", "손목", "손가락",
            "가슴", "배", "허리", "등", "엉덩이", "다리", "무릎", "발", "발목",
            "머리", "뇌", "심장", "간", "위", "장", "신장", "폐", "피부", "뼈", "관절"
        ]
        
        logger.info("개체명 추출기 초기화 완료")
    
    def extract(self, query: str) -> Dict[str, List[str]]:
        """쿼리에서 개체명 추출 (중복 매칭 방지 적용)"""
        
        entities = {
            "symptoms": [],
            "ingredients": [],
            "body_parts": [],
            "effects": []
        }
        
        # 매칭된 영역을 마킹하기 위한 마스크 (True: 이미 매칭됨)
        matched_mask = [False] * len(query)
        
        # 모든 키워드를 카테고리와 함께 리스트로 구성
        # (키워드, 카테고리) 튜플 리스트
        all_keywords = []
        for k in self.symptom_keywords: all_keywords.append((k, "symptoms"))
        for k in self.ingredient_keywords: all_keywords.append((k, "ingredients"))
        for k in self.body_parts: all_keywords.append((k, "body_parts"))
        
        effect_keywords = ["개선", "완화", "예방", "강화", "증진", "회복", "보호", "유지"]
        for k in effect_keywords: all_keywords.append((k, "effects"))
        
        # 길이 긴 순서대로 정렬 (긴 단어 우선 매칭)
        all_keywords.sort(key=lambda x: len(x[0]), reverse=True)
        
        # 매칭 수행
        for keyword, category in all_keywords:
            start_idx = 0
            while True:
                idx = query.find(keyword, start_idx)
                if idx == -1:
                    break
                
                end_idx = idx + len(keyword)
                
                # 이미 매칭된 영역과 겹치는지 확인
                # 하나라도 겹치면 스킵 (긴 단어가 이미 차지함)
                is_overlapped = any(matched_mask[i] for i in range(idx, end_idx))
                
                if not is_overlapped:
                    # 유효한 매칭으로 인정
                    entities[category].append(keyword)
                    # 마스크 업데이트
                    for i in range(idx, end_idx):
                        matched_mask[i] = True
                
                start_idx = idx + 1
        
        # 중복 제거
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        logger.debug(f"추출된 개체명: {entities}")
        
        return entities


class IntentClassifier:
    """의도 분류기"""
    
    # 의도별 키워드
    INTENT_KEYWORDS = {
        "SYMPTOM_SEARCH": ["아프", "통증", "불편", "힘들", "괴롭", "고통"],
        "INGREDIENT_SEARCH": ["성분", "함유", "포함", "들어있", "함량", "원료"],
        "TIMING_QUERY": ["언제", "시간", "타이밍", "먹", "복용", "섭취"],
        "EFFECT_QUERY": ["효과", "효능", "도움", "좋", "개선"],
        "PRODUCT_SEARCH": ["제품", "상품", "브랜드", "회사"]
    }
    
    def __init__(self):
        logger.info("의도 분류기 초기화 완료")
    
    def classify(self, query: str, entities: Dict) -> str:
        """쿼리 의도 분류"""
        
        scores = {intent: 0 for intent in self.INTENT_KEYWORDS.keys()}
        
        # 키워드 기반 점수 계산
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    scores[intent] += 1
        
        # 개체명 기반 추가 점수
        if entities["ingredients"]:
            scores["INGREDIENT_SEARCH"] += 2
        
        if entities["symptoms"] or entities["body_parts"]:
            scores["SYMPTOM_SEARCH"] += 2
        
        # 최고 점수 의도 선택
        max_score = max(scores.values())
        
        if max_score == 0:
            return "GENERAL_SEARCH"
        
        # 복합 의도 감지
        high_score_intents = [intent for intent, score in scores.items() if score >= max_score - 1]
        
        if len(high_score_intents) > 1:
            return "MIXED"
        
        intent = max(scores.items(), key=lambda x: x[1])[0]
        
        logger.debug(f"분류된 의도: {intent} (점수: {scores})")
        
        return intent


class QueryExpander:
    """쿼리 확장기 (동의어/유사어) - 강화 버전"""
    
    # 확장된 동의어 맵
    SYNONYM_MAP = {
        # 증상 관련
        "피로": ["피곤", "지침", "무기력", "기력저하", "활력저하", "에너지부족"],
        "관절": ["무릎", "팔꿈치", "손목", "발목", "뼈마디", "관절통"],
        "면역": ["면역력", "저항력", "방어력", "면역체계"],
        "눈": ["시력", "안구", "눈건강", "시야", "안구건조", "눈피로"],
        "소화": ["장", "위", "배", "소화기", "소화불량", "위장"],
        "피부": ["피부건강", "미용", "탄력", "피부미용", "주름"],
        "기억력": ["집중력", "두뇌", "인지기능", "기억", "치매예방"],
        "혈액순환": ["혈행", "순환", "혈류", "혈액순환개선"],
        "뼈": ["골밀도", "골다공증", "뼈건강", "골격"],
        "간": ["간기능", "간건강", "해독", "간보호"],
        "혈당": ["당뇨", "혈당조절", "인슐린", "당수치"],
        "콜레스테롤": ["고지혈증", "혈중지질", "중성지방"],
        "스트레스": ["긴장", "불안", "우울", "심리"],
        "수면": ["불면증", "잠", "숙면", "수면장애"],
        "변비": ["배변", "장운동", "변통"],
        
        # 성분 동의어 (확장)
        "비타민C": ["아스코르브산", "비타민씨", "비타민c", "Vitamin C"],
        "비타민D": ["비타민디", "비타민d", "Vitamin D", "칼시페롤"],
        "비타민B": ["비타민비", "비타민b", "Vitamin B", "비타민B군"],
        "비타민B1": ["티아민", "Thiamine"],
        "비타민B2": ["리보플라빈", "Riboflavin"],
        "비타민B6": ["피리독신", "Pyridoxine"],
        "비타민B12": ["코발라민", "Cobalamin"],
        "비타민E": ["토코페롤", "Vitamin E"],
        "비타민A": ["레티놀", "Vitamin A"],
        "비타민K": ["Vitamin K", "나프토퀴논"],
        
        "오메가3": ["EPA", "DHA", "불포화지방산", "오메가-3", "omega3"],
        "프로바이오틱스": ["유산균", "락토바실러스", "비피더스균", "probiotics"],
        "루테인": ["지아잔틴", "Lutein", "제아잔틴"],
        "칼슘": ["Ca", "칼슘제", "Calcium"],
        "마그네슘": ["Mg", "마그네슘제", "Magnesium"],
        "철분": ["Fe", "철", "Iron", "헤모글로빈"],
        "아연": ["Zn", "Zinc"],
        "셀레늄": ["Se", "Selenium"],
        
        "코엔자임Q10": ["CoQ10", "유비퀴논", "코큐텐"],
        "글루코사민": ["Glucosamine", "글루코사민황산염"],
        "콘드로이틴": ["Chondroitin", "콘드로이친"],
        "MSM": ["메틸설포닐메탄", "황"],
        "콜라겐": ["Collagen", "교원단백질"],
        "히알루론산": ["Hyaluronic Acid", "히알루론"],
        "레시틴": ["Lecithin", "포스파티딜콜린"],
        "밀크씨슬": ["실리마린", "엉겅퀴"],
        "홍삼": ["인삼", "고려인삼", "사포닌"],
        "프로폴리스": ["벌집추출물", "Propolis"],
        "스피루리나": ["Spirulina", "클로렐라"],
        "빌베리": ["Bilberry", "블루베리"],
        "크릴오일": ["Krill Oil", "크릴"],
        "아스타잔틴": ["Astaxanthin"],
        
        # 효능 관련
        "항산화": ["산화방지", "노화방지", "활성산소제거"],
        "항염": ["염증완화", "항염증", "소염"],
        "해독": ["디톡스", "독소제거", "정화"],
    }
    
    # 컨텍스트별 추가 키워드
    CONTEXT_KEYWORDS = {
        "눈": ["시력보호", "안구건조", "눈피로", "황반변성"],
        "관절": ["연골", "관절염", "류마티스"],
        "피부": ["콜라겐", "탄력", "주름개선", "보습"],
        "간": ["간기능개선", "숙취해소", "해독"],
        "면역": ["감기예방", "바이러스", "항균"],
        "뼈": ["골다공증예방", "칼슘흡수"],
        "혈액순환": ["혈전예방", "혈관건강"],
    }
    
    def __init__(self):
        logger.info("쿼리 확장기 초기화 완료 (강화 버전)")
    
    def expand(
        self, 
        query: str, 
        entities: Dict,
        max_synonyms: int = 3,
        include_context: bool = True
    ) -> str:
        """
        쿼리 확장 (강화 버전)
        
        Args:
            query: 원본 쿼리
            entities: 추출된 개체명
            max_synonyms: 각 키워드당 최대 동의어 개수
            include_context: 컨텍스트 키워드 포함 여부
        """
        
        expanded_terms = set()
        
        # 원본 쿼리 단어들
        original_words = query.split()
        expanded_terms.update(original_words)
        
        # 1. 쿼리 내 키워드 기반 동의어 추가
        for key, synonyms in self.SYNONYM_MAP.items():
            if key in query:
                # 가중치 부여: 원본 키워드는 중요도 높음
                expanded_terms.add(key)
                # 상위 N개 동의어만 추가
                expanded_terms.update(synonyms[:max_synonyms])
        
        # 2. 추출된 개체명의 동의어 추가
        for symptom in entities.get("symptoms", []):
            if symptom in self.SYNONYM_MAP:
                expanded_terms.add(symptom)
                expanded_terms.update(self.SYNONYM_MAP[symptom][:max_synonyms])
        
        for ingredient in entities.get("ingredients", []):
            if ingredient in self.SYNONYM_MAP:
                expanded_terms.add(ingredient)
                expanded_terms.update(self.SYNONYM_MAP[ingredient][:max_synonyms])
        
        for body_part in entities.get("body_parts", []):
            if body_part in self.SYNONYM_MAP:
                expanded_terms.add(body_part)
                expanded_terms.update(self.SYNONYM_MAP[body_part][:max_synonyms])
        
        # 3. 컨텍스트 키워드 추가
        if include_context:
            for key, context_words in self.CONTEXT_KEYWORDS.items():
                if key in query or key in entities.get("body_parts", []):
                    # 컨텍스트 키워드는 1-2개만
                    expanded_terms.update(context_words[:2])
        
        # 4. 중복 제거 및 정렬
        # 원본 쿼리 단어를 앞에 배치
        final_terms = []
        
        # 원본 단어 우선
        for word in original_words:
            if word in expanded_terms:
                final_terms.append(word)
                expanded_terms.remove(word)
        
        # 나머지 확장 단어
        final_terms.extend(sorted(expanded_terms))
        
        expanded_query = " ".join(final_terms)
        
        logger.debug(f"확장된 쿼리: {expanded_query}")
        logger.debug(f"확장 비율: {len(final_terms)}/{len(original_words)} = {len(final_terms)/max(len(original_words), 1):.1f}x")
        
        return expanded_query
    
    def get_boosted_terms(self, query: str) -> Dict[str, float]:
        """
        검색 가중치를 위한 부스팅 용어 반환
        
        Returns:
            Dict[term, boost_weight]: 용어별 가중치
        """
        boosted = {}
        
        # 원본 쿼리 단어는 가중치 높음
        for word in query.split():
            boosted[word] = 2.0
        
        # 동의어는 중간 가중치
        for key, synonyms in self.SYNONYM_MAP.items():
            if key in query:
                boosted[key] = 2.0
                for syn in synonyms[:2]:
                    boosted[syn] = 1.5
        
        return boosted


class QueryAnalyzer:
    """통합 쿼리 분석기"""
    
    def __init__(self):
        self.kb = HealthKnowledgeBase()
        self.entity_extractor = EntityExtractor(self.kb)
        self.intent_classifier = IntentClassifier()
        self.query_expander = QueryExpander()
        
        logger.info("쿼리 분석기 초기화 완료")
    
    def analyze(self, query: str) -> Dict:
        """쿼리 종합 분석"""
        
        logger.info(f"쿼리 분석 시작: '{query}'")
        
        # 1. 개체명 추출
        entities = self.entity_extractor.extract(query)
        
        # 2. 의도 분류
        intent = self.intent_classifier.classify(query, entities)
        
        # 3. 쿼리 확장
        expanded_query = self.query_expander.expand(query, entities)
        
        # 4. 지식 베이스 매칭
        knowledge_match = None
        if entities["symptoms"]:
            knowledge_match = self.kb.get_nutrients_for_symptom(query)
        
        analysis_result = {
            "original_query": query,
            "entities": entities,
            "intent": intent,
            "expanded_query": expanded_query,
            "knowledge_match": knowledge_match
        }
        
        logger.info(f"쿼리 분석 완료: 의도={intent}, 개체명={len(sum(entities.values(), []))}개")
        
        return analysis_result

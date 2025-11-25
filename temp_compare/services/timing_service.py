from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class TimingService:
    """영양제 복용 시간 추천 서비스"""

    def __init__(self):
        # 성분별 복용 시간 규칙
        self.timing_rules = {
            '철분': {
                'timing_type': '공복',
                'reason': '철분은 공복에 흡수율이 가장 높습니다.',
                'avoid_with': ['칼슘', '커피', '차', '우유'],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '식사 30분 전', 'description': '점심 식사 전', 'priority': 2},
                ]
            },
            '비타민D': {
                'timing_type': '식후',
                'reason': '비타민D는 지용성 비타민으로 지방과 함께 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '비타민C': {
                'timing_type': '식후',
                'reason': '비타민C는 식후에 섭취하면 위장 자극을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '칼슘': {
                'timing_type': '식후 또는 취침 전',
                'reason': '칼슘은 식후나 취침 전에 섭취하면 흡수율이 좋습니다.',
                'avoid_with': ['철분', '아연'],
                'recommended_times': [
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 1},
                    {'time': '취침 30분 전', 'description': '잠들기 전', 'priority': 2},
                ]
            },
            '마그네슘': {
                'timing_type': '취침 전',
                'reason': '마그네슘은 근육 이완 효과가 있어 취침 전 복용이 좋습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '취침 30분 전', 'description': '잠들기 30분 전', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '오메가3': {
                'timing_type': '식후',
                'reason': '오메가3는 지용성이므로 식사와 함께 섭취하면 흡수율이 높아집니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '비타민B': {
                'timing_type': '아침 식후',
                'reason': '비타민B는 에너지 대사에 관여하므로 아침에 섭취하는 것이 좋습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '아연': {
                'timing_type': '공복 또는 식후',
                'reason': '아연은 공복에 흡수율이 높지만, 위장 자극이 있을 수 있어 식후도 가능합니다.',
                'avoid_with': ['칼슘', '철분', '구리'],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 2시간 후', 'priority': 2},
                ]
            },
            '프로바이오틱스': {
                'timing_type': '공복',
                'reason': '프로바이오틱스는 공복에 섭취하면 위산의 영향을 덜 받아 장까지 잘 도달합니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '취침 전', 'description': '잠들기 전', 'priority': 2},
                ]
            },
        }

    def recommend_timing(self, ingredient: str) -> Dict:
        """성분 기반 복용 시간 추천

        Args:
            ingredient: 성분명 (예: '철분', '비타민D')

        Returns:
            복용 시간 추천 정보를 담은 딕셔너리
        """
        logger.info(f"복용 시간 추천 시작: '{ingredient}'")

        # 성분 이름 정규화 (대소문자, 공백 등)
        normalized_ingredient = self._normalize_ingredient_name(ingredient)

        # 규칙 조회
        timing_info = self.timing_rules.get(normalized_ingredient)

        if timing_info:
            result = {
                'ingredient': ingredient,
                'timing_type': timing_info['timing_type'],
                'reason': timing_info['reason'],
                'avoid_with': timing_info['avoid_with'],
                'recommended_times': timing_info['recommended_times'],
                'has_timing_info': True  # 타이밍 정보 존재 여부
            }
        else:
            # 타이밍 정보 없음 표시 (기본값 반환하지 않음)
            result = {
                'ingredient': ingredient,
                'timing_type': None,
                'reason': None,
                'avoid_with': [],
                'recommended_times': [],
                'has_timing_info': False  # 타이밍 정보 없음
            }
            logger.warning(f"'{ingredient}'에 대한 복용 시간 규칙이 없습니다.")

        return result

    def recommend_multiple_timing(self, ingredients: List[str]) -> Dict:
        """여러 성분에 대한 복용 시간 추천 (개선 버전)

        Args:
            ingredients: 성분 목록

        Returns:
            성분별 복용 시간 추천 정보 + 최적 복용 스케줄
        """
        logger.info(f"복수 성분 복용 시간 추천: {ingredients}")

        recommendations = {}
        conflicts = []
        timing_groups = {
            '아침 공복': [],
            '아침 식후': [],
            '점심 식후': [],
            '저녁 식후': [],
            '취침 전': []
        }

        # 각 성분별 추천 정보 수집
        ingredients_with_info = []
        ingredients_without_info = []
        
        for ingredient in ingredients:
            rec = self.recommend_timing(ingredient)
            recommendations[ingredient] = rec
            
            if rec.get('has_timing_info'):
                ingredients_with_info.append(ingredient)
                # 타이밍 그룹 분류
                timing_type = rec['timing_type']
                if '공복' in timing_type:
                    timing_groups['아침 공복'].append(ingredient)
                elif '아침' in timing_type:
                    timing_groups['아침 식후'].append(ingredient)
                elif '취침' in timing_type:
                    timing_groups['취침 전'].append(ingredient)
                elif '저녁' in timing_type:
                    timing_groups['저녁 식후'].append(ingredient)
                else:
                    timing_groups['점심 식후'].append(ingredient)
            else:
                ingredients_without_info.append(ingredient)

        # 모든 항목에 대해 정보가 없는 경우 기본 추천 제공
        if len(ingredients_without_info) == len(ingredients):
            logger.info("모든 성분에 대한 타이밍 정보가 없어 기본 추천을 제공합니다.")
            return {
                'recommendations': recommendations,
                'conflicts': [],
                'timing_groups': {},
                'optimal_schedule': [],
                'summary': {
                    'total_ingredients': len(ingredients),
                    'conflict_count': 0,
                    'timing_slots': 0,
                    'ingredients_with_info': 0,
                    'ingredients_without_info': len(ingredients)
                },
                'default_recommendation': {
                    'message': '입력하신 성분들에 대한 구체적인 복용 시간 정보가 없습니다.',
                    'general_advice': '일반적으로 식후 섭취를 권장합니다. 제품 라벨을 참고하거나 전문가와 상담하세요.',
                    'ingredients': ingredients_without_info
                },
                'message': f'{len(ingredients)}개 성분에 대한 정보를 조회했으나 구체적인 복용 시간 정보가 없습니다.'
            }

        # 충돌 검사 및 해결 방안 제시 (정보가 있는 성분들만)
        for i, ing1 in enumerate(ingredients_with_info):
            for ing2 in ingredients_with_info[i+1:]:
                norm_ing1 = self._normalize_ingredient_name(ing1)
                norm_ing2 = self._normalize_ingredient_name(ing2)

                timing1 = self.timing_rules.get(norm_ing1, {})
                timing2 = self.timing_rules.get(norm_ing2, {})

                avoid1 = timing1.get('avoid_with', [])
                avoid2 = timing2.get('avoid_with', [])

                if norm_ing2 in avoid1 or norm_ing1 in avoid2:
                    conflicts.append({
                        'ingredient1': ing1,
                        'ingredient2': ing2,
                        'warning': f'{ing1}과(와) {ing2}은(는) 함께 복용하지 않는 것이 좋습니다.',
                        'solution': f'{ing1}은(는) {timing1.get("timing_type", "식후")}에, {ing2}은(는) {timing2.get("timing_type", "식후")}에 각각 복용하세요.',
                        'time_gap': '최소 2시간 간격을 두고 복용하세요.'
                    })

        # 최적 복용 스케줄 생성
        schedule = self._generate_optimal_schedule(timing_groups, conflicts)

        result = {
            'recommendations': recommendations,
            'conflicts': conflicts,
            'timing_groups': {k: v for k, v in timing_groups.items() if v},  # 비어있지 않은 그룹만
            'optimal_schedule': schedule,
            'summary': {
                'total_ingredients': len(ingredients),
                'conflict_count': len(conflicts),
                'timing_slots': len([v for v in timing_groups.values() if v]),
                'ingredients_with_info': len(ingredients_with_info),
                'ingredients_without_info': len(ingredients_without_info)
            },
            'message': f'{len(ingredients)}개 성분에 대한 복용 시간을 추천했습니다.'
        }
        
        # 정보가 없는 성분이 있으면 알림 추가
        if ingredients_without_info:
            result['ingredients_without_timing_info'] = ingredients_without_info
            result['message'] += f" (단, {len(ingredients_without_info)}개 성분은 구체적인 타이밍 정보가 없습니다.)"
        
        return result
    
    def _generate_optimal_schedule(self, timing_groups: Dict, conflicts: List[Dict]) -> List[Dict]:
        """최적 복용 스케줄 생성"""
        schedule = []
        
        # 충돌하는 성분 쌍 추출
        conflict_pairs = set()
        for conflict in conflicts:
            pair = tuple(sorted([conflict['ingredient1'], conflict['ingredient2']]))
            conflict_pairs.add(pair)
        
        # 각 타이밍 슬롯별로 스케줄 생성
        time_slots = [
            ('07:00', '아침 공복', '기상 직후'),
            ('08:00', '아침 식후', '아침 식사 직후'),
            ('12:30', '점심 식후', '점심 식사 직후'),
            ('18:30', '저녁 식후', '저녁 식사 직후'),
            ('22:00', '취침 전', '잠들기 30분 전')
        ]
        
        for time, slot_name, description in time_slots:
            ingredients_in_slot = timing_groups.get(slot_name, [])
            if ingredients_in_slot:
                schedule.append({
                    'time': time,
                    'timing': slot_name,
                    'description': description,
                    'ingredients': ingredients_in_slot,
                    'count': len(ingredients_in_slot),
                    'notes': self._get_slot_notes(ingredients_in_slot, conflict_pairs)
                })
        
        return schedule
    
    def _get_slot_notes(self, ingredients: List[str], conflict_pairs: set) -> List[str]:
        """특정 타이밍 슬롯에 대한 주의사항 생성"""
        notes = []
        
        # 충돌 확인
        for i, ing1 in enumerate(ingredients):
            for ing2 in ingredients[i+1:]:
                pair = tuple(sorted([ing1, ing2]))
                if pair in conflict_pairs:
                    notes.append(f'⚠️ {ing1}과(와) {ing2}은(는) 2시간 간격을 두고 복용하세요.')
        
        # 일반 주의사항
        if len(ingredients) > 3:
            notes.append('💊 한 번에 너무 많은 영양제를 복용하지 마세요.')
        
        return notes

    def _normalize_ingredient_name(self, ingredient: str) -> str:
        """성분명 정규화

        Args:
            ingredient: 원본 성분명

        Returns:
            정규화된 성분명
        """
        # 공백 제거 및 소문자 변환
        normalized = ingredient.strip()

        # 별칭 처리
        aliases = {
            '비타민디': '비타민D',
            'vitamin d': '비타민D',
            'vitamin D': '비타민D',
            '비타민씨': '비타민C',
            'vitamin c': '비타민C',
            'vitamin C': '비타민C',
            '비타민비': '비타민B',
            'vitamin b': '비타민B',
            'vitamin B': '비타민B',
            'omega3': '오메가3',
            'omega-3': '오메가3',
            '유산균': '프로바이오틱스',
            'probiotics': '프로바이오틱스',
        }

        return aliases.get(normalized, normalized)

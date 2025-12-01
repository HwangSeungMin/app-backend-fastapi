from typing import List, Dict, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TimingService:
    """영양제 복용 시간 추천 서비스"""

    def __init__(self):
        # 성분별 복용 시간 규칙 (50가지 영양 성분)
        self.timing_rules = {
            # ========== 비타민류 (14개) ==========
            '비타민A': {
                'timing_type': '식후',
                'reason': '비타민A는 지용성 비타민으로 지방과 함께 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '비타민B1': {
                'timing_type': '아침 식후',
                'reason': '티아민은 에너지 대사에 관여하므로 아침에 섭취하는 것이 좋습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '비타민B2': {
                'timing_type': '아침 식후',
                'reason': '리보플라빈은 에너지 생성에 필요하므로 아침 섭취가 효과적입니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '비타민B6': {
                'timing_type': '아침 식후',
                'reason': '피리독신은 신경전달물질 합성에 관여하므로 아침 섭취가 좋습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '비타민B12': {
                'timing_type': '아침 식후',
                'reason': '코발라민은 에너지 대사와 적혈구 생성에 관여하므로 아침 섭취가 효과적입니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
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
            '비타민C': {
                'timing_type': '식후',
                'reason': '비타민C는 식후에 섭취하면 위장 자극을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
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
            '비타민E': {
                'timing_type': '식후',
                'reason': '비타민E는 지용성 비타민으로 지방과 함께 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '비타민K': {
                'timing_type': '식후',
                'reason': '비타민K는 지용성 비타민으로 지방과 함께 섭취 시 흡수율이 높습니다.',
                'avoid_with': ['항응고제'],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '엽산': {
                'timing_type': '아침 공복',
                'reason': '엽산은 공복에 흡수율이 높으며, 세포 분열과 DNA 합성에 필수적입니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 2},
                ]
            },
            '나이아신': {
                'timing_type': '식후',
                'reason': '나이아신은 식후 섭취 시 홍조 부작용을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '판토텐산': {
                'timing_type': '아침 식후',
                'reason': '판토텐산은 에너지 대사에 관여하므로 아침 섭취가 좋습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '비오틴': {
                'timing_type': '아침 식후',
                'reason': '비오틴은 에너지 대사와 피부 건강에 관여하므로 아침 섭취가 효과적입니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            
            # ========== 미네랄류 (12개) ==========
            '철분': {
                'timing_type': '공복',
                'reason': '철분은 공복에 흡수율이 가장 높습니다.',
                'avoid_with': ['칼슘', '커피', '차', '우유'],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '식사 30분 전', 'description': '점심 식사 전', 'priority': 2},
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
            '아연': {
                'timing_type': '공복 또는 식후',
                'reason': '아연은 공복에 흡수율이 높지만, 위장 자극이 있을 수 있어 식후도 가능합니다.',
                'avoid_with': ['칼슘', '철분', '구리'],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 2시간 후', 'priority': 2},
                ]
            },
            '셀레늄': {
                'timing_type': '식후',
                'reason': '셀레늄은 식후 섭취 시 흡수율이 높고 위장 자극을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '구리': {
                'timing_type': '식후',
                'reason': '구리는 식후 섭취 시 흡수율이 높습니다.',
                'avoid_with': ['아연'],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '망간': {
                'timing_type': '식후',
                'reason': '망간은 식후 섭취 시 흡수율이 높고 위장 자극을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '크롬': {
                'timing_type': '식후',
                'reason': '크롬은 혈당 조절에 도움이 되므로 식후 섭취가 효과적입니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '요오드': {
                'timing_type': '아침 공복',
                'reason': '요오드는 갑상선 호르몬 합성에 필요하므로 아침 공복 섭취가 좋습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 2},
                ]
            },
            '칼륨': {
                'timing_type': '식후',
                'reason': '칼륨은 식후 섭취 시 위장 자극을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '몰리브덴': {
                'timing_type': '식후',
                'reason': '몰리브덴은 식후 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '인': {
                'timing_type': '식후',
                'reason': '인은 칼슘과 함께 뼈 건강에 중요하므로 식후 섭취가 좋습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            
            # ========== 오메가 지방산 (3개) ==========
            '오메가3': {
                'timing_type': '식후',
                'reason': '오메가3는 지용성이므로 식사와 함께 섭취하면 흡수율이 높아집니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '오메가6': {
                'timing_type': '식후',
                'reason': '오메가6는 지용성이므로 식사와 함께 섭취하면 흡수율이 높아집니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '오메가9': {
                'timing_type': '식후',
                'reason': '오메가9는 지용성이므로 식사와 함께 섭취하면 흡수율이 높아집니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            
            # ========== 프로바이오틱스 & 소화효소 (2개) ==========
            '프로바이오틱스': {
                'timing_type': '공복',
                'reason': '프로바이오틱스는 공복에 섭취하면 위산의 영향을 덜 받아 장까지 잘 도달합니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '취침 전', 'description': '잠들기 전', 'priority': 2},
                ]
            },
            '소화효소': {
                'timing_type': '식사 직전',
                'reason': '소화효소는 식사 직전 섭취 시 음식물 분해를 효과적으로 도울 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '식사 10분 전', 'description': '식사 10분 전', 'priority': 1},
                    {'time': '식사 직전', 'description': '식사 직전', 'priority': 2},
                ]
            },
            
            # ========== 항산화제 (5개) ==========
            '코엔자임Q10': {
                'timing_type': '식후',
                'reason': '코엔자임Q10은 지용성이므로 지방과 함께 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '알파리포산': {
                'timing_type': '공복',
                'reason': '알파리포산은 공복에 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '식사 30분 전', 'description': '식사 30분 전', 'priority': 2},
                ]
            },
            '루테인': {
                'timing_type': '식후',
                'reason': '루테인은 지용성이므로 지방과 함께 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '아스타잔틴': {
                'timing_type': '식후',
                'reason': '아스타잔틴은 지용성이므로 지방과 함께 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '레스베라트롤': {
                'timing_type': '식후',
                'reason': '레스베라트롤은 식후 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            
            # ========== 아미노산 (5개) ==========
            'L-카르니틴': {
                'timing_type': '운동 전',
                'reason': 'L-카르니틴은 지방 연소를 돕므로 운동 30분~1시간 전 섭취가 효과적입니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '운동 30분 전', 'description': '운동 30분 전', 'priority': 1},
                    {'time': '아침 공복', 'description': '아침 공복', 'priority': 2},
                ]
            },
            'L-아르기닌': {
                'timing_type': '공복',
                'reason': 'L-아르기닌은 공복에 흡수율이 높으며, 혈류 개선에 도움이 됩니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '운동 전', 'description': '운동 30분 전', 'priority': 2},
                ]
            },
            'L-글루타민': {
                'timing_type': '운동 후',
                'reason': 'L-글루타민은 근육 회복을 돕므로 운동 후 섭취가 효과적입니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '운동 직후', 'description': '운동 직후', 'priority': 1},
                    {'time': '취침 전', 'description': '취침 전', 'priority': 2},
                ]
            },
            'BCAA': {
                'timing_type': '운동 전후',
                'reason': 'BCAA는 근육 분해를 막고 회복을 돕므로 운동 전후 섭취가 좋습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '운동 30분 전', 'description': '운동 30분 전', 'priority': 1},
                    {'time': '운동 직후', 'description': '운동 직후', 'priority': 2},
                ]
            },
            'L-테아닌': {
                'timing_type': '취침 전',
                'reason': 'L-테아닌은 이완 효과가 있어 취침 전 섭취가 수면에 도움이 됩니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '취침 30분 전', 'description': '취침 30분 전', 'priority': 1},
                    {'time': '스트레스 상황', 'description': '스트레스 상황', 'priority': 2},
                ]
            },
            
            # ========== 관절/뼈 건강 (4개) ==========
            '글루코사민': {
                'timing_type': '식후',
                'reason': '글루코사민은 식후 섭취 시 위장 자극을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '콘드로이틴': {
                'timing_type': '식후',
                'reason': '콘드로이틴은 식후 섭취 시 흡수율이 높고 위장 자극을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            'MSM': {
                'timing_type': '식후',
                'reason': 'MSM은 식후 섭취 시 위장 자극을 줄일 수 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '콜라겐': {
                'timing_type': '취침 전',
                'reason': '콜라겐은 취침 중 피부 재생이 활발하므로 취침 전 섭취가 효과적입니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '취침 1시간 전', 'description': '취침 1시간 전', 'priority': 1},
                    {'time': '공복', 'description': '아침 공복', 'priority': 2},
                ]
            },
            
            # ========== 허브/식물 추출물 (5개) ==========
            '밀크씨슬': {
                'timing_type': '식후',
                'reason': '밀크씨슬은 간 건강에 도움이 되며, 식후 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '홍삼': {
                'timing_type': '아침 공복',
                'reason': '홍삼은 공복에 흡수율이 높으며, 에너지 증진 효과가 있어 아침 섭취가 좋습니다.',
                'avoid_with': ['커피'],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 2},
                ]
            },
            '은행잎추출물': {
                'timing_type': '식후',
                'reason': '은행잎추출물은 혈액순환 개선에 도움이 되며, 식후 섭취가 좋습니다.',
                'avoid_with': ['항응고제'],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '점심 식사 후', 'description': '점심 식사 직후', 'priority': 2},
                ]
            },
            '커큐민': {
                'timing_type': '식후',
                'reason': '커큐민은 지용성이므로 지방과 함께 섭취 시 흡수율이 높습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '아침 식사 후', 'description': '아침 식사 직후', 'priority': 1},
                    {'time': '저녁 식사 후', 'description': '저녁 식사 직후', 'priority': 2},
                ]
            },
            '프로폴리스': {
                'timing_type': '공복',
                'reason': '프로폴리스는 공복에 흡수율이 높으며, 면역 증진 효과가 있습니다.',
                'avoid_with': [],
                'recommended_times': [
                    {'time': '기상 직후', 'description': '아침 공복', 'priority': 1},
                    {'time': '취침 전', 'description': '취침 전', 'priority': 2},
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

        # 별칭 처리 (50개 성분 지원)
        aliases = {
            # 비타민류
            '비타민에이': '비타민A',
            'vitamin a': '비타민A',
            'vitamin A': '비타민A',
            '레티놀': '비타민A',
            'retinol': '비타민A',
            
            '티아민': '비타민B1',
            'thiamine': '비타민B1',
            'vitamin b1': '비타민B1',
            
            '리보플라빈': '비타민B2',
            'riboflavin': '비타민B2',
            'vitamin b2': '비타민B2',
            
            '피리독신': '비타민B6',
            'pyridoxine': '비타민B6',
            'vitamin b6': '비타민B6',
            
            '코발라민': '비타민B12',
            'cobalamin': '비타민B12',
            'vitamin b12': '비타민B12',
            
            '비타민비': '비타민B',
            'vitamin b': '비타민B',
            'vitamin B': '비타민B',
            '비타민B군': '비타민B',
            '비타민B복합체': '비타민B',
            
            '비타민씨': '비타민C',
            'vitamin c': '비타민C',
            'vitamin C': '비타민C',
            '아스코르브산': '비타민C',
            'ascorbic acid': '비타민C',
            
            '비타민디': '비타민D',
            'vitamin d': '비타민D',
            'vitamin D': '비타민D',
            '칼시페롤': '비타민D',
            'calciferol': '비타민D',
            
            '비타민이': '비타민E',
            'vitamin e': '비타민E',
            'vitamin E': '비타민E',
            '토코페롤': '비타민E',
            'tocopherol': '비타민E',
            
            '비타민케이': '비타민K',
            'vitamin k': '비타민K',
            'vitamin K': '비타민K',
            
            '폴산': '엽산',
            'folic acid': '엽산',
            'folate': '엽산',
            
            '니아신': '나이아신',
            'niacin': '나이아신',
            'vitamin b3': '나이아신',
            
            '판토텐': '판토텐산',
            'pantothenic acid': '판토텐산',
            'vitamin b5': '판토텐산',
            
            'biotin': '비오틴',
            'vitamin b7': '비오틴',
            'vitamin h': '비오틴',
            
            # 미네랄류
            'iron': '철분',
            'fe': '철분',
            
            'calcium': '칼슘',
            'ca': '칼슘',
            
            'magnesium': '마그네슘',
            'mg': '마그네슘',
            
            'zinc': '아연',
            'zn': '아연',
            
            'selenium': '셀레늄',
            'se': '셀레늄',
            
            'copper': '구리',
            'cu': '구리',
            
            'manganese': '망간',
            'mn': '망간',
            
            'chromium': '크롬',
            'cr': '크롬',
            
            'iodine': '요오드',
            'i': '요오드',
            '아이오딘': '요오드',
            
            'potassium': '칼륨',
            'k': '칼륨',
            
            'molybdenum': '몰리브덴',
            'mo': '몰리브덴',
            
            'phosphorus': '인',
            'p': '인',
            
            # 오메가 지방산
            'omega3': '오메가3',
            'omega-3': '오메가3',
            'omega 3': '오메가3',
            'dha': '오메가3',
            'epa': '오메가3',
            
            'omega6': '오메가6',
            'omega-6': '오메가6',
            'omega 6': '오메가6',
            
            'omega9': '오메가9',
            'omega-9': '오메가9',
            'omega 9': '오메가9',
            
            # 프로바이오틱스
            '유산균': '프로바이오틱스',
            'probiotics': '프로바이오틱스',
            '락토바실러스': '프로바이오틱스',
            '비피더스균': '프로바이오틱스',
            
            # 항산화제
            'coq10': '코엔자임Q10',
            'coenzyme q10': '코엔자임Q10',
            '코큐텐': '코엔자임Q10',
            
            'alpha lipoic acid': '알파리포산',
            'ala': '알파리포산',
            
            'lutein': '루테인',
            '지아잔틴': '루테인',
            
            'astaxanthin': '아스타잔틴',
            
            'resveratrol': '레스베라트롤',
            
            # 아미노산
            'l-carnitine': 'L-카르니틴',
            'carnitine': 'L-카르니틴',
            '카르니틴': 'L-카르니틴',
            
            'l-arginine': 'L-아르기닌',
            'arginine': 'L-아르기닌',
            '아르기닌': 'L-아르기닌',
            
            'l-glutamine': 'L-글루타민',
            'glutamine': 'L-글루타민',
            '글루타민': 'L-글루타민',
            
            'bcaa': 'BCAA',
            '분지쇄아미노산': 'BCAA',
            
            'l-theanine': 'L-테아닌',
            'theanine': 'L-테아닌',
            '테아닌': 'L-테아닌',
            
            # 관절/뼈 건강
            'glucosamine': '글루코사민',
            
            'chondroitin': '콘드로이틴',
            '콘드로이친': '콘드로이틴',
            
            'msm': 'MSM',
            '메틸설포닐메탄': 'MSM',
            
            'collagen': '콜라겐',
            '교원단백질': '콜라겐',
            
            # 허브/식물 추출물
            'milk thistle': '밀크씨슬',
            '실리마린': '밀크씨슬',
            '엉겅퀴': '밀크씨슬',
            
            '인삼': '홍삼',
            '고려인삼': '홍삼',
            'ginseng': '홍삼',
            
            'ginkgo biloba': '은행잎추출물',
            '은행잎': '은행잎추출물',
            
            'curcumin': '커큐민',
            '강황': '커큐민',
            'turmeric': '커큐민',
            
            'propolis': '프로폴리스',
            '벌집추출물': '프로폴리스',
        }

        return aliases.get(normalized, normalized)

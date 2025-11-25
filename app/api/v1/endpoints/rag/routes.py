from fastapi import APIRouter, HTTPException, Path
from app.schemas.rag.schemas import (
    SearchRequest, SymptomSearchRequest, IngredientSearchRequest,
    TimingRecommendationRequest, APIResponse, IntelligentSearchRequest,
    GeminiRecommendationRequest
)
from app.services.rag.recommendation_service import RecommendationService
from app.services.rag.timing_service import TimingService
from app.search.rag_search import RAGSearchEngine
from app.search.query_analyzer import QueryAnalyzer
from app.search.smart_router import SmartRouter
from app.search.fallback_system import FallbackSystem
from app.search.reranker import ResultReRanker
from app.utils.logger import get_logger
from typing import Dict, Any

logger = get_logger(__name__)

# 라우터 생성
router = APIRouter()

# 서비스 초기화
search_engine = RAGSearchEngine()
recommendation_service = RecommendationService()
timing_service = TimingService()

# 새로운 지능형 검색 컴포넌트 초기화
query_analyzer = QueryAnalyzer()
smart_router = SmartRouter()
fallback_system = FallbackSystem()
reranker = ResultReRanker()

@router.get('/health', response_model=Dict[str, Any])
async def health_check():
    """헬스 체크"""
    return {
        'success': True,
        'message': 'API 서버가 정상 작동 중입니다.'
    }

@router.post('/search/hybrid', response_model=Dict[str, Any])
async def hybrid_search(request: SearchRequest):
    """하이브리드 검색"""
    try:
        results = search_engine.hybrid_search(
            query=request.query,
            top_k=request.top_k
        )

        return {
            'success': True,
            'message': f'{len(results)}개의 결과를 찾았습니다.',
            'data': {
                'query': request.query,
                'results': results,
                'count': len(results)
            }
        }

    except Exception as e:
        logger.error(f"검색 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail='검색 중 오류가 발생했습니다.'
        )

@router.post('/search/symptom', response_model=Dict[str, Any])
async def search_by_symptom(request: SymptomSearchRequest):
    """증상 기반 검색"""
    try:
        results = search_engine.search_by_symptom(
            symptom=request.symptom,
            top_k=request.top_k
        )

        return {
            'success': True,
            'message': f'{len(results)}개의 결과를 찾았습니다.',
            'data': {
                'symptom': request.symptom,
                'results': results,
                'count': len(results)
            }
        }

    except Exception as e:
        logger.error(f"증상 검색 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail='검색 중 오류가 발생했습니다.'
        )

@router.post('/search/ingredient', response_model=Dict[str, Any])
async def search_by_ingredient(request: IngredientSearchRequest):
    """성분 기반 검색"""
    try:
        results = search_engine.search_by_ingredient(
            ingredient=request.ingredient,
            top_k=request.top_k
        )

        return {
            'success': True,
            'message': f'{len(results)}개의 제품을 찾았습니다.',
            'data': {
                'ingredient': request.ingredient,
                'results': results,
                'count': len(results)
            }
        }

    except Exception as e:
        logger.error(f"성분 검색 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail='검색 중 오류가 발생했습니다.'
        )

@router.post('/recommend/symptom', response_model=Dict[str, Any])
async def recommend_by_symptom(request: SymptomSearchRequest):
    """증상 기반 추천"""
    try:
        result = recommendation_service.recommend_by_symptom(
            symptom=request.symptom,
            top_k=request.top_k
        )

        return {
            'success': True,
            'message': result['message'],
            'data': result
        }

    except Exception as e:
        logger.error(f"추천 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail='추천 중 오류가 발생했습니다.'
        )

@router.post('/recommend/timing', response_model=Dict[str, Any])
async def recommend_timing(request: TimingRecommendationRequest):
    """복용 시간 추천 (복수형 통일)"""
    try:
        ingredients = request.ingredients
        logger.info(f"복용 시간 추천 요청: {ingredients}")
        
        # 단일 성분이든 복수 성분이든 통일된 처리
        if len(ingredients) == 1:
            # 단일 성분
            result = timing_service.recommend_timing(
                ingredient=ingredients[0]
            )
            # 단일 성분도 복수형 응답 형식으로 변환
            result = {
                'recommendations': {ingredients[0]: result},
                'conflicts': [],
                'timing_groups': {},
                'optimal_schedule': [],
                'summary': {
                    'total_ingredients': 1,
                    'conflict_count': 0,
                    'timing_slots': 1
                },
                'message': '복용 시간 추천이 완료되었습니다.'
            }
        else:
            # 복수 성분
            result = timing_service.recommend_multiple_timing(
                ingredients=ingredients
            )
        
        # 메시지 생성
        message = f'{len(ingredients)}개 성분에 대한 복용 시간을 추천했습니다.'
        if result.get('conflicts'):
            message += f" ({len(result['conflicts'])}개 상호작용 주의사항 있음)"

        return {
            'success': True,
            'message': message,
            'data': result
        }

    except Exception as e:
        logger.error(f"시간 추천 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail='시간 추천 중 오류가 발생했습니다.'
        )

@router.get('/product/{product_id}', response_model=Dict[str, Any])
async def get_product_detail(
    product_id: str = Path(..., description="제품 ID")
):
    """제품 상세 조회"""
    try:
        result = search_engine.get_product_by_id(product_id)

        if result:
            return {
                'success': True,
                'message': '제품 정보를 조회했습니다.',
                'data': result
            }
        else:
            raise HTTPException(
                status_code=404,
                detail='제품을 찾을 수 없습니다.'
            )


    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"제품 조회 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail='제품 조회 중 오류가 발생했습니다.'
        )

@router.post('/search/intelligent', response_model=Dict[str, Any])
async def intelligent_search(request: IntelligentSearchRequest):
    """
    지능형 검색 (Intelligent Search)
    
    쿼리 분석, 의도 파악, 스마트 라우팅, Fallback, Re-ranking, SERP 검색을 통합한
    고급 검색 엔드포인트입니다.
    """
    try:
        logger.info(f"지능형 검색 요청: '{request.query}'")
        
        # 1. 쿼리 분석
        analysis = query_analyzer.analyze(request.query)
        
        logger.info(f"쿼리 분석 완료: 의도={analysis['intent']}")
        
        # 2. SERP 검색 (비동기, 원본 쿼리 사용)
        serp_results = []
        serp_enabled = False
        
        if request.enable_serp:
            logger.info("SERP 검색 시작 (원본 쿼리)")
            try:
                # 비동기로 SERP 검색 실행
                from app.services.rag.serp_service import serp_service
                serp_results = await serp_service.search(
                    query=request.query,  # 원본 쿼리 사용 (개체명 추출 전)
                    max_results=request.serp_max_results,
                    enabled=request.enable_serp
                )
                serp_enabled = len(serp_results) > 0
                logger.info(f"SERP 검색 완료: {len(serp_results)}개 결과")
            except Exception as e:
                logger.error(f"SERP 검색 오류 (계속 진행): {e}")
        
        # 3. 스마트 라우팅 및 RAG 검색 실행
        api_name, routing_info, results = smart_router.route(
            analysis=analysis,
            top_k=request.top_k
        )
        
        logger.info(f"라우팅 완료: API={api_name}")
        
        # 4. Fallback 처리
        fallback_used = False
        fallback_info = None
        
        if request.enable_fallback:
            if fallback_system.should_use_fallback(results):
                logger.info("Fallback 응답 생성")
                fallback_info = fallback_system.generate_fallback_response(
                    request.query,
                    analysis
                )
                fallback_used = True
        
        # 5. Re-ranking (리스트 결과인 경우만)
        if request.enable_reranking and isinstance(results, list) and len(results) > 0:
            logger.info("Re-ranking 적용")
            
            if request.enable_diversity:
                results = reranker.rerank_with_diversity(results)
            else:
                results = reranker.rerank(results, request.query)
        
        # 6. 추가 정보 보강
        additional_info = None
        if not fallback_used:
            enhanced = fallback_system.enhance_results(
                results,
                request.query,
                analysis
            )
            additional_info = enhanced.get("additional_info")
        
        # 7. 응답 구성
        response = {
            'success': True,
            'message': f'검색 완료 (API: {api_name})',
            'query_analysis': {
                'original_query': analysis['original_query'],
                'entities': analysis['entities'],
                'intent': analysis['intent'],
                'expanded_query': analysis['expanded_query'],
                'knowledge_match': analysis.get('knowledge_match')
            },
            'routing_info': {
                'selected_api': api_name,
                **routing_info
            },
            'results': results,
            'fallback_used': fallback_used,
            'serp_enabled': serp_enabled
        }
        
        if fallback_info:
            response['fallback_info'] = fallback_info
        
        if additional_info:
            response['additional_info'] = additional_info
        
        if serp_results:
            response['serp_results'] = serp_results
        
        logger.info(f"지능형 검색 완료: fallback={fallback_used}, serp={serp_enabled}")
        
        return response
        
    except Exception as e:
        logger.error(f"지능형 검색 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f'검색 중 오류가 발생했습니다: {str(e)}'
        )

@router.post('/search/serp', response_model=Dict[str, Any])
async def serp_search(request: SearchRequest):
    """
    Google SERP 검색 (테스트용)
    
    SerpAPI를 사용하여 Google 검색 결과만 반환합니다.
    """
    try:
        logger.info(f"SERP 검색 요청: '{request.query}'")
        
        # SERP 서비스 import
        from app.services.rag.serp_service import serp_service
        
        # SERP 검색 실행
        serp_results = await serp_service.search(
            query=request.query,
            max_results=request.top_k,
            enabled=True  # 강제 활성화
        )
        
        # 서비스 상태 확인
        status = serp_service.get_status()
        
        logger.info(f"SERP 검색 완료: {len(serp_results)}개 결과")
        
        return {
            'success': True,
            'message': f'SERP 검색 완료 ({len(serp_results)}개 결과)',
            'query': request.query,
            'results': serp_results,
            'service_status': status,
            'result_count': len(serp_results)
        }
        
    except Exception as e:
        logger.error(f"SERP 검색 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f'SERP 검색 중 오류가 발생했습니다: {str(e)}'
        )

@router.post('/recommend/gemini', response_model=Dict[str, Any])
async def gemini_recommendation(request: GeminiRecommendationRequest):
    """
    Gemini 기반 통합 추천
    
    RAG + SERP 결과를 Gemini LLM으로 융합하여 최종 추천 생성
    """
    try:
        logger.info(f"Gemini 추천 요청: '{request.query}'")
        
        # 1. RAG 검색
        logger.info("RAG 검색 시작")
        rag_results = search_engine.hybrid_search(
            query=request.query,
            top_k=request.top_k
        )
        logger.info(f"RAG 검색 완료: {len(rag_results)}개 결과")
        
        # 2. SERP 검색
        serp_results = []
        if request.enable_serp:
            logger.info("SERP 검색 시작")
            from app.services.rag.serp_service import serp_service
            serp_results = await serp_service.search(
                query=request.query,
                max_results=request.serp_max_results,
                enabled=True
            )
            logger.info(f"SERP 검색 완료: {len(serp_results)}개 결과")
        
        # 3. Gemini로 융합
        logger.info("Gemini 추천 생성 시작")
        from app.services.rag.gemini_service import gemini_service
        
        recommendation = await gemini_service.generate_recommendation(
            query=request.query,
            rag_results=rag_results,
            serp_results=serp_results,
            rag_weight=request.rag_weight,
            max_length=request.max_length,
            custom_prompt=request.custom_prompt,
            output_options={
                'include_product_name': request.include_product_name,
                'include_ingredients': request.include_ingredients,
                'include_timing': request.include_timing,
                'include_precautions': request.include_precautions
            }
        )
        
        logger.info("Gemini 추천 생성 완료")
        
        # 4. 응답 구성
        return {
            'success': True,
            'message': 'Gemini 추천 완료',
            'query': request.query,
            'recommendation': recommendation,
            'sources': {
                'rag_count': len(rag_results),
                'serp_count': len(serp_results),
                'rag_weight': request.rag_weight,
                'gemini_weight': 1 - request.rag_weight
            },
            'metadata': {
                'max_length': request.max_length,
                'actual_length': len(recommendation.get('text', '')),
                'model': gemini_service.model_name,
                'temperature': gemini_service.temperature
            }
        }
        
    except ValueError as e:
        logger.error(f"Gemini 설정 오류: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Gemini 추천 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f'추천 생성 중 오류가 발생했습니다: {str(e)}'
        )

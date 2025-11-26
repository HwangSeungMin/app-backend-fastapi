import json
from datetime import datetime
from typing import List, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DataProcessor:
    """C003 API 데이터 전처리 클래스"""
    
    def process_product_data(
        self, 
        products: List[Dict],
        kibana_optimized: bool = True
    ) -> List[Dict]:
        """C003 API 데이터를 ElasticSearch 문서 형식으로 변환
        
        Args:
            products: C003 API 제품 데이터 리스트
            kibana_optimized: Kibana 최적화 필드 추가 여부
        """
        
        logger.info(f"C003 데이터 전처리 시작 (Kibana 최적화: {kibana_optimized})")
        
        processed = []
        
        for idx, product in enumerate(products):
            try:
                doc = self._create_document(
                    product,
                    kibana_optimized=kibana_optimized
                )
                processed.append(doc)
                
                if (idx + 1) % 1000 == 0:
                    logger.info(f"처리 진행: {idx + 1}/{len(products)}")
                    
            except Exception as e:
                logger.error(f"문서 생성 오류 (제품 ID: {product.get('PRDLST_REPORT_NO')}): {e}")
                continue
        
        logger.info(f"전처리 완료: {len(processed)}개 문서")
        
        return processed
    
    def _create_document(
        self, 
        product: Dict,
        kibana_optimized: bool = True
    ) -> Dict:
        """C003 API 데이터로 개별 문서 생성"""
        
        product_id = product.get('PRDLST_REPORT_NO', '')
        company_name = product.get('BSSH_NM', '')
        product_name = product.get('PRDLST_NM', '')
        
        # 고유 ID 생성 (제품번호_회사명)
        unique_id = f"{product_id}_{company_name}"
        
        doc = {
            'product_id': unique_id,
            'product_name': product_name,
            'company_name': company_name,
            
            # 날짜 정보
            'report_date': product.get('PRMS_DT', ''),
            'last_update_date': product.get('LAST_UPDT_DTM', ''),
            'created_date': product.get('CRET_DTM', ''),
            
            # 제품 형태 (NEW!)
            'product_shape': product.get('PRDT_SHAP_CD_NM', ''),
            
            # 원재료 및 기능성
            'raw_materials': product.get('RAWMTRL_NM', ''),
            'primary_function': product.get('PRIMARY_FNCLTY', ''),
            
            # 섭취 정보
            'intake_info': {
                'method': product.get('NTK_MTHD', ''),
                'caution': product.get('IFTKN_ATNT_MATR_CN', '')
            },
            
            # 제품 상세 정보 (NEW!)
            'product_details': {
                'standards': product.get('STDR_STND', ''),
                'appearance': product.get('DISPOS', ''),
                'shelf_life': product.get('POG_DAYCNT', ''),
                'storage_method': product.get('CSTDY_MTHD', '')
            },
            
            # 인허가 정보 (NEW!)
            'license_info': {
                'license_no': product.get('LCNS_NO', ''),
                'report_no': product_id
            },
            
            # 메타데이터
            'metadata': {
                'source': 'C003_API',
                'update_date': datetime.now().isoformat()
            }
        }
        
        # Kibana 최적화 필드 추가
        if kibana_optimized:
            doc['indexed_at'] = datetime.now().isoformat()
            doc['updated_at'] = datetime.now().isoformat()
            
            doc['stats'] = {
                'view_count': 0,
                'search_count': 0,
                'popularity_score': 0.0
            }
            
            # 성분 개수 계산
            raw_materials = doc.get('raw_materials', '')
            if raw_materials:
                doc['ingredient_count'] = len([x.strip() for x in raw_materials.split(',') if x.strip()])
            else:
                doc['ingredient_count'] = 0
            
            doc['metadata']['version'] = '2.0'  # C003 전용 버전
        
        # 임베딩용 텍스트 생성
        doc['embedding_text'] = self._create_embedding_text(doc)
        
        return doc
    
    def _create_embedding_text(self, doc: Dict) -> str:
        """벡터 임베딩용 통합 텍스트 생성 (C003 데이터 기반)"""
        
        parts = []
        
        # 제품명
        if doc.get('product_name'):
            parts.append(f"제품명: {doc['product_name']}")
        
        # 회사명
        if doc.get('company_name'):
            parts.append(f"회사: {doc['company_name']}")
        
        # 제품 형태 (NEW!)
        if doc.get('product_shape'):
            parts.append(f"형태: {doc['product_shape']}")
        
        # 주요 기능
        if doc.get('primary_function'):
            parts.append(f"주요기능: {doc['primary_function']}")
        
        # 원재료
        if doc.get('raw_materials'):
            parts.append(f"원재료: {doc['raw_materials']}")
        
        # 외관/성상 (NEW!)
        product_details = doc.get('product_details', {})
        if product_details.get('appearance'):
            parts.append(f"외관: {product_details['appearance']}")
        
        # 섭취 방법
        intake_info = doc.get('intake_info', {})
        if intake_info.get('method'):
            parts.append(f"섭취방법: {intake_info['method']}")
        
        return " ".join(parts)
    
    def save_to_json(self, data: List[Dict], filename: str):
        """데이터를 JSON 파일로 저장"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"데이터 저장 완료: {filename} ({len(data)}개 문서)")
            
        except Exception as e:
            logger.error(f"파일 저장 오류: {e}")
            raise
    
    def load_from_json(self, filename: str) -> List[Dict]:
        """JSON 파일에서 데이터 로드"""
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"데이터 로드 완료: {filename} ({len(data)}개 문서)")
            
            return data
            
        except Exception as e:
            logger.error(f"파일 로드 오류: {e}")
            raise
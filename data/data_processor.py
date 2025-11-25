import json
from datetime import datetime
from typing import List, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DataProcessor:
    """데이터 전처리 클래스"""
    
    def process_product_data(
        self, 
        products: List[Dict], 
        classifications: List[Dict],
        kibana_optimized: bool = True
    ) -> List[Dict]:
        """API 데이터를 ElasticSearch 문서 형식으로 변환
        
        Args:
            products: 제품 데이터 리스트 (C003)
            classifications: 분류 데이터 리스트 (I2710)
            kibana_optimized: Kibana 최적화 필드 추가 여부
        """
        
        logger.info(f"데이터 전처리 시작 (Kibana 최적화: {kibana_optimized})")
        
        # 데이터 맵핑 생성
        classification_map = {item.get('PRDLST_REPORT_NO'): item for item in classifications}
        
        processed = []
        
        for idx, product in enumerate(products):
            try:
                doc = self._create_document(
                    product, 
                    classification_map,
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
        classification_map: Dict,
        kibana_optimized: bool = True
    ) -> Dict:
        """개별 문서 생성"""
        
        product_id = product.get('PRDLST_REPORT_NO', '')
        company_name = product.get('BSSH_NM', '')
        product_name = product.get('PRDLST_NM', '')
        
        # 고유 ID 생성 (제품번호_회사명)
        unique_id = f"{product_id}_{company_name}"
        
        doc = {
            'product_id': unique_id,
            'product_name': product_name,
            'company_name': company_name,
            'report_date': product.get('PRMS_DT', ''),
            'raw_materials': product.get('RAWMTRL_NM', ''),
            'primary_function': product.get('PRIMARY_FNCLTY', ''),
            'classification': self._get_classification_info(
                product_id, 
                classification_map
            ),
            'metadata': {
                'manufacturer': product.get('MNFTR_NM', ''),
                'distribution_company': product.get('DISPOS', ''),
                'import_declaration': product.get('IMPORT_DECLAR_NO', ''),
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
            
            raw_materials = doc.get('raw_materials', '')
            if raw_materials:
                doc['ingredient_count'] = len([x.strip() for x in raw_materials.split(',') if x.strip()])
            else:
                doc['ingredient_count'] = 0
            
            doc['metadata']['source'] = 'food_safety_api'
            doc['metadata']['version'] = '1.0'
        
        # 임베딩용 텍스트 생성
        doc['embedding_text'] = self._create_embedding_text(doc)
        
        return doc
    
    def _get_classification_info(self, report_no: str, classification_map: Dict) -> Dict:
        """분류 정보 추출"""
        
        if report_no not in classification_map:
            return {}
        
        cls_info = classification_map[report_no]
        
        return {
            'category': cls_info.get('PRDLST_CDNM', ''),
            'detail_category': cls_info.get('STTEMNT_NO', ''),
            'function_content': cls_info.get('FNCLTY_CN', ''),
            'intake_method': cls_info.get('NTK_MTHD', ''),
            'intake_caution': cls_info.get('IFTKN_ATNT_MATR_CN', '')
        }
    
    def _create_embedding_text(self, doc: Dict) -> str:
        """벡터 임베딩용 통합 텍스트 생성"""
        
        parts = []
        
        if doc.get('product_name'):
            parts.append(f"제품명: {doc['product_name']}")
        
        if doc.get('primary_function'):
            parts.append(f"주요기능: {doc['primary_function']}")
        
        if doc.get('raw_materials'):
            parts.append(f"원재료: {doc['raw_materials']}")
        
        classification = doc.get('classification', {})
        if classification.get('function_content'):
            parts.append(f"기능성내용: {classification['function_content']}")
        
        if classification.get('category'):
            parts.append(f"분류: {classification['category']}")
        
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
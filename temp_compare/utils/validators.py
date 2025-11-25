from typing import Optional

def validate_query(query: str, min_length: int = 1, max_length: int = 200) -> tuple[bool, Optional[str]]:
    """쿼리 유효성 검증"""
    
    if not query or not query.strip():
        return False, "검색어를 입력해주세요."
    
    if len(query) < min_length:
        return False, f"검색어는 최소 {min_length}자 이상이어야 합니다."
    
    if len(query) > max_length:
        return False, f"검색어는 최대 {max_length}자까지 입력 가능합니다."
    
    return True, None

def validate_top_k(top_k: int, min_value: int = 1, max_value: int = 20) -> tuple[bool, Optional[str]]:
    """top_k 파라미터 검증"""
    
    if top_k < min_value or top_k > max_value:
        return False, f"결과 개수는 {min_value}~{max_value} 사이의 값이어야 합니다."
    
    return True, None
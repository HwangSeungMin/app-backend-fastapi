"""
검색 기능 테스트
"""
import pytest
from search.rag_search import RAGSearchEngine

@pytest.fixture
def search_engine():
    return RAGSearchEngine()

def test_hybrid_search(search_engine):
    """하이브리드 검색 테스트"""
    results = search_engine.hybrid_search('비타민', top_k=3)
    
    assert isinstance(results, list)
    assert len(results) <= 3
    
    if results:
        assert 'product_name' in results[0]
        assert 'score' in results[0]

def test_symptom_search(search_engine):
    """증상 검색 테스트"""
    results = search_engine.search_by_symptom('피로', top_k=3)
    
    assert isinstance(results, list)

def test_ingredient_search(search_engine):
    """성분 검색 테스트"""
    results = search_engine.search_by_ingredient('철분', top_k=5)
    
    assert isinstance(results, list)
"""
API 엔드포인트 테스트
"""
import pytest
from api.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """헬스 체크 테스트"""
    response = client.get('/api/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True

def test_hybrid_search(client):
    """하이브리드 검색 테스트"""
    response = client.post('/api/search/hybrid', json={
        'query': '비타민',
        'top_k': 3
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data

def test_symptom_search(client):
    """증상 검색 테스트"""
    response = client.post('/api/search/symptom', json={
        'symptom': '피로',
        'top_k': 3
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_invalid_request(client):
    """잘못된 요청 테스트"""
    response = client.post('/api/search/hybrid', json={
        'top_k': 3
        # query 누락
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
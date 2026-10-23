from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get('/health').json() == {'status': 'ok'}

def test_evaluation_requires_context():
    assert client.post('/v1/evaluate', json={'question':'q','answer':'a'}).status_code == 422

def test_evaluation_review():
    response = client.post('/v1/evaluate', json={'question':'Capital?','answer':'Paris','context':'Paris is the capital of France'})
    assert response.status_code == 200
    assert response.json()['verdict'] == 'review'

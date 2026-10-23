from fastapi.testclient import TestClient
from app.main import app
from app.judge import JudgeOutput

client = TestClient(app)

def test_judge_requires_provider(monkeypatch):
    monkeypatch.delenv('JUDGE_API_KEY', raising=False)
    monkeypatch.delenv('JUDGE_MODEL', raising=False)
    r = client.post('/v1/judge', json={'question':'q','answer':'a','context':'c'})
    assert r.status_code == 503

def test_judge_mock_provider(monkeypatch):
    import app.main as main
    monkeypatch.setattr(main, 'judge', lambda *args: JudgeOutput(score=0.9, verdict='pass', rationale='Supported', evidence=['context']))
    r = client.post('/v1/judge', json={'question':'q','answer':'a','context':'c'})
    assert r.status_code == 200 and r.json()['score'] == 0.9

def test_unknown_rubric_rejected():
    r = client.post('/v1/judge', json={'question':'q','answer':'a','context':'c','rubric':'made-up'})
    assert r.status_code == 422

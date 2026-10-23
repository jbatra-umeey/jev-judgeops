import json
import httpx
import pytest
import app.judge as module
from fastapi.testclient import TestClient
from app.main import app

REAL_CLIENT = httpx.Client
VALID = {'score': 0.9, 'verdict': 'pass', 'rationale': 'Supported', 'evidence': ['Paris']}

@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv('JUDGE_API_KEY', 'test-key-not-a-secret')
    monkeypatch.setenv('JUDGE_MODEL', 'test-model')
    monkeypatch.setenv('JUDGE_BASE_URL', 'https://judge.invalid/v1/')
    def install(handler):
        monkeypatch.setattr(module.httpx, 'Client', lambda **kw: REAL_CLIENT(transport=httpx.MockTransport(handler), **kw))
    return install

def test_provider_request_and_output(provider):
    def handler(req):
        assert str(req.url) == 'https://judge.invalid/v1/chat/completions'
        assert req.headers['Authorization'] == 'Bearer test-key-not-a-secret'
        payload = json.loads(req.content)
        assert payload['model'] == 'test-model'
        assert payload['response_format'] == {'type': 'json_object'}
        assert module.RUBRICS['groundedness'] in payload['messages'][0]['content']
        assert 'Paris' in payload['messages'][1]['content']
        return httpx.Response(200, json={'choices': [{'message': {'content': json.dumps(VALID)}}]})
    provider(handler)
    assert module.judge('Capital?', 'Paris', 'Paris').model_dump() == VALID

@pytest.mark.parametrize('body', [None, {}, {'choices': []}, {'choices': None}, {'choices': [{'message': None}]}, {'choices': [{'message': {'content': None}}]}])
def test_malformed_envelope_fails_closed(provider, body):
    provider(lambda req: httpx.Response(200, content=json.dumps(body)))
    with pytest.raises(module.JudgeUnavailable):
        module.judge('q', 'a', 'c')

@pytest.mark.parametrize('content', ['not json', '{}', json.dumps({**VALID, 'score': 2}), json.dumps({**VALID, 'score': '0.9'}), json.dumps({**VALID, 'extra': 'field'}), json.dumps({**VALID, 'verdict': 'unknown'})])
def test_invalid_judgment_fails_closed(provider, content):
    provider(lambda req: httpx.Response(200, json={'choices': [{'message': {'content': content}}]}))
    with pytest.raises(module.JudgeUnavailable):
        module.judge('q', 'a', 'c')

@pytest.mark.parametrize('status', [401, 429, 500])
def test_provider_http_errors(provider, status):
    provider(lambda req: httpx.Response(status, text='private upstream detail'))
    with TestClient(app) as client:
        response = client.post('/v1/judge', json={'question':'q','answer':'a','context':'c'})
    assert response.status_code == 503
    assert 'private upstream detail' not in response.text
    assert 'test-key' not in response.text

def test_timeout_fails_closed(provider):
    def handler(req):
        raise httpx.ReadTimeout('timeout', request=req)
    provider(handler)
    with pytest.raises(module.JudgeUnavailable):
        module.judge('q', 'a', 'c')

def test_request_limit():
    with TestClient(app) as client:
        assert client.post('/v1/judge', json={'question':'q','answer':'a'*50001,'context':'c'}).status_code == 422

def test_rubrics_and_baseline_failure():
    with TestClient(app) as client:
        assert set(client.get('/v1/rubrics').json()) == set(module.RUBRICS)
        r = client.post('/v1/evaluate', json={'question':'q','answer':'Rome','context':'Paris'})
    assert r.json()['verdict'] == 'fail'
    assert r.json()['score'] == 0

# Jev JudgeOps

A FastAPI demonstration of LLM-as-a-Judge with rubric selection, structured output
validation, fail-closed provider errors and a separate deterministic baseline.
**Status: executable demonstration; production hardening remains incomplete.**

## Included

- `/health`: process liveness (does not check provider readiness).
- `/v1/rubrics`: groundedness, relevance, safety and trajectory rubric prompts.
- `/v1/evaluate`: lexical overlap baseline, returning review or fail.
- `/v1/judge`: configured OpenAI-compatible chat-completions provider, JSON output
  validation and HTTP 503 for missing configuration or invalid provider output.
- Docker/Compose setup, automated tests, GitHub Actions and architecture diagrams.

No semantic judgment is fabricated when a provider is unavailable. The baseline
is not an LLM judge, and neither schema validation nor a passing test establishes
judgment accuracy.

## Local run (Python 3.12)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For a live judge, export `JUDGE_API_KEY`, `JUDGE_MODEL` and optionally
`JUDGE_BASE_URL` in your shell before starting the service. Direct Python runs do
not automatically load `.env`. Provider support for JSON mode and temperature
zero must be checked against the chosen model.

## Docker

```bash
cp .env.example .env
# Edit .env with your provider credentials and model ID; never commit it.
docker compose up --build --wait
```

Compose passes the configured variables into the container and binds port 8000
to localhost. The API runs as a non-root user with a read-only root filesystem.
API documentation: http://localhost:8000/docs

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/v1/judge \
  -H 'Content-Type: application/json' \
  -d '{"question":"Capital of France?","answer":"Paris","context":"Paris is the capital of France.","rubric":"groundedness"}'
```

Use `/v1/evaluate` with the same body for the offline baseline. Example input is
in `datasets/examples.jsonl`. This is illustrative input, not a calibration set.
The LLM endpoint sends input text to the configured external model provider.

## Validation

```bash
python -m pytest -q
python -m compileall -q app tests
docker compose config --quiet
```

CI runs unit/API tests and a container health/API smoke test. Tests use mocked
HTTP provider responses and make no paid model calls. See
[validation evidence](docs/VALIDATION.md) for checks actually executed and limits.

## Documentation

- [Architecture and diagrams](docs/ARCHITECTURE.md)
- [Production readiness work](docs/PRODUCTION_READINESS.md)
- [Validation evidence](docs/VALIDATION.md)

Persistence, authentication, queues, UI, human calibration, production observability
and DecisionOps/EvalOps/MCP Nexus adapters remain unimplemented. Lexical overlap
is not a reliable truth metric. Do not use it alone as a deployment approval gate.

# Validation evidence

Executed on 2026-10-23 with Python 3.12.14 in a fresh virtual environment.

| Check | Result |
| --- | --- |
| `python -m pytest -q` | 25 passed in 0.59 seconds; one Starlette TestClient deprecation warning |
| `python -m compileall -q app tests` | Passed |
| `python -m pip check` | No broken requirements found |
| Compose and Actions YAML parsing | Passed with PyYAML; not Docker semantic validation |
| Local Docker build / Compose runtime | Not run: Docker is not installed in the execution environment |
| Live model-provider request | Not run: no provider credentials supplied |
| Hosted GitHub Actions | Workflow configured; result must be checked after publication |

Tests cover API validation, baseline review/failure, rubric discovery, provider
configuration, request construction, valid structured output, malformed envelopes,
invalid scores/verdicts, unknown fields, HTTP 401/429/500, timeouts and generic
client-facing errors. Provider transport is mocked; no judgment accuracy is proven.

The warning advises migration away from Starlette's HTTPX TestClient integration.
Dependency ranges are not a reproducible lock; resolve and lock approved versions
before production deployment.

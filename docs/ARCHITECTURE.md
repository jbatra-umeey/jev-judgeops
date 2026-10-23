# Architecture

## Implemented request flow

```mermaid
flowchart TD
    C[API client] --> V[FastAPI and Pydantic validation]
    V --> E[Lexical overlap evaluator]
    V --> J[Rubric judge adapter]
    J --> P[Configured external model provider]
    P --> S[Strict output schema validation]
    S --> R[Judgment response]
    J --> F[503 on configuration or provider error]
    E --> B[Baseline response]
```

`app/main.py` exposes health, rubric discovery and two evaluation endpoints.
`app/judge.py` makes one synchronous HTTP request with a 30-second HTTPX timeout.
The judge uses temperature zero and requests JSON output. Returned scores must be
between zero and one; verdicts are pass/fail/review. This checks structure, not
correctness. Evidence strings are not independently checked against the context.
The baseline measures ASCII token overlap and never returns pass.

## Deployment and trust boundaries

```mermaid
flowchart TD
    H[Local client] --> L[Loopback port 8000]
    L --> A[Non-root API container]
    A --> M[External model API]
    E[Environment configuration] --> A
```

Compose binds only to localhost. No database, queue, dashboard, authentication or
persistent audit log exists. The health endpoint reports process liveness, not
model availability. User question, context and answer leave the deployment when
`/v1/judge` calls the configured provider. The server operator controls provider
URL and credentials; callers cannot override them through the API.

Request fields have a 50,000-character limit each. This is not a transport-level
body limit. Prompts label submitted content as untrusted, but that does not prove
resistance to prompt injection. A valid schema is not evidence of judge accuracy.

## Proposed production architecture (not implemented)

```mermaid
flowchart TD
    C[Client] --> G[Authenticated gateway and quotas]
    G --> Q[Durable evaluation queue]
    Q --> W[Isolated judge workers]
    W --> M[Allowlisted model gateway]
    W --> D[Evaluation database and audit log]
    W --> O[Metrics and traces]
    D --> H[Human calibration and review]
```

See [production readiness](PRODUCTION_READINESS.md) for the remaining work.

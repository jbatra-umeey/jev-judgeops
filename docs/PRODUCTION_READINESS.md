# Production readiness

This repository is an executable demonstration, not a production certification.

Before serving external traffic:

- Implement authentication, authorization and tested tenant isolation.
- Add ingress body limits, per-tenant rate limits, budgets and bounded concurrency.
- Restrict provider egress and model selection; validate provider configuration.
- Integrate a secret manager, key rotation, privacy controls and data retention.
- Persist rubric/model versions, input hashes, immutable judgments and audit events.
- Add durable jobs, cancellation, retry policy, idempotency and backpressure.
- Establish human-labeled calibration sets, agreement metrics, position-bias tests,
  adversarial prompt-injection tests and independent evidence verification.
- Define score/verdict consistency rules and operational review thresholds.
- Add tracing, metrics, readiness checks, alerting, SLOs and load/soak tests.
- Lock dependencies, scan vulnerabilities, produce SBOMs, pin image/action digests,
  sign releases, configure branch protection and select an appropriate license.
- Verify live-provider compatibility and complete Docker runtime validation.

A Next.js UI, orchestration, integration adapters and experiment dashboards are
roadmap items. They are not present in this source archive.

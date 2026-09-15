# Agentflow

Reusable, sequential Python orchestration for one feature at a time. The orchestrator alone owns routing; agents return validated Pydantic JSON and never launch one another.

```text
DEVELOPMENT -> TESTING -> REVIEW -> DONE
                  ^          |
                  |          +-- developer -> TESTING -> REVIEW
                  +-- tester +-- both -> developer -> TESTING
```

Routes are `developer`, `tester`, `reviewer`, `both`, `done`, and `human_required`. Any invalid result, exception, timeout, blocked approval, or iteration overflow stops safely at `HUMAN_REQUIRED`. Production changes therefore cannot bypass Tester.

Install with `cd .agentflow && python -m pip install -e .`. Use `agentflow doctor`, `agentflow mock --scenario happy`, and `agentflow run feature.md`. Runtime JSON and append-only events live in `.agentflow/runtime/`; `agentflow status` inspects them and `agentflow reset` only clears runtime state.

Customize `roles/developer.md`, `roles/tester.md`, and `roles/reviewer.md`. Framework-specific commands and coverage policy belong in Tester’s role/configuration, not this engine. This supports Go, Python, Java, Node, or other stacks without changes to routing.

The current project role rules specialize this repository for a Python/Django cinema application using Django ORM, layered controller/service/repository architecture, DTOs, entities, mappers, SOLID principles, Docker Compose infrastructure under `infra/local/docker-compose.yaml`, PostgreSQL, RabbitMQ, Redis, Testcontainers integration tests, HTTP tests, E2E tests, and a 90% coverage requirement. Use a `justfile` for convenient repeatable commands.

The selected resume-friendly defaults are Django REST Framework with Django ORM, `djangorestframework-simplejwt` for JWT authentication, `drf-spectacular` for OpenAPI/Swagger, a project-owned RFC 7807 exception handler, `django-health-check`, `python-json-logger`, `django-prometheus`, OpenTelemetry Python instrumentation, `testcontainers`, `pika`, and `redis` (redis-py). JWTs may contain trusted role claims and administrative endpoints use explicit DRF role-based permissions. These are defaults for consistency, not invitations to add multiple competing libraries.

This repository uses Django migrations as the single authoritative database migration system. Model changes must use Python migration files under the relevant app's `migrations/` directory. Use `just makemigrations` to generate migrations, `just migrate` to apply them locally, `just migrate-docker` to apply them inside the Compose API container, and `just migrate-check` to detect model changes that have not been captured.

The project observability rules require structured logs, metrics, and distributed traces. Use OpenTelemetry-compatible instrumentation and collect Docker-container telemetry with Grafana Alloy. The intended local stack is Grafana for dashboards, Loki for logs, Prometheus for metrics, Tempo for traces, and Alloy as the collector/forwarder. Keep observability configuration under the infrastructure area when it is implemented, add health/readiness checks, propagate request and message correlation IDs, and never log secrets or sensitive personal data.

Application services must expose an Actuator-like operational surface: `/health/live`, `/health/ready`, `/metrics`, and `/info`. Logs must be JSON written to stdout/stderr, with timestamp, level, service, and correlation identifiers where available. Liveness must not depend on external services; readiness checks required dependencies. Metrics must be Prometheus-compatible, traces and metrics should use OpenTelemetry, and operational endpoints must be tested and protected appropriately.

API error handling follows RFC 7807 with `application/problem+json`. Repositories raise domain-specific errors, services catch and translate them into application outcomes, and a centralized Django exception handler performs the HTTP response mapping. Repositories, services, and controllers must not contain HTTP-status exception logic. Successful APIs use consistent Google-style resource-oriented JSON representations and pagination conventions.

Public Python code should use accurate typed docstrings, similar in purpose to JavaDoc. REST APIs should publish generated OpenAPI documentation with Swagger UI or an equivalent viewer. The schema must document request/response bodies, authentication, pagination, examples, and RFC 7807 errors. Prefer the project’s existing tooling; for Django REST Framework without an existing choice, use `drf-spectacular`.

Codex 0.9-style `codex exec` is used through `CodexAdapter` with workspace-write and no auto-approval. Session IDs are stored in `runtime/sessions.json`; configured IDs use `codex exec resume <id>`, while missing IDs use one-shot ephemeral mode. `agentflow setup` initializes the registry without inventing IDs. Herdr 0.9.0 provides agent prompt/wait/session commands; `HerdrAdapter` remains the extension point for named Herdr panes. Notifications use `notify-send` when available and never affect pipeline success.

There is no automatic commit, merge, worktree, permission approval, phone push, or safe resume yet. Recover HUMAN_REQUIRED by inspecting `current_run.json` and `events.jsonl`, resolving the human issue, then starting a new run; add resume only when the persisted context is unambiguous.

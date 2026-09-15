# Cinema

A cinema reservation and ticketing platform designed as a production-style Django application. The project is being built as a portfolio project with a focus on clean architecture, reliable booking behavior, observability, and well-defined API contracts.

The initial foundation is in place. Business domains are being introduced incrementally, starting with the movie catalog.

## Project overview

Cinema is a cinema management and ticketing platform designed around a
modular Django backend. The system is intended to support the complete movie
discovery and ticket-purchasing lifecycle through secure REST APIs.

The planned business capabilities include:

- Movie catalog and metadata management
- Cinema, auditorium, seat, and screening management
- Customer seat selection and temporary reservation holds
- Shopping carts and order processing
- Payment lifecycle integration
- JWT authentication with role-based authorization
- Separate customer and administrative API workflows

Temporary seat reservations will use an expiration timestamp and transactional
protection to prevent conflicting bookings. This concern is intentionally
separated from the initial movie catalog model.

## Technology stack

### Application

- Python 3.12+
- Django 5.2+
- Django REST Framework
- Django ORM
- PostgreSQL
- Layered architecture: API/controller, service, repository, DTO, entity, and mapper layers
- SOLID-oriented design

### Infrastructure

Local infrastructure runs through Docker Compose under `infra/local/docker-compose.yaml`:

- PostgreSQL 18.6 Alpine
- Redis 8.10.1 Alpine
- RabbitMQ 4.3.5 Management Alpine
- Django API served by Gunicorn

The application uses port `8000` locally. PostgreSQL, Redis, and RabbitMQ are not expected to be installed directly on the host machine.

### API and security

- JWT authentication with `djangorestframework-simplejwt`
- Role-based permissions for administrative endpoints
- RFC 7807 error responses using `application/problem+json`
- Centralized Django exception handling
- OpenAPI schema and Swagger UI using `drf-spectacular`
- Sphinx-generated internal Python documentation
- Resource-oriented JSON success responses

Repositories and services do not contain HTTP status-code logic. Repositories raise domain errors, services handle application decisions, and the transport exception handler maps failures to HTTP responses.

### Observability

The local observability stack consists of:

- Grafana 13.2.2
- Loki 3.7.7 for logs
- Prometheus 3.14.0 for metrics
- Tempo 3.0.3 for traces
- Grafana Alloy 1.19.2 for collection and forwarding
- OpenTelemetry for application instrumentation
- JSON logging to stdout/stderr

The intended flow is:

```text
Django API -> Grafana Alloy -> Loki       -> Grafana
           -> Grafana Alloy -> Prometheus -> Grafana
           -> Grafana Alloy -> Tempo      -> Grafana
```

Operational endpoints:

```text
GET /health/live   Process liveness only
GET /health/ready  Dependency readiness, without dependency details
GET /metrics       Prometheus metrics
GET /info          Safe service metadata
GET /api/docs/     Swagger UI when enabled by configuration
```

`/health/live` remains available when PostgreSQL, Redis, or RabbitMQ is down. `/health/ready` returns `503` when required dependencies are unavailable and does not expose their names publicly.

## Configuration

Configuration is YAML-based and profile-aware:

```text
config/application.yaml       Common defaults
config/application.local.yaml Local development profile
config/application.dev.yaml   Development profile
```

Select a profile with:

```bash
APP_PROFILE=local
```

The container mounts the configuration directory at `/etc/cinema`. An alternative file or directory can be supplied with `APP_CONFIG_FILE` or `APP_CONFIG_DIR`.

Secrets and local overrides belong in environment variables or an ignored `.env` file. `.env.example` documents the expected values.

## Database migrations

Django migrations are the single authoritative database migration system. Models are defined in Python and migrations are generated from them.

The current catalog model preparation includes movies, languages, actors, screenplays, genres, countries, studios, directors, and movie relationship tables.

No catalog migration has been generated or applied yet. Review `src/core/models.py` and `docs/catalog-schema-review.md` first.

The normal development workflow uses two commands:

```bash
just makemigrations
just migrate
```

Use these optional verification/deployment commands when needed:

```text
just migrate-check   # Confirm model changes have a migration
just migrate-docker  # Apply migrations inside the running API container
```

The schema will grow incrementally as the catalog, screenings, booking holds,
carts, orders, and payments domains are implemented. Django will create the
appropriate numbered migration files automatically; the numbers are not
manually planned or maintained in advance.

Do not use a second migration system for the same tables.

## Local development

Install the Python project dependencies, then start the local stack:

```bash
python -m pip install -e '.[dev,integration]'
just up
just health
```

Common commands:

```bash
just up                 # Start the local Compose stack
just down               # Stop the stack
just logs               # Follow service logs
just test               # Run unit and project tests
just test-integration   # Run Testcontainers integration tests
just test-e2e           # Run E2E tests
just coverage           # Run tests with the 90% threshold
just lint               # Run Ruff checks
just format             # Format Python code
just observability      # Inspect observability services
```

Useful local URLs:

```text
API:         http://localhost:8000
Swagger UI:  http://localhost:8000/api/docs/
Grafana:     http://localhost:3000
Prometheus:  http://localhost:9090
Loki:        http://localhost:3100
Tempo:       http://localhost:3200
RabbitMQ:    http://localhost:15672
```

## Documentation

Sphinx generates static HTML documentation from Python docstrings and type
hints. Install the documentation dependencies and build it with:

```bash
python -m pip install -e '.[docs]'
just docs
```

The generated site is written to `build/docs/index.html`. Serve it locally with:

```bash
just docs-serve
```

Then open `http://localhost:8080`. Internal Python documentation is separate
from the generated REST API documentation at `/api/docs/`.

## Testing approach

The project is intended to contain unit tests, PostgreSQL/Redis/RabbitMQ integration tests using Testcontainers, HTTP contract tests, end-to-end tests, and at least 90% measured code coverage.

The application’s own test suite uses pytest. This does not prescribe which testing tools future feature-specific agent rules may use in another project.

## Agentflow

`.agentflow/` contains the reusable Developer/Tester/Reviewer orchestration framework. It runs agents sequentially against the same working tree:

```text
Developer -> Tester -> Reviewer -> DONE
                 ^        |
                 |        +-- production issue -> Developer -> Tester
                 +----------- test issue -------> Tester
```

The orchestrator owns all routing. Any production-code change must pass through Tester before Reviewer can approve it. Herdr manages persistent agent sessions when available; Codex communication is hidden behind adapters.

Customize the project-specific rules here:

```text
.agentflow/roles/developer.md
.agentflow/roles/tester.md
.agentflow/roles/reviewer.md
```

See [.agentflow/README.md](.agentflow/README.md) for Agentflow setup, persistent sessions, mock mode, runtime state, and recovery procedures.

## Current status

Implemented foundation:

- Django project and two-stage application Dockerfile
- Docker Compose local infrastructure
- YAML profile configuration
- Health, readiness, metrics, and info endpoints
- JWT and role-permission foundation
- OpenAPI/Swagger configuration
- JSON logging and OpenTelemetry foundation
- Grafana, Loki, Prometheus, Tempo, and Alloy setup
- Initial catalog model design
- Agentflow orchestration framework

Not implemented yet:

- Catalog migration generation/application
- Screening and seat inventory domain
- Five-minute booking holds
- Carts, orders, and payments
- Customer-facing business APIs

No automatic commits, merges, Git resets, permission approvals, or destructive database operations are performed by the development agents.

# Local Docker Compose project used for the API and supporting services.
compose := "docker compose -f infra/local/docker-compose.yaml"

# Start the local application and infrastructure stack in the background.
up:
    {{compose}} up -d

# Stop containers without deleting persistent Docker volumes.
down:
    {{compose}} down

# Follow the latest logs from all local services.
logs:
    {{compose}} logs -f --tail=200

# Run the complete application test suite.
test:
    python -m pytest -q

# Run tests marked as integration tests.
test-integration:
    python -m pytest -q tests/integration/testcontainers_smoke.py -m integration

# Run tests marked as end-to-end tests.
test-e2e:
    python -m pytest -q -m e2e

# Generate Django migrations from model changes using the host-published database port.
makemigrations:
    POSTGRES_HOST=localhost python manage.py makemigrations

# Apply pending Django migrations using the host-published database port.
migrate:
    POSTGRES_HOST=localhost python manage.py migrate

# Fail if model changes exist without a migration.
migrate-check:
    python manage.py makemigrations --check --dry-run

# Apply migrations inside the running Docker Compose API container.
migrate-docker:
    {{compose}} exec api python manage.py migrate

# Run tests and enforce the project's 90% coverage threshold.
coverage:
    python -m coverage run -m pytest && python -m coverage report --fail-under=90

# Run Ruff static checks.
lint:
    python -m ruff format --check .

# Format Python source files with Ruff.
format:
    python -m ruff format .

# Build internal Python/API documentation with Sphinx.
docs:
    python -m sphinx -b html docs build/docs

# Serve the generated Sphinx HTML documentation locally.
docs-serve:
    python -m http.server 8080 --directory build/docs

# Check application liveness and dependency readiness.
health:
    curl --fail --retry 30 --retry-all-errors --retry-delay 1 http://localhost:8000/health/live
    curl --fail --retry 30 --retry-all-errors --retry-delay 1 http://localhost:8000/health/ready

# Show service status and verify the main observability endpoints.
observability:
    docker ps -a --format "$(printf 'table \173\173.Names\175\175\011\173\173.Image\175\175\011\173\173.ID\175\175\011\173\173.Status\175\175')"
    curl --fail --retry 30 --retry-all-errors --retry-delay 1 http://localhost:3000/api/health
    curl --fail --retry 30 --retry-all-errors --retry-delay 1 http://localhost:9090/-/healthy
    curl --fail --retry 30 --retry-all-errors --retry-delay 1 http://localhost:3100/ready
    curl --fail --retry 30 --retry-all-errors --retry-delay 1 http://localhost:3200/ready

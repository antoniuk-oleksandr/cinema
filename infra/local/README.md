# Local infrastructure

`docker compose -f infra/local/docker-compose.yaml up -d` starts PostgreSQL, Redis, RabbitMQ, Prometheus, Loki, Tempo, Grafana, and Grafana Alloy.

The future Django service should expose `/metrics` on port 8000 and send OTLP telemetry to Alloy at `http://localhost:4317` (gRPC) or `http://localhost:4318` (HTTP). Alloy collects Docker logs and forwards logs to Loki, metrics to Prometheus, and traces to Tempo.

Application configuration is committed YAML. The loader reads `config/application.yaml`, then overlays `config/application.<APP_PROFILE>.yaml` (default profile: `local`). To provide a different file through Docker, set `APP_CONFIG_FILE=/etc/cinema/application.custom.yaml` and mount the directory containing that file at `/etc/cinema`.

Grafana is available at http://localhost:3000. Default local credentials are `admin` / `admin-local-only` unless overridden through `.env`; change them before sharing the environment.

The Docker socket is mounted read-only for container log discovery. This is convenient for local development but should be reviewed carefully for production deployments.

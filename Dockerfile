FROM python:3.12-slim AS build
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 VIRTUAL_ENV=/opt/venv PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential \
    && python -m venv "$VIRTUAL_ENV" \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
COPY manage.py ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

FROM python:3.12-slim AS run
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src VIRTUAL_ENV=/opt/venv PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=build /opt/venv /opt/venv
COPY --from=build /app/manage.py ./
COPY --from=build /app/src ./src
RUN chown -R app:app /app /opt/venv
USER app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-"]

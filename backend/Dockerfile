# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages ./packages
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable

FROM python:3.13-slim-bookworm
RUN useradd --create-home --uid 1000 ecokaz
COPY --from=build --chown=ecokaz:ecokaz /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
USER ecokaz
EXPOSE 8000
# Apply pending migrations, then serve. Migrations are idempotent (tested).
CMD ["sh", "-c", "python -m ecokaz_api.migrate && exec uvicorn ecokaz_api.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]

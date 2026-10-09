# Ecokaz

The household energy and carbon copilot: actual electricity, gas, water and fuel use, in units, euros and kgCO₂e, with an AI coach that explains and suggests actions.

> **Status: V0 in progress (lot 0, foundation, done).** Personal use first, mainland France. See [`PLAN.md`](PLAN.md).

## Getting started

```bash
cp .env.example .env      # then change the values
make setup                # dependencies + commit-msg hook
make check                # lint, types, tests
make dev-api              # API on :8001
make dev-web              # UI on :5174
make up                   # full stack on https://localhost:8453
```

Requirements: Docker, [uv](https://docs.astral.sh/uv/), Node (via fnm) and pnpm.

## Stack

FastAPI · SQLAlchemy · Alembic · PostgreSQL 17 · React · TypeScript · Vite · Tailwind · Caddy · Docker Compose.

## Data and factor sources

- Electricity: Enedis, through [Conso API](https://conso.boris.sh/) or a CSV export from the customer area.
- Emission factors: ADEME, Base Empreinte. Every value is versioned with its source.

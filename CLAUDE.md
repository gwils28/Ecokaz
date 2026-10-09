# CLAUDE.md

Ecokaz — self-hosted web app that tracks a household's electricity, gas, water and fuel use, its cost and its carbon footprint, with an AI coach. FastAPI + PostgreSQL backend (uv workspace), React + TypeScript frontend. Mobile app only in V2: build for the responsive web.

- Plan, scope and lots: `PLAN.md` (log every deviation in its §8). Original product spec: `Ecokaz_spec.md` (private, git-ignored: may be absent).
- Scaffold derived from the maintainer's Kwak Finance project (commit 7d67666): same conventions.

## Commands

- `make check` — everything CI runs (ruff, mypy strict, pytest, Biome, tsc, Vitest). `make check-fast` is what the Stop hook runs.
- `make dev-api` / `make dev-web` — API on :8001, Vite on :5174 (proxies `/api`).
- `make up` — full stack on https://localhost:8453 (needs `.env`, copy `.env.example`).
- Node comes from fnm; if `pnpm` is not found, run `eval "$(fnm env)"`.
- Backend commands run from `backend/` (uv workspace root), frontend ones from `frontend/`.
- DB tests use testcontainers: Docker must be running.

## Rules

- **Never commit or push.** The maintainer must be the sole GitHub contributor (public repo). Prepare the change and propose a Conventional Commit message (skill `prepare-commit`). One topic per commit. Never add a `Co-Authored-By` trailer.
- Code, docs and commit messages in English; the UI is in French.
- **The LLM never computes a number.** kWh, m³, km, €, kgCO₂e, forecasts and simulations come from tested functions in `ecokaz_core`; the coach calls them as tools and explains the result. Otherwise the coach can state numbers nobody can check.
- **No emission factor, price or conversion coefficient in code.** They live in one versioned table with source (ADEME Base Empreinte, …) and validity dates, so every figure can be traced back to its source.
- Every data source (Conso API, Enedis CSV, manual meter index) implements the same source interface and yields normalised readings: adding a source must not touch storage or the dashboard.
- Readings are half-open intervals `[start, end)` in UTC. Quantities and money are `Decimal` / `NUMERIC`, never float. Meter indexes must not decrease (reject, do not clamp).
- Business rules go in `backend/packages/core` (pure, no I/O) and are tested there, with hypothesis property tests for invariants.
- Write the failing test first, check it fails for the right reason, then implement.
- `data/` holds real household data: never read it into the conversation unless asked, and never write to it. Test fixtures must be synthetic.
- UI colours come from the tokens in `frontend/src/styles/tokens.css` (blog charter, scheme "mousse"). Do not introduce ad-hoc hex values.
- Enedis legacy APIs close mid-October 2026: target Conso API with Token V3 / Metering Data V5 only.

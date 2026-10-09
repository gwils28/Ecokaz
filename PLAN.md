# Ecokaz — V0 plan

> Status: **approved on 2026-10-09**. Name: Ecokaz. Public GitHub repository.
> Last updated: 2026-10-09 — lot 0 done.

## 1. V0 promise

For **my household** (mainland France), in one place:
see my actual electricity, gas, water and fuel use in **units, € and kgCO₂e**,
compare it with my baseline carbon footprint, and get warned when something drifts.

V0 success criterion: I open it every week for 2 months and have made at least one decision because of it.

## 2. Scope

| In V0 | Out of V0 (later) |
|---|---|
| Household profile (dwelling, floor area, build year, occupants, heating, vehicles) | Bill OCR |
| Quick self-reported carbon footprint at onboarding (≈ 15 questions) | Social benchmark, multi-household |
| Electricity: Conso API connector (Enedis Metering V5) + Enedis CSV import | Full "what-if" simulations |
| Gas, water, car mileage: manual meter/odometer readings | ML forecasting (after 3 months of data) |
| User-entered tariffs → € | Gamification, badges |
| Dashboard: day / week / month / year, per category | Freemium, payments |
| Reduction goals + progress tracking | Mobile app (V2), push notifications |
| Spike detection (simple, explained statistical method) | RAG over a document corpus |
| Coach: deterministic rules + Mistral to explain and answer | |

## 3. Non-negotiable principles

1. **The LLM never computes.** Every figure comes from tested Python functions; the coach calls them (tool calling) and comments on them.
2. **Versioned, sourced emission factors** (ADEME Base Empreinte), in a single table with the source and validity date of each value. No hard-coded figures.
3. **One data source = one adapter** behind a common interface (`fetch() → normalised readings`). Adding a source touches neither storage nor the dashboard.
4. **Baseline before model**: anomalies first with simple statistical rules; ML only if it beats them on a protocol written in advance.
5. **Personal data**: EU hosting, secrets out of the repo, encrypted backups, export and deletion available.

## 4. Architecture (modular monolith)

```
Responsive React web app (Vite, TS, Tailwind, gwils28 charter) — mobile in V2
        │ HTTPS (Caddy)
FastAPI ─┬─ domain/      pure computations: consumption, €, CO₂e, anomalies, goals   ← tested core
         ├─ sources/     linky_api, linky_csv, manual_index
         ├─ coach/       rules + Mistral client (tool calling on domain/)
         ├─ api/         REST routes, auth
         └─ jobs/        daily Linky sync (APScheduler, no Celery)
PostgreSQL 17 (no TimescaleDB: ~17,500 points/year at 30 min, plain Postgres is enough)
```

Deployment: Docker Compose on an EU VPS (Hetzner or Scaleway, ≈ €5/month), Caddy for HTTPS, daily encrypted `pg_dump`.
Tooling: `uv` + `ruff` + `pytest` (backend), `pnpm` + `vitest` + Playwright (frontend), GitHub Actions CI.

### Data model (first version)

- `household` (profile), `user`
- `meter` (kind: elec / gas / water / vehicle; unit; source)
- `reading` (meter_id, ts_start, ts_end, value, unit, source, imported_at), unique on (meter, ts_start, ts_end)
- `tariff` (meter, validity period, standing charge, unit price, peak/off-peak)
- `emission_factor` (category, value, unit, source, validity date)
- `footprint_survey` (self-reported answers + result)
- `goal` (category, reference period, target in %)
- `alert` (meter, period, kind, severity, explanation)

Manual readings (gas, water, km) become consumption over the interval between two readings, without inventing any split within the interval.

## 5. Lots (each ends with proof)

| # | Lot | Proof of completion |
|---|---|---|
| 0 ✅ | Foundation: git, uv, pnpm, Docker Compose, CI, CLAUDE.md, hooks | `docker compose up` + green CI |
| 1 | Domain: conversions, €, CO₂e, readings → consumption (test-first) | green property tests (non-negativity, additivity, decreasing index rejected) |
| 2 | Electricity: Enedis CSV import + Conso API V5 connector + daily sync | my real load curve imported, quality checks (gaps, duplicates, units) passed |
| 3 | Auth (household account) + frontend: charter, onboarding/profile, electricity dashboard | browser screenshots, desktop and narrow screen, light and dark |
| 4 | **VPS deployment** (early, to use it daily) | reachable HTTPS URL, backup restore tested |
| 5 | Gas, water, car (manual readings) + tariffs + multi-category dashboard | totals consistent with my bills (gap explained) |
| 6 | Self-reported footprint + reported vs measured comparison | result compared with Nos Gestes Climat on my profile, gap explained |
| 7 | Goals + spike detection (robust day-of-week baseline) | tests on synthetic series (injected spike detected, flat series without false alarm) |
| 8 | Coach: rules, then Mistral tool calling, with an evaluation set written **before** the prompts | versioned eval set, no hallucinated figure |

Estimate, at an evenings-and-weekends pace: lots 0–4 ≈ 3–4 weeks, full V0 ≈ 8–10 weeks.

## 6. Claude Code tooling (minimal at first, extended when needed)

- Short **CLAUDE.md**: non-obvious commands, principles 1–3 above with their reason.
- **Hooks**: formatting (ruff / Biome) after each edit; secrets (`.env*`) unreadable and `data/` read-only; `Stop` hook that refuses to finish while `make check-fast` fails; guard on version-control commands (no hook bypass, no co-author).
- **`code-reviewer` subagent** (read-only): reviews the diff in a fresh context, reports correctness issues only.
- **Skills**: `prepare-commit` (Conventional Commit message, the maintainer commits); `db-migration` (model + tested Alembic migration).
- **Later, if the need recurs**: `energy-data-dictionary` skill (units, Enedis pitfalls, ADEME sources); `statistician` subagent for lot 7.
- **Chrome MCP** to check the UI in a real browser.

## 7. Open decisions (maintainer)

- [x] Plan approved; name **Ecokaz**; **public** repo; web first, mobile in V2.
- [x] Reuse the Kwak Finance foundation (tooling; auth to reuse in lot 3).
- [ ] Hetzner or Scaleway; domain name?
- [ ] Check whether the GRDF customer area offers a file export (otherwise gas stays on manual readings).
- [ ] Water supplier (some expose an online history).
- [ ] Mistral API key (lot 8 only).

## 8. Corrections to the plan

_(deviation log, filled in as we go)_

- **2026-10-09, lot 0.** Foundation taken from Kwak Finance (commit 7d67666) instead of written from scratch, to keep the same conventions: sole committer, hooks, `make check-fast` Stop hook, testcontainers. Consequences: PostgreSQL **17** instead of 16; Biome instead of Prettier; scheduler and i18n postponed to the lot that needs them.
- **2026-10-09, lot 0, review.** The inherited foundation had defects, fixed: Alembic saw no model (added `ecokaz_api/models`); the `api` container never applied migrations (it now runs `python -m ecokaz_api.migrate`); the `web` container received the database credentials; the HSTS header was sent on localhost (now `ECOKAZ_HSTS_MAX_AGE`, 0 locally). Dedicated ports 8090/8453 and 8001/5174, to run beside Kwak Finance.
- **2026-10-09, charter.** In dark mode the background is `neutral-800`, as on the blog (Kwak Finance used `neutral-900`).
- **2026-10-09, docs.** Code and docs in English (this plan and the README were first written in French); the UI stays in French.

---
name: db-migration
description: Add or change database tables with SQLAlchemy models and an Alembic migration, tested on a real Postgres. Use when a change adds, alters or removes a table, column, index or constraint.
---

Models live in `backend/packages/api/src/ecokaz_api/` and inherit `Base` from `ecokaz_api.db`. Migrations live in `ecokaz_api/migrations/versions/` and ship inside the package.

1. **Test first.** Write the test for the behaviour the schema change enables (constraint, default, relationship) using the `session` fixture from `tests/api/db/conftest.py`. Run it and check it fails for the right reason.
2. **Model.** Edit or add the model:
   - Use the `UUIDPrimaryKey` and `Timestamps` mixins from `ecokaz_api.db` (UUIDv7, `timestamptz` in UTC).
   - Money is `Numeric(14, 2)` mapped to `Decimal`. Physical quantities (kWh, m³, km, kgCO₂e) are `Numeric(18, 6)`, with the unit in the column name or a unit column. Measurement intervals are `timestamptz` (UTC), half-open `[start, end)`. Never `Float`.
   - Name nothing by hand: the metadata naming convention names constraints and indexes.
   - Re-export the model from `ecokaz_api/models/__init__.py`: `env.py` imports that package, and autogenerate only sees models it imported.
3. **Generate** against a throwaway database (the compose `db` service is not exposed to the host):
   ```bash
   docker run --rm -d --name ecokaz-migrate -e POSTGRES_USER=ecokaz -e POSTGRES_PASSWORD=ecokaz -p 55432:5432 postgres:17-alpine
   export ECOKAZ_DATABASE_URL=postgresql+psycopg://ecokaz:ecokaz@localhost:55432/ecokaz
   make migrate && make migration m="<imperative summary>"
   docker stop ecokaz-migrate
   ```
4. **Review the generated file line by line.** Autogenerate misses or gets wrong:
   - renames (it emits drop + add, which loses data: rewrite with `op.alter_column` / `op.rename_table`);
   - server defaults, `CHECK` constraints, enum type creation and removal;
   - data migrations (write them by hand, with plain SQL, not with the ORM models, which change over time).
   Make sure `downgrade()` really reverses `upgrade()`.
5. **Test.** `cd backend && uv run pytest tests/api/db`. `test_migrations.py` runs upgrade → downgrade → upgrade and fails if the models and migrations differ. Then `make check-fast`.
6. **One migration per PR topic**, committed with the model change (`feat(api): ...`).

Rules:
- Never edit a migration that is merged into `main`: write a new one.
- Never run migrations against the real database from Claude. Never touch `data/`.
- If `alembic heads` shows several heads after a rebase, re-point the new revision's `down_revision` to the current head instead of adding a merge revision.

import ecokaz_api.models  # noqa: F401  (registers tables on Base.metadata)
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from ecokaz_api.db import Base, make_engine
from ecokaz_api.migrate import alembic_config, upgrade_head
from sqlalchemy import Engine


def test_migrations_upgrade_downgrade_upgrade(database_url: str) -> None:
    config = alembic_config(database_url)
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    command.upgrade(config, "head")


def test_models_match_migrations(database_url: str, engine: Engine) -> None:
    command.upgrade(alembic_config(database_url), "head")
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == []


def test_upgrade_head_is_idempotent(database_url: str) -> None:
    # The api container runs this on every start, so a second run must be a no-op.
    upgrade_head(database_url)
    upgrade_head(database_url)
    config = alembic_config(database_url)
    with make_engine(database_url).connect() as conn:
        current = MigrationContext.configure(conn).get_current_heads()
    assert set(current) == set(ScriptDirectory.from_config(config).get_heads())

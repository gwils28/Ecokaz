"""Programmatic Alembic configuration (tests, container entrypoint).

`python -m ecokaz_api.migrate` upgrades the configured database to head; the api container
runs it before starting uvicorn.
"""

from alembic import command
from alembic.config import Config

from ecokaz_api.settings import Settings

SCRIPT_LOCATION = "ecokaz_api:migrations"


def alembic_config(database_url: str) -> Config:
    config = Config()
    config.set_main_option("script_location", SCRIPT_LOCATION)
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


def upgrade_head(database_url: str) -> None:
    command.upgrade(alembic_config(database_url), "head")


if __name__ == "__main__":
    upgrade_head(Settings().database_url)

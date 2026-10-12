"""The default database URL names its driver explicitly.

shqaff declares psycopg2-binary as its PostgreSQL driver. A bare
``postgresql://`` URL leaves the choice to SQLAlchemy, whose default changed to
psycopg (v3) in 2.1. A fresh install then failed with
``ModuleNotFoundError: No module named 'psycopg'`` at import time.
"""

from sqlalchemy.engine import make_url

from shqaff import config


def test_default_url_uses_the_declared_psycopg2_driver():
    # The URL itself must name the driver: with a bare "postgresql://" the
    # resolved driver depends on the installed SQLAlchemy version.
    assert make_url(config.DATABASE_URL).drivername == "postgresql+psycopg2"


def test_engine_loads_the_psycopg2_dialect():
    from shqaff.db import engine

    assert engine.dialect.driver == "psycopg2"

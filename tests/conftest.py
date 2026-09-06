import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shqaff.db import init_db, SessionLocal
from shqaff.models import Base, TaskQueue
from shqaff.registry import consumer_registry
from shqaff.repository import TaskRepository


@pytest.fixture(autouse=True)
def clear_consumer_registry():
    consumer_registry.clear()
    yield
    consumer_registry.clear()


@pytest.fixture
def faker_seed():
    """Deterministic Faker output across the suite."""
    return 20260906


@pytest.fixture
def sqlite_engine():
    """A self-contained in-memory SQLite engine, no PostgreSQL required."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sqlite_session(sqlite_engine):
    session = sessionmaker(bind=sqlite_engine)()
    yield session
    session.close()


@pytest.fixture
def repo(sqlite_session):
    return TaskRepository(sqlite_session)


@pytest.fixture(scope="function")
def db():
    init_db()
    session = SessionLocal()

    # Clean the table before each test
    session.query(TaskQueue).delete()
    session.commit()

    yield session

    session.close()

import pytest
from shqaff.db import init_db, SessionLocal
from shqaff.models import TaskQueue
from shqaff.registry import consumer_registry


@pytest.fixture(autouse=True)
def clear_consumer_registry():
    consumer_registry.clear()
    yield
    consumer_registry.clear()


@pytest.fixture(scope="function")
def db():
    init_db()
    session = SessionLocal()

    # Clean the table before each test
    session.query(TaskQueue).delete()
    session.commit()

    yield session

    session.close()

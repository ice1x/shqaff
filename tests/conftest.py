import pytest
from shqaff.db import init_db, SessionLocal
from shqaff.models import TaskQueue


@pytest.fixture(scope="function")
def db():
    init_db()
    session = SessionLocal()

    # Clean the table before each test
    session.query(TaskQueue).delete()
    session.commit()

    yield session

    session.close()

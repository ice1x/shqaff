import pytest
from sqlalchemy.orm import Session

from shqaff.db import init_db, SessionLocal
from shqaff.models import TaskQueue
from shqaff.producer import create_task


@pytest.fixture(scope="module")
def db() -> Session:
    init_db()
    db = SessionLocal()
    yield db
    db.close()


def test_create_task(db):
    create_task(
        db=db,
        task_name="test_task",
        consumer="test_consumer",
        payload={"foo": "bar"},
        max_retries=2,
    )

    task = (
        db.query(TaskQueue)
        .filter_by(task_name="test_task", consumer="test_consumer")
        .first()
    )

    assert task is not None
    assert task.payload["foo"] == "bar"
    assert task.status == "pending"
    assert task.max_retries == 2

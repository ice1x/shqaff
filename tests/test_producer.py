"""Unit tests for the producer, which delegates to the repository layer."""

from shqaff.producer import create_task
from shqaff.status import TaskStatus


def test_create_task_persists_and_returns_pending_task(sqlite_session, faker):
    payload = {"to": faker.email()}

    task = create_task(
        db=sqlite_session,
        task_name="welcome",
        consumer="send_email",
        payload=payload,
        max_retries=2,
    )

    assert task.id is not None
    assert task.task_name == "welcome"
    assert task.consumer == "send_email"
    assert task.payload == payload
    assert task.max_retries == 2
    assert task.retries == 0
    assert task.status == TaskStatus.PENDING.value

"""End-to-end tests: enqueue via the repository, drain with the event loop."""

from shqaff.consumer import Consumer
from shqaff.event_loop import process_once
from shqaff.registry import register_consumer
from shqaff.repository import TaskRepository
from shqaff.status import TaskStatus


class RecordingConsumer(Consumer):
    name = "record"

    def __init__(self):
        RecordingConsumer.seen = getattr(RecordingConsumer, "seen", [])

    def run(self, payload: dict) -> None:
        RecordingConsumer.seen.append(payload)


class BoomConsumer(Consumer):
    name = "boom"

    def run(self, payload: dict) -> None:
        raise RuntimeError("boom")


def test_e2e_task_succeeds(repo: TaskRepository, faker):
    RecordingConsumer.seen = []
    register_consumer(RecordingConsumer)
    payload = {"user": faker.name(), "id": faker.random_int()}

    task = repo.create(task_name="job", consumer="record", payload=payload)
    process_once(repo.db, batch_size=10)

    processed = repo.get(task.id)
    assert processed.status == TaskStatus.DONE.value
    assert processed.error is None
    assert RecordingConsumer.seen[-1] == payload


def test_e2e_task_fails_after_retries(repo: TaskRepository):
    register_consumer(BoomConsumer)
    task = repo.create(
        task_name="job", consumer="boom", payload={}, max_retries=1
    )

    process_once(repo.db, batch_size=10)

    failed = repo.get(task.id)
    assert failed.status == TaskStatus.FAILED.value
    assert failed.retries == 1
    assert "boom" in failed.error


def test_e2e_task_retries_then_stays_pending(repo: TaskRepository):
    register_consumer(BoomConsumer)
    task = repo.create(
        task_name="job", consumer="boom", payload={}, max_retries=3
    )

    process_once(repo.db, batch_size=10)

    retried = repo.get(task.id)
    assert retried.status == TaskStatus.PENDING.value
    assert retried.retries == 1

from shqaff.models import TaskQueue
from shqaff.registry import register_consumer
from shqaff.event_loop import process_once
from shqaff.consumer import Consumer
from shqaff.producer import create_task


class DummyConsumer(Consumer):
    name = "dummy"
    processed = []

    def run(self, payload: dict) -> None:
        self.__class__.processed.append(payload)


def test_event_loop_processes_task(db):
    register_consumer(DummyConsumer)

    create_task(
        db=db,
        task_name="some_task",
        consumer="dummy",
        payload={"hello": "world"},
        max_retries=1,
    )

    process_once(db=db, batch_size=1)

    task = db.query(TaskQueue).filter_by(consumer="dummy").first()
    assert task.status == "done"
    assert task.error is None
    assert task.retries == 0
    assert DummyConsumer.processed[-1] == {"hello": "world"}

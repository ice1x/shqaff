from shqaff.consumer import Consumer
from shqaff.registry import register_consumer
from shqaff.producer import create_task
from shqaff.event_loop import process_once
from shqaff.models import TaskQueue


class AlwaysFailingConsumer(Consumer):
    name = "always_fail"

    def run(self, payload: dict) -> None:
        raise RuntimeError("crash")


def test_task_fails_permanently_after_max_retries(db):
    register_consumer(AlwaysFailingConsumer)

    create_task(
        db=db,
        task_name="fail_task",
        consumer="always_fail",
        payload={},
        max_retries=1,
    )

    process_once(db)

    task = db.query(TaskQueue).first()
    assert task.status == "failed"
    assert task.retries == 1
    assert "crash" in task.error

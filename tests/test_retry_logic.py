from shqaff.consumer import Consumer
from shqaff.registry import register_consumer
from shqaff.producer import create_task
from shqaff.event_loop import process_once
from shqaff.models import TaskQueue


class FailingOnceConsumer(Consumer):
    name = "fail_once"
    call_count = 0

    def run(self, payload: dict) -> None:
        self.__class__.call_count += 1
        if self.__class__.call_count == 1:
            raise Exception("fail once")


def test_retry_logic(db):
    FailingOnceConsumer.call_count = 0
    register_consumer(FailingOnceConsumer)

    create_task(
        db=db,
        task_name="retry_task",
        consumer="fail_once",
        payload={},
        max_retries=2,
    )

    process_once(db=db, batch_size=1)

    task = db.query(TaskQueue).filter_by(consumer="fail_once").first()
    assert task.status == "pending"
    assert task.retries == 1
    assert "fail once" in task.error

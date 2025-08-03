from dataclasses import asdict, dataclass

from shqaff.db import init_db, SessionLocal
from shqaff.event_loop import process_tasks
from shqaff.registry import register_consumer
from shqaff.consumer import Consumer
from shqaff.producer import create_task


@dataclass
class DemoPayload:
    message: str
    number: int


class DemoConsumer(Consumer):

    @property
    def name(self) -> str:
        return "demo_task"

    def run(self, payload: dict) -> None:
        data = DemoPayload(**payload)
        print("DemoConsumer received:", data)


if __name__ == "__main__":
    init_db()
    register_consumer(DemoConsumer)
    db = SessionLocal()
    create_task(
        db,
        task_name="demo",
        consumer="demo_task",
        payload=asdict(DemoPayload("hello", 1)),
    )
    process_tasks(db=db, poll_interval=2)

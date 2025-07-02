from shqaff.db import init_db, SessionLocal
from shqaff.event_loop import process_tasks
from shqaff.registry import register_consumer
from shqaff.consumer import Consumer


class DemoConsumer(Consumer):

    @property
    def name(self) -> str:
        return "demo_task"

    def run(self, payload: dict) -> None:
        print("DemoConsumer received:", payload)


if __name__ == "__main__":
    init_db()
    register_consumer(DemoConsumer)
    process_tasks(db=SessionLocal(), poll_interval=2)

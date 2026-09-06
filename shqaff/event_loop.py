import time
from datetime import datetime, timezone

from shqaff.registry import consumer_registry
from shqaff.repository import TaskRepository
from shqaff.task import Task
from shqaff.status import TaskStatus


def process_once(db, batch_size: int = 10):
    repo = TaskRepository(db)
    tasks = repo.claim_pending(batch_size)

    for task_model in tasks:
        consumer_cls = consumer_registry.get(task_model.consumer)
        if not consumer_cls:
            continue

        task = Task(task_model)

        try:
            task.start()
            task_model.last_attempt_at = datetime.now(timezone.utc)
            repo.commit()

            consumer = consumer_cls()
            consumer.run(task_model.payload)

            task.succeed()

        except Exception as e:
            task_model.retries += 1
            task_model.error = str(e)

            if task_model.retries >= task_model.max_retries:
                task.fail()
            else:
                task_model.status = TaskStatus.PENDING.value

        finally:
            task_model.updated_at = datetime.now(timezone.utc)
            repo.commit()


def process_tasks(db, poll_interval: int = 5, batch_size: int = 10):
    while True:
        process_once(db, batch_size=batch_size)
        time.sleep(poll_interval)

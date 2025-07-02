import time
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from .models import TaskQueue
from .registry import consumer_registry


def process_tasks(db: Session, poll_interval: int = 5, batch_size: int = 10) -> None:
    while True:
        stmt = (
            select(TaskQueue)
            .where(TaskQueue.status == "pending")
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        tasks = db.execute(stmt).scalars().all()

        for task in tasks:
            consumer_cls = consumer_registry.get(task.consumer)

            if not consumer_cls:
                continue

            consumer = consumer_cls()

            try:
                task.status = "in_progress"
                task.last_attempt_at = datetime.utcnow()
                db.commit()

                consumer.run(task.payload)

                task.status = "done"

            except Exception as e:
                task.retries += 1
                task.error = str(e)

                if task.retries >= task.max_retries:
                    task.status = "failed"
                else:
                    task.status = "pending"

            finally:
                task.updated_at = datetime.utcnow()
                db.commit()

        time.sleep(poll_interval)

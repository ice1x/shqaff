from sqlalchemy.orm import Session
from .models import TaskQueue


def create_task(
    db: Session, task_name: str, consumer: str, payload: dict, max_retries: int = 3
) -> None:
    task = TaskQueue(
        task_name=task_name,
        consumer=consumer,
        payload=payload,
        max_retries=max_retries,
        status="pending",
    )
    db.add(task)
    db.commit()

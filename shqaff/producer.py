from sqlalchemy.orm import Session

from shqaff.models import TaskQueue
from shqaff.repository import TaskRepository


def create_task(
    db: Session, task_name: str, consumer: str, payload: dict, max_retries: int = 3
) -> TaskQueue:
    return TaskRepository(db).create(
        task_name=task_name,
        consumer=consumer,
        payload=payload,
        max_retries=max_retries,
    )

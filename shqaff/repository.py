"""Repository layer: a thin, testable data-access API over :class:`TaskQueue`."""

from __future__ import annotations

from typing import Any, List, Optional, Union

from sqlalchemy.orm import Session

from shqaff.models import TaskQueue
from shqaff.status import TaskStatus

StatusLike = Union[TaskStatus, str]

# Columns a caller is allowed to mutate through :meth:`TaskRepository.update`.
_UPDATABLE_FIELDS = frozenset(
    {
        "task_name",
        "consumer",
        "payload",
        "max_retries",
        "retries",
        "status",
        "error",
    }
)


def _status_value(status: StatusLike) -> str:
    return status.value if isinstance(status, TaskStatus) else str(status)


class TaskRepository:
    """CRUD access to the task queue, decoupled from any particular engine.

    The repository holds no connection of its own; it operates on the
    :class:`~sqlalchemy.orm.Session` handed to it, so it works identically
    against PostgreSQL in production and SQLite in tests.
    """

    def __init__(self, db: Session):
        self.db = db

    # -- create ---------------------------------------------------------
    def create(
        self,
        *,
        task_name: str,
        consumer: str,
        payload: Optional[dict] = None,
        max_retries: int = 3,
        status: StatusLike = TaskStatus.PENDING,
    ) -> TaskQueue:
        task = TaskQueue(
            task_name=task_name,
            consumer=consumer,
            payload=payload,
            max_retries=max_retries,
            retries=0,
            status=_status_value(status),
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    # -- read -----------------------------------------------------------
    def get(self, task_id: int) -> Optional[TaskQueue]:
        return self.db.get(TaskQueue, task_id)

    def list(
        self,
        *,
        status: Optional[StatusLike] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[TaskQueue]:
        query = self.db.query(TaskQueue)
        if status is not None:
            query = query.filter(TaskQueue.status == _status_value(status))
        query = query.order_by(TaskQueue.id)
        if offset:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def count(self, *, status: Optional[StatusLike] = None) -> int:
        query = self.db.query(TaskQueue)
        if status is not None:
            query = query.filter(TaskQueue.status == _status_value(status))
        return query.count()

    def claim_pending(
        self, batch_size: int = 10, *, for_update: bool = True
    ) -> List[TaskQueue]:
        """Fetch a batch of pending tasks for processing.

        When ``for_update`` is set (the default) the rows are locked with
        ``SELECT ... FOR UPDATE SKIP LOCKED`` so concurrent workers never claim
        the same task. The clause is a no-op on backends that do not support it
        (e.g. SQLite in tests). No transaction is committed here; the caller
        owns the unit of work and persists via :meth:`commit`.
        """
        query = (
            self.db.query(TaskQueue)
            .filter(TaskQueue.status == TaskStatus.PENDING.value)
            .limit(batch_size)
        )
        if for_update:
            query = query.with_for_update(skip_locked=True)
        return query.all()

    def commit(self) -> None:
        """Persist pending changes on the underlying session."""
        self.db.commit()

    # -- update ---------------------------------------------------------
    def update(self, task_id: int, **fields: Any) -> Optional[TaskQueue]:
        unknown = set(fields) - _UPDATABLE_FIELDS
        if unknown:
            raise ValueError(f"Unknown or protected field(s): {sorted(unknown)}")

        task = self.get(task_id)
        if task is None:
            return None

        if "status" in fields:
            fields["status"] = _status_value(fields["status"])

        for key, value in fields.items():
            setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def set_status(self, task_id: int, status: StatusLike) -> Optional[TaskQueue]:
        return self.update(task_id, status=status)

    # -- delete ---------------------------------------------------------
    def delete(self, task_id: int) -> bool:
        task = self.get(task_id)
        if task is None:
            return False
        self.db.delete(task)
        self.db.commit()
        return True

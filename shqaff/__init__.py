"""shqaff — a lightweight, PostgreSQL-backed task queue for Python."""

from shqaff.consumer import Consumer
from shqaff.db import Base, SessionLocal, get_db, init_db
from shqaff.event_loop import process_once, process_tasks
from shqaff.fsm import TaskStateMachine
from shqaff.models import TaskQueue
from shqaff.producer import create_task
from shqaff.registry import consumer_registry, register_consumer
from shqaff.repository import TaskRepository
from shqaff.status import TaskStatus
from shqaff.task import Task

__version__ = "0.0.2"

__all__ = [
    "__version__",
    "Base",
    "Consumer",
    "SessionLocal",
    "Task",
    "TaskQueue",
    "TaskRepository",
    "TaskStateMachine",
    "TaskStatus",
    "consumer_registry",
    "create_task",
    "get_db",
    "init_db",
    "process_once",
    "process_tasks",
    "register_consumer",
]

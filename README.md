# 🗄️ shqaff

A lightweight, PostgreSQL-backed task queue for Python. Uses SQLAlchemy for storage and a finite state machine for reliable task lifecycle management.

## Features

- PostgreSQL-backed persistence with row-level locking (`SELECT ... FOR UPDATE SKIP LOCKED`)
- Finite state machine for task transitions: `pending -> in_progress -> done | failed`
- Configurable retry logic with max retry limits
- Simple consumer registration pattern
- Minimal dependencies: SQLAlchemy, psycopg2, transitions

## Installation

```bash
pip install shqaff
```

For development:

```bash
pip install shqaff[dev]
```

## Quick Start

### 1. Start PostgreSQL

Using Docker:

```bash
docker run -d --name shqaff-db \
  -e POSTGRES_DB=shqaff \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15
```

### 2. Define a Consumer

A consumer is a class that processes tasks. Subclass `Consumer` and implement the `name` property and `run()` method:

```python
from shqaff.consumer import Consumer
from shqaff.registry import register_consumer

class EmailConsumer(Consumer):

    @property
    def name(self) -> str:
        return "send_email"

    def run(self, payload: dict) -> None:
        to = payload["to"]
        subject = payload["subject"]
        body = payload["body"]
        print(f"Sending email to {to}: {subject}")
        # ... actual email sending logic here

register_consumer(EmailConsumer)
```

### 3. Create Tasks

```python
from shqaff.db import init_db, SessionLocal
from shqaff.producer import create_task

# Initialize the database tables
init_db()

db = SessionLocal()

# Enqueue a task
create_task(
    db=db,
    task_name="welcome_email",
    consumer="send_email",
    payload={
        "to": "user@example.com",
        "subject": "Welcome!",
        "body": "Thanks for signing up.",
    },
    max_retries=3,
)
```

### 4. Process Tasks

```python
from shqaff.event_loop import process_tasks

# Poll the database and process pending tasks
# This runs an infinite loop with a configurable interval
process_tasks(db=db, poll_interval=2, batch_size=10)
```

### Single-batch Processing

For cron-style execution, process one batch and exit:

```python
from shqaff.event_loop import process_once

process_once(db=db, batch_size=10)
```

## Full Working Example

```python
from dataclasses import asdict, dataclass

from shqaff.consumer import Consumer
from shqaff.db import init_db, SessionLocal
from shqaff.event_loop import process_tasks
from shqaff.producer import create_task
from shqaff.registry import register_consumer


@dataclass
class OrderPayload:
    order_id: int
    items: list[str]


class OrderConsumer(Consumer):

    @property
    def name(self) -> str:
        return "process_order"

    def run(self, payload: dict) -> None:
        order = OrderPayload(**payload)
        print(f"Processing order #{order.order_id}: {order.items}")


if __name__ == "__main__":
    init_db()
    register_consumer(OrderConsumer)

    db = SessionLocal()
    create_task(
        db=db,
        task_name="new_order",
        consumer="process_order",
        payload=asdict(OrderPayload(order_id=42, items=["widget", "gadget"])),
    )

    # Process tasks every 2 seconds
    process_tasks(db=db, poll_interval=2)
```

## Repository Layer

`TaskRepository` is a thin, engine-agnostic CRUD layer over the task model. It
holds no connection of its own — it operates on the `Session` you pass in, so it
works identically against PostgreSQL in production and SQLite in tests:

```python
from shqaff import SessionLocal, TaskRepository, TaskStatus

repo = TaskRepository(SessionLocal())

task = repo.create(task_name="welcome_email", consumer="send_email", payload={"to": "a@b.c"})
repo.get(task.id)
repo.list(status=TaskStatus.PENDING, limit=20)
repo.count(status=TaskStatus.PENDING)
repo.set_status(task.id, TaskStatus.DONE)
repo.delete(task.id)
```

## Command-Line Interface

Installing the package exposes a `shqaff` command with full CRUD over the queue:

```bash
shqaff init-db
shqaff create --task-name welcome_email --consumer send_email --payload '{"to": "a@b.c"}'
shqaff list --status pending
shqaff get 1
shqaff update 1 --status done
shqaff delete 1
```

The database URL is resolved from the `--database-url` option, the
`SHQAFF_DATABASE_URL` environment variable, or the `SHAQAFF_DB_*` configuration
variables, in that order.

## Task Lifecycle

Tasks follow a strict state machine:

```
pending ──start()──> in_progress ──succeed()──> done
                          │
                          └──fail()──> failed
```

- **pending**: Task is queued, waiting to be picked up
- **in_progress**: A consumer is currently executing the task
- **done**: Task completed successfully
- **failed**: Task exceeded max retries and is permanently failed

When a task raises an exception during processing, it is retried (reset to `pending`) until `max_retries` is reached, at which point it transitions to `failed`.

## Configuration

Database connection is configured via environment variables:

| Variable | Default | Description |
|---|---|---|
| `SHAQAFF_DB_HOST` | `localhost` | PostgreSQL host |
| `SHAQAFF_DB_PORT` | `5432` | PostgreSQL port |
| `SHAQAFF_DB_NAME` | `shqaff` | Database name |
| `SHAQAFF_DB_USER` | `postgres` | Database user |
| `SHAQAFF_DB_PASS` | *(empty)* | Database password |

## Docker

Run the full stack with Docker Compose:

```bash
docker compose up -d db       # Start PostgreSQL
docker compose up shqaff      # Run the demo app
docker compose run test       # Run the test suite
```

## Testing

The suite spans unit, integration, fuzz (Hypothesis) and end-to-end layers.
The repository, CLI and lifecycle tests run against in-memory SQLite and need no
PostgreSQL; the legacy DB-backed tests (`test_smoke`, `test_event_loop`,
`test_retry_logic`, `test_fail_after_max_retries`) require a running instance.

```bash
pip install -e ".[dev]"

# Runs everywhere, no database required:
pytest tests/test_repository.py tests/test_repository_fuzz.py \
       tests/test_cli.py tests/test_e2e.py tests/test_package.py \
       tests/test_task_fsm.py tests/test_invalid_fsm_transition.py

# Full suite (needs a running PostgreSQL instance):
pytest tests/
```

## License

MIT

"""Command-line interface exposing CRUD operations over the task queue."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Optional, Sequence

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shqaff import __version__
from shqaff.config import DATABASE_URL
from shqaff.models import Base, TaskQueue
from shqaff.repository import TaskRepository
from shqaff.status import TaskStatus


def _resolve_database_url(cli_value: Optional[str]) -> str:
    return cli_value or os.getenv("SHQAFF_DATABASE_URL") or DATABASE_URL


def _make_session(database_url: str) -> Session:
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _task_to_dict(task: TaskQueue) -> dict:
    return {
        "id": task.id,
        "task_name": task.task_name,
        "consumer": task.consumer,
        "payload": task.payload,
        "status": task.status,
        "retries": task.retries,
        "max_retries": task.max_retries,
        "error": task.error,
    }


def _parse_payload(raw: Optional[str]) -> Optional[dict]:
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--payload is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("--payload must be a JSON object")
    return value


def _emit(data: Any, out) -> None:
    json.dump(data, out, indent=2, default=str)
    out.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shqaff", description="Manage the shqaff task queue."
    )
    parser.add_argument("--version", action="version", version=f"shqaff {__version__}")
    parser.add_argument(
        "--database-url",
        default=None,
        help="SQLAlchemy database URL (defaults to $SHQAFF_DATABASE_URL or config).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Create the task_queue table.")

    p_create = sub.add_parser("create", help="Enqueue a new task.")
    p_create.add_argument("--task-name", required=True)
    p_create.add_argument("--consumer", required=True)
    p_create.add_argument("--payload", default=None, help="JSON object payload.")
    p_create.add_argument("--max-retries", type=int, default=3)

    p_get = sub.add_parser("get", help="Show a single task by id.")
    p_get.add_argument("id", type=int)

    p_list = sub.add_parser("list", help="List tasks.")
    p_list.add_argument(
        "--status", choices=[s.value for s in TaskStatus], default=None
    )
    p_list.add_argument("--limit", type=int, default=None)
    p_list.add_argument("--offset", type=int, default=0)

    p_update = sub.add_parser("update", help="Update fields of a task.")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--task-name", default=None)
    p_update.add_argument("--consumer", default=None)
    p_update.add_argument("--payload", default=None, help="JSON object payload.")
    p_update.add_argument("--max-retries", type=int, default=None)
    p_update.add_argument(
        "--status", choices=[s.value for s in TaskStatus], default=None
    )

    p_delete = sub.add_parser("delete", help="Delete a task by id.")
    p_delete.add_argument("id", type=int)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    out = sys.stdout
    err = sys.stderr

    database_url = _resolve_database_url(args.database_url)

    if args.command == "init-db":
        engine = create_engine(database_url)
        Base.metadata.create_all(bind=engine)
        out.write("Database initialized.\n")
        return 0

    session = _make_session(database_url)
    repo = TaskRepository(session)
    try:
        if args.command == "create":
            payload = _parse_payload(args.payload)
            task = repo.create(
                task_name=args.task_name,
                consumer=args.consumer,
                payload=payload,
                max_retries=args.max_retries,
            )
            _emit(_task_to_dict(task), out)
            return 0

        if args.command == "get":
            task = repo.get(args.id)
            if task is None:
                err.write(f"Task {args.id} not found.\n")
                return 1
            _emit(_task_to_dict(task), out)
            return 0

        if args.command == "list":
            tasks = repo.list(
                status=args.status, limit=args.limit, offset=args.offset
            )
            _emit([_task_to_dict(t) for t in tasks], out)
            return 0

        if args.command == "update":
            fields = {}
            if args.task_name is not None:
                fields["task_name"] = args.task_name
            if args.consumer is not None:
                fields["consumer"] = args.consumer
            if args.payload is not None:
                fields["payload"] = _parse_payload(args.payload)
            if args.max_retries is not None:
                fields["max_retries"] = args.max_retries
            if args.status is not None:
                fields["status"] = args.status
            if not fields:
                err.write("Nothing to update: provide at least one field.\n")
                return 2
            task = repo.update(args.id, **fields)
            if task is None:
                err.write(f"Task {args.id} not found.\n")
                return 1
            _emit(_task_to_dict(task), out)
            return 0

        if args.command == "delete":
            if repo.delete(args.id):
                out.write(f"Deleted task {args.id}.\n")
                return 0
            err.write(f"Task {args.id} not found.\n")
            return 1
    except ValueError as exc:
        err.write(f"Error: {exc}\n")
        return 2
    finally:
        session.close()

    return 0  # pragma: no cover - argparse guarantees a known command


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

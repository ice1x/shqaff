"""Integration tests driving the CLI end-to-end against a temp SQLite file."""

import json

import pytest

from shqaff.cli import main
from shqaff.status import TaskStatus


@pytest.fixture
def db_url(tmp_path):
    return f"sqlite:///{tmp_path/'cli.sqlite'}"


def run(db_url, *args, capsys):
    code = main(["--database-url", db_url, *args])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_full_crud_flow(db_url, capsys):
    # init
    code, out, _ = run(db_url, "init-db", capsys=capsys)
    assert code == 0 and "initialized" in out.lower()

    # create
    code, out, _ = run(
        db_url,
        "create",
        "--task-name", "welcome",
        "--consumer", "greet",
        "--payload", '{"who": "world"}',
        "--max-retries", "2",
        capsys=capsys,
    )
    assert code == 0
    created = json.loads(out)
    task_id = created["id"]
    assert created["status"] == TaskStatus.PENDING.value
    assert created["payload"] == {"who": "world"}
    assert created["max_retries"] == 2

    # get
    code, out, _ = run(db_url, "get", str(task_id), capsys=capsys)
    assert code == 0
    assert json.loads(out)["id"] == task_id

    # list
    code, out, _ = run(db_url, "list", capsys=capsys)
    assert code == 0
    assert [t["id"] for t in json.loads(out)] == [task_id]

    # update
    code, out, _ = run(
        db_url, "update", str(task_id), "--status", "done", capsys=capsys
    )
    assert code == 0
    assert json.loads(out)["status"] == TaskStatus.DONE.value

    # list filtered
    code, out, _ = run(db_url, "list", "--status", "pending", capsys=capsys)
    assert code == 0 and json.loads(out) == []

    # delete
    code, out, _ = run(db_url, "delete", str(task_id), capsys=capsys)
    assert code == 0 and "deleted" in out.lower()

    # get after delete -> not found
    code, _, err = run(db_url, "get", str(task_id), capsys=capsys)
    assert code == 1 and "not found" in err.lower()


def test_get_missing_returns_1(db_url, capsys):
    run(db_url, "init-db", capsys=capsys)
    code, _, err = run(db_url, "get", "12345", capsys=capsys)
    assert code == 1
    assert "not found" in err.lower()


def test_invalid_payload_returns_2(db_url, capsys):
    code, _, err = run(
        db_url,
        "create",
        "--task-name", "t",
        "--consumer", "c",
        "--payload", "not-json",
        capsys=capsys,
    )
    assert code == 2
    assert "json" in err.lower()


def test_payload_must_be_object(db_url, capsys):
    code, _, err = run(
        db_url,
        "create",
        "--task-name", "t",
        "--consumer", "c",
        "--payload", "[1, 2, 3]",
        capsys=capsys,
    )
    assert code == 2
    assert "object" in err.lower()


def test_update_without_fields_returns_2(db_url, capsys):
    run(db_url, "init-db", capsys=capsys)
    code, out, _ = run(
        db_url, "create", "--task-name", "t", "--consumer", "c", capsys=capsys
    )
    task_id = json.loads(out)["id"]
    code, _, err = run(db_url, "update", str(task_id), capsys=capsys)
    assert code == 2
    assert "nothing to update" in err.lower()


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "shqaff" in out

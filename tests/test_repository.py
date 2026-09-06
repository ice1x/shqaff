"""Unit tests for the repository layer (SQLite-backed, faker data)."""

import pytest

from shqaff.repository import TaskRepository
from shqaff.status import TaskStatus


def _make(faker):
    return {
        "task_name": faker.slug(),
        "consumer": faker.word(),
        "payload": {"email": faker.email(), "n": faker.random_int()},
        "max_retries": faker.random_int(min=1, max=5),
    }


def test_create_sets_defaults(repo: TaskRepository, faker):
    data = _make(faker)
    task = repo.create(**data)

    assert task.id is not None
    assert task.task_name == data["task_name"]
    assert task.consumer == data["consumer"]
    assert task.payload == data["payload"]
    assert task.max_retries == data["max_retries"]
    assert task.retries == 0
    assert task.status == TaskStatus.PENDING.value


def test_get_returns_task_and_none(repo: TaskRepository, faker):
    task = repo.create(**_make(faker))

    assert repo.get(task.id).id == task.id
    assert repo.get(999_999) is None


def test_list_and_count_filter_by_status(repo: TaskRepository, faker):
    for _ in range(3):
        repo.create(**_make(faker))
    done = repo.create(**_make(faker))
    repo.set_status(done.id, TaskStatus.DONE)

    assert repo.count() == 4
    assert repo.count(status=TaskStatus.PENDING) == 3
    assert repo.count(status=TaskStatus.DONE) == 1

    pending = repo.list(status=TaskStatus.PENDING)
    assert {t.status for t in pending} == {TaskStatus.PENDING.value}
    assert len(pending) == 3


def test_list_pagination_is_ordered(repo: TaskRepository, faker):
    created = [repo.create(**_make(faker)) for _ in range(5)]
    ids = [t.id for t in created]

    page = repo.list(limit=2, offset=1)
    assert [t.id for t in page] == ids[1:3]


def test_update_mutates_whitelisted_fields(repo: TaskRepository, faker):
    task = repo.create(**_make(faker))
    new_payload = {"changed": faker.boolean()}

    updated = repo.update(
        task.id, payload=new_payload, status=TaskStatus.IN_PROGRESS, retries=2
    )

    assert updated.payload == new_payload
    assert updated.status == TaskStatus.IN_PROGRESS.value
    assert updated.retries == 2
    # persisted, not just in-memory
    assert repo.get(task.id).status == TaskStatus.IN_PROGRESS.value


def test_update_missing_returns_none(repo: TaskRepository):
    assert repo.update(424242, status=TaskStatus.DONE) is None


def test_update_rejects_unknown_field(repo: TaskRepository, faker):
    task = repo.create(**_make(faker))
    with pytest.raises(ValueError):
        repo.update(task.id, id=1)
    with pytest.raises(ValueError):
        repo.update(task.id, nonsense="x")


def test_set_status_accepts_enum_and_str(repo: TaskRepository, faker):
    task = repo.create(**_make(faker))

    assert repo.set_status(task.id, "done").status == TaskStatus.DONE.value
    assert repo.set_status(task.id, TaskStatus.FAILED).status == TaskStatus.FAILED.value


def test_delete(repo: TaskRepository, faker):
    task = repo.create(**_make(faker))

    assert repo.delete(task.id) is True
    assert repo.get(task.id) is None
    assert repo.delete(task.id) is False


def test_claim_pending_returns_only_pending_up_to_batch(repo: TaskRepository, faker):
    pending = [repo.create(**_make(faker)) for _ in range(4)]
    done = repo.create(**_make(faker))
    repo.set_status(done.id, TaskStatus.DONE)

    claimed = repo.claim_pending(batch_size=3)

    assert len(claimed) == 3
    assert {t.id for t in claimed} <= {t.id for t in pending}
    assert all(t.status == TaskStatus.PENDING.value for t in claimed)


def test_commit_persists_pending_mutations(repo: TaskRepository, faker):
    task = repo.create(**_make(faker))

    task.error = "boom"
    repo.commit()

    assert repo.get(task.id).error == "boom"

from shqaff.models import TaskQueue
from shqaff.registry import register_consumer
from shqaff.event_loop import process_once
from shqaff.consumer import Consumer
from shqaff.producer import create_task
from shqaff.status import TaskStatus


class DummyConsumer(Consumer):
    name = "dummy"
    processed = []

    def run(self, payload: dict) -> None:
        self.__class__.processed.append(payload)


def test_event_loop_processes_task(db):
    register_consumer(DummyConsumer)

    create_task(
        db=db,
        task_name="some_task",
        consumer="dummy",
        payload={"hello": "world"},
        max_retries=1,
    )

    process_once(db=db, batch_size=1)

    task = db.query(TaskQueue).filter_by(consumer="dummy").first()
    assert task.status == TaskStatus.DONE.value
    assert task.error is None
    assert task.retries == 0
    assert DummyConsumer.processed[-1] == {"hello": "world"}


# --- FIFO: pending tasks are claimed oldest first ----------------------------
#
# A query without ORDER BY returns rows in heap order. In PostgreSQL an UPDATE
# writes a new row version after the existing ones, so a task that was touched
# (a retry puts it back to pending, a status change, ...) moves behind newer
# tasks. Seen in production (reviews, 2026-10-12): a queue's scoring and ML
# tasks ran before the data-ingest tasks enqueued ahead of them.


def _touch(db, task_id):
    """Rewrite a row in place, as a retry or a status change does."""
    db.query(TaskQueue).filter(TaskQueue.id == task_id).update({TaskQueue.error: "x"})
    db.query(TaskQueue).filter(TaskQueue.id == task_id).update({TaskQueue.error: None})
    db.commit()


def test_claim_pending_returns_the_oldest_tasks_first(db):
    from shqaff.repository import TaskRepository

    ids = [create_task(db=db, task_name=f"t{i}", consumer="dummy", payload={"i": i}).id for i in range(3)]
    _touch(db, ids[0])  # its new row version now sits after t1 and t2 in the heap

    claimed = TaskRepository(db).claim_pending(batch_size=3)
    assert [t.id for t in claimed] == ids


def test_a_small_batch_takes_the_oldest_pending_tasks(db):
    from shqaff.repository import TaskRepository

    ids = [create_task(db=db, task_name=f"t{i}", consumer="dummy", payload={"i": i}).id for i in range(4)]
    _touch(db, ids[0])
    _touch(db, ids[1])

    claimed = TaskRepository(db).claim_pending(batch_size=2)
    assert [t.id for t in claimed] == ids[:2]


def test_process_once_runs_tasks_in_creation_order(db):
    class Recorder(Consumer):
        name = "recorder"
        seen = []

        def run(self, payload: dict) -> None:
            self.__class__.seen.append(payload["i"])

    register_consumer(Recorder)
    ids = [create_task(db=db, task_name=f"t{i}", consumer="recorder", payload={"i": i}).id for i in range(5)]
    _touch(db, ids[0])
    _touch(db, ids[2])

    process_once(db=db, batch_size=5)
    assert Recorder.seen == [0, 1, 2, 3, 4]

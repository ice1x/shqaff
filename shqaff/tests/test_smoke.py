from shqaff.models import TaskQueue
from shqaff.producer import create_task
from shqaff.status import TaskStatus


def test_create_task(db):
    create_task(
        db=db,
        task_name="test_task",
        consumer="test_consumer",
        payload={"foo": "bar"},
        max_retries=2,
    )

    task = (
        db.query(TaskQueue)
        .filter_by(task_name="test_task", consumer="test_consumer")
        .first()
    )

    assert task is not None
    assert task.payload["foo"] == "bar"
    assert task.status == TaskStatus.PENDING.value
    assert task.max_retries == 2

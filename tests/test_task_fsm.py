from shqaff.models import TaskQueue
from shqaff.task import Task


def test_fsm_transitions():
    task_model = TaskQueue(status="pending")
    task = Task(task_model)

    assert task_model.status == "pending"

    task.start()
    assert task_model.status == "in_progress"

    task.succeed()
    assert task_model.status == "done"


def test_fsm_failure_transition():
    task_model = TaskQueue(status="pending")
    task = Task(task_model)

    task.start()
    assert task_model.status == "in_progress"

    task.fail()
    assert task_model.status == "failed"

from shqaff.models import TaskQueue
from shqaff.task import Task
from shqaff.status import TaskStatus


def test_fsm_transitions():
    task_model = TaskQueue(status=TaskStatus.PENDING.value)
    task = Task(task_model)

    assert task_model.status == TaskStatus.PENDING.value

    task.start()
    assert task_model.status == TaskStatus.IN_PROGRESS.value

    task.succeed()
    assert task_model.status == TaskStatus.DONE.value


def test_fsm_failure_transition():
    task_model = TaskQueue(status=TaskStatus.PENDING.value)
    task = Task(task_model)

    task.start()
    assert task_model.status == TaskStatus.IN_PROGRESS.value

    task.fail()
    assert task_model.status == TaskStatus.FAILED.value

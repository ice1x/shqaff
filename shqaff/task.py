from shqaff.models import TaskQueue
from shqaff.fsm import TaskStateMachine


class Task:

    def __init__(self, task: TaskQueue):
        self.task = task
        self.fsm = TaskStateMachine(initial=task.status)

    def start(self):
        self.fsm.start()
        self.task.status = self.fsm.get_state()

    def succeed(self):
        self.fsm.succeed()
        self.task.status = self.fsm.get_state()

    def fail(self):
        self.fsm.fail()
        self.task.status = self.fsm.get_state()

    @property
    def model(self) -> TaskQueue:
        return self.task

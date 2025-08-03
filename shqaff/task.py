from dataclasses import dataclass, field

from shqaff.models import TaskQueue
from shqaff.fsm import TaskStateMachine


@dataclass
class Task:
    task: TaskQueue
    fsm: TaskStateMachine = field(init=False)

    def __post_init__(self):
        self.fsm = TaskStateMachine(initial=self.task.status)

    def start(self):
        self.fsm.start()
        self.task.status = self.fsm.get_state().value

    def succeed(self):
        self.fsm.succeed()
        self.task.status = self.fsm.get_state().value

    def fail(self):
        self.fsm.fail()
        self.task.status = self.fsm.get_state().value

    @property
    def model(self) -> TaskQueue:
        return self.task

from transitions import Machine

from .status import TaskStatus


class TaskStateMachine:

    states = [status.value for status in TaskStatus]

    def __init__(self, initial: TaskStatus | str = TaskStatus.PENDING):
        self.state = initial.value if isinstance(initial, TaskStatus) else initial

        self.machine = Machine(
            model=self,
            states=TaskStateMachine.states,
            initial=self.state,
        )

        self.machine.add_transition("start", source=TaskStatus.PENDING.value, dest=TaskStatus.IN_PROGRESS.value)
        self.machine.add_transition("succeed", source=TaskStatus.IN_PROGRESS.value, dest=TaskStatus.DONE.value)
        self.machine.add_transition("fail", source=TaskStatus.IN_PROGRESS.value, dest=TaskStatus.FAILED.value)

    def get_state(self) -> TaskStatus:
        return TaskStatus(self.state)

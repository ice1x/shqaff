from transitions import Machine


class TaskStateMachine:

    states = ["pending", "in_progress", "done", "failed"]

    def __init__(self, initial: str = "pending"):
        self.state = initial

        self.machine = Machine(
            model=self,
            states=TaskStateMachine.states,
            initial=self.state,
        )

        self.machine.add_transition("start", source="pending", dest="in_progress")
        self.machine.add_transition("succeed", source="in_progress", dest="done")
        self.machine.add_transition("fail", source="in_progress", dest="failed")

    def get_state(self) -> str:
        return self.state

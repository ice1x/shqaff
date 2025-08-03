import pytest
from shqaff.fsm import TaskStateMachine
from transitions.core import MachineError


def test_invalid_fsm_transition_raises():
    fsm = TaskStateMachine(initial="done")

    with pytest.raises(MachineError):
        fsm.start()

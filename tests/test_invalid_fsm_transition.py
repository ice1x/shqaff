import pytest
from shqaff.fsm import TaskStateMachine
from transitions.core import MachineError
from shqaff.status import TaskStatus


def test_invalid_fsm_transition_raises():
    fsm = TaskStateMachine(initial=TaskStatus.DONE)

    with pytest.raises(MachineError):
        fsm.start()

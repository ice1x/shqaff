"""Unit tests for the package's public API surface."""

import shqaff


def test_version_is_exposed():
    assert isinstance(shqaff.__version__, str)
    assert shqaff.__version__.count(".") >= 2


def test_public_api_is_importable():
    for name in shqaff.__all__:
        assert hasattr(shqaff, name), f"missing public export: {name}"


def test_key_symbols_present():
    from shqaff import (  # noqa: F401
        Consumer,
        Task,
        TaskQueue,
        TaskRepository,
        TaskStatus,
        create_task,
        process_once,
        register_consumer,
    )

"""Property-based (fuzz) tests for the repository using Hypothesis.

Each example runs against a fresh in-memory database so Hypothesis's many
generated inputs stay isolated from one another.
"""

from contextlib import contextmanager

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shqaff.models import Base
from shqaff.repository import TaskRepository
from shqaff.status import TaskStatus


@contextmanager
def fresh_repo():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield TaskRepository(session)
    finally:
        session.close()
        engine.dispose()


# JSON-object payloads: string keys, JSON-serialisable scalar values.
json_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-(10**15), max_value=10**15),
    st.text(max_size=50),
)
json_payloads = st.dictionaries(keys=st.text(max_size=30), values=json_scalars, max_size=8)

identifiers = st.text(min_size=1, max_size=60).filter(lambda s: s.strip() != "")


@settings(max_examples=150, deadline=None)
@given(
    task_name=identifiers,
    consumer=identifiers,
    payload=json_payloads,
    max_retries=st.integers(min_value=0, max_value=100),
)
def test_create_get_roundtrip(task_name, consumer, payload, max_retries):
    with fresh_repo() as repo:
        created = repo.create(
            task_name=task_name,
            consumer=consumer,
            payload=payload,
            max_retries=max_retries,
        )
        fetched = repo.get(created.id)

        assert fetched is not None
        assert fetched.task_name == task_name
        assert fetched.consumer == consumer
        assert fetched.payload == payload
        assert fetched.max_retries == max_retries
        assert fetched.status == TaskStatus.PENDING.value
        assert fetched.retries == 0


@settings(max_examples=100, deadline=None)
@given(status=st.sampled_from(list(TaskStatus)), payload=json_payloads)
def test_update_status_and_payload_persist(status, payload):
    with fresh_repo() as repo:
        task = repo.create(task_name="t", consumer="c", payload={})
        updated = repo.update(task.id, status=status, payload=payload)

        assert updated.status == status.value
        assert updated.payload == payload
        assert repo.get(task.id).status == status.value


@settings(max_examples=50, deadline=None)
@given(n=st.integers(min_value=0, max_value=25))
def test_count_matches_list_length(n):
    with fresh_repo() as repo:
        for i in range(n):
            repo.create(task_name=f"t{i}", consumer="c", payload={})
        assert repo.count() == n
        assert len(repo.list()) == n

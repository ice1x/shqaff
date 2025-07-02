from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, func

from sqlalchemy.orm import declarative_base


Base = declarative_base()


class TaskQueue(Base):
    __tablename__ = "task_queue"

    id = Column(Integer, primary_key=True)
    task_name = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    consumer = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    retries = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_attempt_at = Column(DateTime)

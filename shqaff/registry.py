from typing import Dict, Type
from .consumer import Consumer


consumer_registry: Dict[str, Type[Consumer]] = {}


def register_consumer(consumer_cls: Type[Consumer]) -> None:
    consumer_registry[consumer_cls().name] = consumer_cls

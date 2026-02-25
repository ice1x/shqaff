from typing import Dict, Type
from shqaff.consumer import Consumer


consumer_registry: Dict[str, Type[Consumer]] = {}


def register_consumer(consumer_cls: Type[Consumer]) -> None:
    consumer_registry[consumer_cls().name] = consumer_cls

import json
from typing import Any


class KafkaMessage:
    def __init__(self, topic: str, value: Any):
        self._topic = topic
        self._value = value

    def topic(self) -> str:
        return self._topic

    def value(self) -> Any:
        return self._value

    def json(self) -> str:
        return json.dumps(self.value())

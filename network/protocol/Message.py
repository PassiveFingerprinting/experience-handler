from dataclasses import dataclass
from enum import IntEnum


class MessageType(IntEnum):
    CMD = 0
    ERROR = 1


@dataclass
class Message:
    type: int
    msg_id: int
    payload: dict
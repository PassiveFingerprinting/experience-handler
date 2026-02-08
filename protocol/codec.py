import json
from .Message import Message

def encode(msg: Message) -> bytes:
    return json.dumps(msg.__dict__).encode()

def decode(data: bytes) -> Message:
    obj = json.loads(data.decode())
    return Message(**obj)
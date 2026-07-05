import json
from .Message import Message

def encode(msg: Message) -> bytes:
    """Function used to encode a message.

    Args:
        msg (Message): message to encode.

    Returns:
        none

    Raises:
        none
    """
    return json.dumps(msg.__dict__).encode()

def decode(data: bytes) -> Message:
    """Function used to decode data into a message.

    Args:
        data (bytes): data to decode.

    Returns:
        Message: returns a Message object.

    Raises:
        none
    """
    obj = json.loads(data.decode())
    return Message(**obj)
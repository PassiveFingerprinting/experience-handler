from .framing import frame, unframe
from .codec import encode, decode
from .Message import Message

class Protocol:

    def __init__(self):
        """Protocol constructor.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        self.buffer = bytearray()

    def encode_message(self, msg):
        """Function used to frame and encode a message.

        Args:
            msg (str): message to encode.

        Returns:
            bytes: encoded and framed message.

        Raises:
            none
        """
        return frame(encode(msg))

    def feed_data(self, data: bytes) -> list[Message]:
        """Function used to unframe and decode data into readable Message objects.

        Args:
            data (str): message to encode.

        Returns:
            list[Message]: unframed and decoded list of Message.

        Raises:
            none
        """
        self.buffer.extend(data)
        return [decode(m) for m in unframe(self.buffer)]
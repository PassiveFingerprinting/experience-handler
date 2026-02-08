from .framing import frame, unframe
from .codec import encode, decode

class Protocol:
    def __init__(self):
        self.buffer = bytearray()

    def encode_message(self, msg):
        return frame(encode(msg))

    def feed_data(self, data: bytes):
        self.buffer.extend(data)
        return [decode(m) for m in unframe(self.buffer)]
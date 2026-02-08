import struct

def frame(data: bytes) -> bytes:
    return struct.pack("!I", len(data)) + data

def unframe(buffer: bytearray) -> list[bytes]:
    messages = []
    while len(buffer) >= 4:
        size = struct.unpack("!I", buffer[:4])[0]
        if len(buffer) < 4 + size:
            break
        messages.append(bytes(buffer[4:4+size]))
        del buffer[:4+size]
    return messages
import struct

def frame(data: bytes) -> bytes:
    """Function used to frame data.

    Args:
        data (bytes): data to frame.

    Returns:
        bytes: framed data.

    Raises:
        none
    """
    return struct.pack("!I", len(data)) + data

def unframe(buffer: bytearray) -> list[bytes]:
    """Function used to unframe data.

    Args:
        data (bytearray): data to frame.

    Returns:
        list[bytes]: unframed data.

    Raises:
        none
    """
    messages = []
    while len(buffer) >= 4:
        size = struct.unpack("!I", buffer[:4])[0]
        if len(buffer) < 4 + size:
            break
        messages.append(bytes(buffer[4:4+size]))
        del buffer[:4+size]
    return messages
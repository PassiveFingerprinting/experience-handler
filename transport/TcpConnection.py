class TcpConnection:

    BUFFER_SIZE = 1042

    def __init__(self, sock):
        self.sock = sock

    def send(self, data: bytes):
        self.sock.sendall(data)

    def recv(self) -> bytes:
        return self.sock.recv(TcpConnection.BUFFER_SIZE)

    def close(self):
        self.sock.close()
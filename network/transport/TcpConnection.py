class TcpConnection:

    BUFFER_SIZE = 1042

    def __init__(self, sock):
        """TcpConnection constructor.

        Args:
            sock (socket): connection socket object.

        Returns:
            none

        Raises:
            none
        """
        self.sock = sock

    def send(self, data: bytes):
        """Function used to send data via socket.

        Args:
            data (bytes): data to send.

        Returns:
            none

        Raises:
            none
        """
        self.sock.sendall(data)

    def recv(self) -> bytes:
        """Function used to receive data.

        Args:
            none

        Returns:
            bytes: returns data received.

        Raises:
            none
        """
        return self.sock.recv(TcpConnection.BUFFER_SIZE)

    def close(self):
        """Close function.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        self.sock.close()
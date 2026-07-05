import logging
import socket
from .TcpConnection import TcpConnection


logger = logging.getLogger(__name__)


class TcpServer:

    def __init__(self, host, port):
        """TcpServer constructor.

        Args:
            host (str): host to bind to.
            port (int): port to bind to.

        Returns:
            none

        Raises:
            none
        """
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.5)
        self.sock.bind((host, port))
        self.sock.listen(1)
        self.run = True

    def accept(self):
        """Function used to accept new connections.

        Args:
            host (str): host to bind to.
            port (int): port to bind to.

        Returns:
            TcpConnection | None: Returns a new TcpConnection when successfull None otherwise.

        Raises:
            none
        """
        logger.info(f"Listening on {self.host}:{self.port}")
        conn = None
        while conn is None and self.run:
            try:
                conn, addr = self.sock.accept()
            except (TimeoutError, OSError):
                continue
        if conn is None:
            return None
        conn.settimeout(0.5)
        logger.debug(f"New connection from: {addr}")
        return TcpConnection(conn)

    def close(self):
        """Close function.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        self.run = False
        self.sock.close()
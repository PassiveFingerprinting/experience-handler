import logging
import socket
from .TcpConnection import TcpConnection

logger = logging.getLogger(__name__)


class TcpClient:

    def __init__(self, host, port):
        """TcpClient constructor.

        Args:
            host (str): target host.
            port (int): target port.

        Returns:
            none

        Raises:
            none
        """
        self.host = host
        self.port = port
        self.sock = socket.socket()

    def connect(self):
        """Function used to connect to server.

        Args:
            none

        Returns:
            TcpConnection | None: Returns a new TcpConnection when connection is successfull, None otherwise.

        Raises:
            none
        """
        self.sock.connect((self.host, self.port))
        return TcpConnection(self.sock)

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
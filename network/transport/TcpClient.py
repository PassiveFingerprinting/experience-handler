import logging
import socket
from .TcpConnection import TcpConnection

logger = logging.getLogger(__name__)


class TcpClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket()

    def connect(self):
        self.sock.connect((self.host, self.port))
        return TcpConnection(self.sock)

    def close(self):
        self.sock.close()
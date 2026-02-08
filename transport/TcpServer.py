import logging
import socket
from .TcpConnection import TcpConnection


logger = logging.getLogger(__name__)


class TcpServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.5)
        self.sock.bind((host, port))
        self.sock.listen(1)
        self.run = True

    def accept(self):
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
        logger.info(f"New connection from: {addr}")
        return TcpConnection(conn)

    def close(self):
        self.run = False
        self.sock.close()
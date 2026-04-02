import logging
import threading

from network.transport.TcpServer import TcpServer
from network.protocol.Protocol import Protocol
from network.protocol import Message, MessageType


logger = logging.getLogger(__name__)


class Server:

    def __init__(self, host, port):
        self.server = TcpServer(host, port)
        self.protocol = Protocol()
        self.run = False
        self.msg_id = 0
        self.conn = None
        self.command_handler = None
        self.on_connection = None
        self.loop_thread = None

    def _loop(self):
        self.run = True
        self.conn = self.server.accept()
        if self.conn is None:
            return
        if self.on_connection is not None:
            self.on_connection(self)
        while self.run:
            try:
                data = self.conn.recv()
            except TimeoutError:
                break
            if not data:
                break
            for msg in self.protocol.feed_data(data):
                if msg.type == MessageType.CMD:
                    self.command_handler(msg.payload)
                if msg.type == MessageType.ERROR:
                    logger.error(f"Error: {msg.msg_id}")

    def start(self, command_handler, on_connection=None):
        if not callable(command_handler):
            raise TypeError("Command handler must be callable")
        if on_connection is not None and not callable(on_connection):
            raise TypeError("on_connection handler must be callable")
        self.command_handler = command_handler
        self.on_connection = on_connection
        self.loop_thread = threading.Thread(target=self._loop)
        self.loop_thread.start()

    def stop(self):
        logger.info(f'Stopping server')
        self.run = False
        self.server.close()
        if self.conn is not None:
            self.conn.close()
        self.loop_thread.join()

    def send_message(self, msg: dict):
        if self.conn is None:
            self.stop()
            raise ConnectionError("Server not connected to agent")
        msg = Message(MessageType.CMD, self.msg_id, msg)
        self.msg_id += 1
        self.conn.send(self.protocol.encode_message(msg))


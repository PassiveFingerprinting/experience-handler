import logging

from transport.TcpClient import TcpClient
from protocol.Protocol import Protocol
from protocol.Message import Message, MessageType


logger = logging.getLogger(__name__)


class Client:

    def __init__(self, host, port):
        self.run = False
        self.conn = None
        self.protocol = Protocol()
        self.client = TcpClient(host, port)
        self.msg_id = 0

    def start(self, command_handler):
        self.run = True
        self.conn = self.client.connect()
        while self.run:
            data = self.conn.recv()
            if not data:
                break
            for msg in self.protocol.feed_data(data):
                logger.info(msg)
                if msg.type == MessageType.CMD:
                    command_handler(msg.payload)
                if msg.type == MessageType.ERROR:
                    logger.error(f"Error: {msg.msg_id}")

    def stop(self):
        self.run = False
        if self.conn is not None:
            self.conn.close()

    def send_message(self, msg: dict):
        if self.conn is None:
            raise ConnectionError("Server not connected to agent")
        msg = Message(MessageType.CMD, self.msg_id, msg)
        self.msg_id += 1
        self.conn.send(self.protocol.encode_message(msg))
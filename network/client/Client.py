import logging

from network.transport.TcpClient import TcpClient
from network.protocol.Protocol import Protocol
from network.protocol import Message, MessageType


logger = logging.getLogger(__name__)


class Client:

    def __init__(self, host, port):
        """Client constructor.

        Args:
            host (str): server host.
            port (int): server port.

        Returns:
            none

        Raises:
            none
        """
        self.run = False
        self.conn = None
        self.protocol = Protocol()
        self.client = TcpClient(host, port)
        self.msg_id = 0

    def start(self, command_handler):
        """Function used to start the client.

        Args:
            command_handler (function): function called when a new command is received.

        Returns:
            none

        Raises:
            none
        """
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
        """Function used to stop the client.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        self.run = False
        if self.conn is not None:
            self.conn.close()

    def send_message(self, msg: dict):
        """Function used to send a message.

        Args:
            msg (dict): message dict to send.

        Returns:
            none

        Raises:
            ConnectionError: when server is not connected to client.
        """
        if self.conn is None:
            raise ConnectionError("Server not connected to client")
        msg = Message(MessageType.CMD, self.msg_id, msg)
        self.msg_id += 1
        self.conn.send(self.protocol.encode_message(msg))
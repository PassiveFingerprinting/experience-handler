import logging
import threading

from network.transport import TcpServer
from network.protocol import Protocol, Message, MessageType


logger = logging.getLogger(__name__)

class Server:

    def __init__(self, host, port):
        """Server constructor.

        Args:
            host (str): server host.
            port (int): server port.

        Returns:
            none

        Raises:
            none
        """
        self.server = TcpServer(host, port)
        self.protocol = Protocol()
        self.run = False
        self.conn = None
        self.command_handler = None
        self.on_connection = None
        self.loop_thread = None

    def _loop(self):
        """Server loop function.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        self.run = True
        while self.run:
            self.on_connection.clear()
            conn = self.server.accept()
            if conn is None:
                continue
            self.conn = conn
            if self.on_connection is not None:
                self.on_connection.set()
                while self.run:
                    try:
                        data = conn.recv()
                        if not data:
                            logger.info("Client disconnected")
                            break
                        for msg in self.protocol.feed_data(data):
                            if msg.type == MessageType.CMD:
                                self.command_handler(msg.payload)
                    except (TimeoutError, OSError) as err:
                        pass

    def start(self, command_handler, on_connection=None):
        """Function used to start the server.

        Args:
            command_handler (function): command handler function called when a new message is received. 
            on_connection (threading.Event): threading Event called when the server get a new connection.

        Returns:
            none

        Raises:
            TypeError: when command_handler or on_connection type checks failes.
        """
        if not callable(command_handler):
            raise TypeError("Command handler must be callable")
        if on_connection is not None and not isinstance(on_connection, threading.Event):
            raise TypeError("on_connection handler must be callable")
        self.command_handler = command_handler
        self.on_connection = on_connection
        self.loop_thread = threading.Thread(target=self._loop)
        self.loop_thread.start()

    def stop(self):
        """Function used to stop the server.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        logger.info("Stopping server")
        self.run = False
        self.server.close()
        if self.conn is not None:
            self.conn.close()
        self.loop_thread.join()

    def send_message(self, msg: dict):
        """Function used to send a message.

        Args:
            msg (dict): message dict to send.

        Returns:
            none

        Raises:
            ConnectionError: if the server is not connected.
        """
        if self.conn is None:
            self.stop()
            raise ConnectionError("Server not connected to client")
        msg = Message(MessageType.CMD, msg)
        self.conn.send(self.protocol.encode_message(msg))


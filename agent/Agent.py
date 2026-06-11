import logging
import platform
from network.client.Client import Client
from cmds import CommandType


logger = logging.getLogger(__name__)


class Agent:

    def __init__(self, host, port):
        """Agent constructor.

        Args:
            host (str): server host.
            port (str): server port.

        Returns:
            none

        Raises:
            none
        """
        self.client = Client(host, int(port))
        self.cmds = {
            str(CommandType.DONE): self.cmd_done,
            str(CommandType.SYSTEM_INFO): self.cmd_info,
        }

    ### Start of command definition block ###

    def cmd_done(self, _):
        """Command function called done, used to signal the server that it's work is finished.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        self.client.send_message({
            "cmd": str(CommandType.DONE),
            "result": {}
        })

    def cmd_info(self, _):
        """Command function called info, used to send to server the target host system informations.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        logger.info(f'cmd info received')
        system_info = platform.uname()
        self.client.send_message({
            "cmd": str(CommandType.SYSTEM_INFO),
            "result": {
                "name": system_info.system,
                "release": system_info.release,
                "version": system_info.version,
                "machine": system_info.machine
            }
        })

    ### End of command definition block ###

    def handle_cmds(self, cmd):
        """Function used to call the appropriate command function.

        Args:
            cmd (dict): command received from the server to be executed on the target host.

        Returns:
            none

        Raises:
            none
        """
        if 'cmd' in cmd:
            if cmd["cmd"] in self.cmds:
                self.cmds[cmd["cmd"]](cmd["data"])
            else:
                logger.info(f'CommandType {cmd["cmd"]} not recognized')

    def start(self):
        """Function used to start the agent on the target host.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        logger.info(f'Agent starting')
        self.client.start(self.handle_cmds)

    def stop(self):
        """Function used to stop the agent on the target host.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        logger.info(f'Agent stopping')
        self.client.stop()